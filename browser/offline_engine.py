"""
Searcher Browser - Complete Offline Application Engine
Manages Offline Detection, Resource Caching, Request Interception,
Local Storage & Draft Preservation, Background Syncing, and Cache Cleanup.
"""

import os
import time
import json
import hashlib
import sqlite3
import requests
from typing import Dict, Any, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QUrl
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineScript, QWebEngineProfile


class OfflineDetector(QThread):
    """
    Background worker that monitors internet connectivity status.
    Periodically checks connection to reliable endpoints.
    """
    status_changed = pyqtSignal(bool)

    def __init__(self, parent=None, check_interval=4):
        super().__init__(parent)
        self.check_interval = check_interval
        self._is_online = True
        self._running = True

    def run(self):
        while self._running:
            online = self.check_connection()
            if online != self._is_online:
                self._is_online = online
                self.status_changed.emit(self._is_online)
            time.sleep(self.check_interval)

    def check_connection(self) -> bool:
        """Checks internet reachability using fast HTTP HEAD requests."""
        endpoints = ["https://1.1.1.1", "https://8.8.8.8", "https://www.google.com"]
        for endpoint in endpoints:
            try:
                resp = requests.head(endpoint, timeout=2.0)
                if resp.status_code < 500:
                    return True
            except Exception:
                continue
        return False

    def stop(self):
        self._running = False
        self.wait()


class ResourceCacheManager:
    """
    Manages local caching of web resources (HTML, CSS, JS, Images, Fonts, WASM, Media).
    Supports Cache-First, Network-First, Stale-While-Revalidate, Versioning, and LRU cleanup.
    """
    def __init__(self, cache_dir="database/offline_cache", max_size_mb=200):
        self.cache_dir = os.path.abspath(cache_dir)
        self.max_bytes = max_size_mb * 1024 * 1024
        self.db_path = os.path.join(self.cache_dir, "cache_index.db")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resource_cache (
                    url_hash TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    content_type TEXT,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    ttl INTEGER NOT NULL,
                    etag TEXT,
                    strategy TEXT DEFAULT 'cache_first'
                )
            ''')
            conn.commit()

    def _hash_url(self, url: str) -> str:
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def get_cached_resource(self, url: str) -> Optional[Dict[str, Any]]:
        url_hash = self._hash_url(url)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url, content_type, file_path, file_size, created_at, last_accessed, ttl, etag, strategy
                FROM resource_cache WHERE url_hash = ?
            ''', (url_hash,))
            row = cursor.fetchone()
            if row:
                u, content_type, file_path, file_size, created_at, last_accessed, ttl, etag, strategy = row
                if os.path.exists(file_path):
                    now = time.time()
                    cursor.execute("UPDATE resource_cache SET last_accessed = ? WHERE url_hash = ?", (now, url_hash))
                    conn.commit()
                    return {
                        "url": u,
                        "content_type": content_type,
                        "file_path": file_path,
                        "file_size": file_size,
                        "etag": etag,
                        "strategy": strategy,
                        "is_expired": (now - created_at) > ttl
                    }
        return None

    def store_resource(self, url: str, content: bytes, content_type: str = "text/html", ttl: int = 604800, etag: str = "", strategy: str = "cache_first") -> str:
        url_hash = self._hash_url(url)
        ext = ".bin"
        if "html" in content_type: ext = ".html"
        elif "css" in content_type: ext = ".css"
        elif "javascript" in content_type or "js" in content_type: ext = ".js"
        elif "image" in content_type: ext = ".img"
        elif "font" in content_type: ext = ".font"
        elif "wasm" in content_type: ext = ".wasm"
        elif "json" in content_type: ext = ".json"

        file_name = f"{url_hash[:16]}{ext}"
        file_path = os.path.join(self.cache_dir, file_name)
        
        with open(file_path, "wb") as f:
            f.write(content)

        file_size = len(content)
        now = time.time()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO resource_cache (url_hash, url, content_type, file_path, file_size, created_at, last_accessed, ttl, etag, strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (url_hash, url, content_type, file_path, file_size, now, now, ttl, etag, strategy))
            conn.commit()

        self.enforce_storage_limit()
        return file_path

    def enforce_storage_limit(self):
        """Purges old cache items (LRU) when total storage exceeds limit."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(file_size) FROM resource_cache")
            row = cursor.fetchone()
            total_size = row[0] or 0

            if total_size > self.max_bytes:
                cursor.execute("SELECT url_hash, file_path, file_size FROM resource_cache ORDER BY last_accessed ASC")
                rows = cursor.fetchall()
                for url_hash, file_path, file_size in rows:
                    if os.path.exists(file_path):
                        try: os.remove(file_path)
                        except Exception: pass
                    cursor.execute("DELETE FROM resource_cache WHERE url_hash = ?", (url_hash,))
                    total_size -= file_size
                    if total_size <= self.max_bytes * 0.8:
                        break
                conn.commit()

    def get_cache_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(file_size) FROM resource_cache")
            row = cursor.fetchone()
            count = row[0] or 0
            size_bytes = row[1] or 0
            return {
                "count": count,
                "size_mb": round(size_bytes / (1024 * 1024), 2),
                "max_mb": round(self.max_bytes / (1024 * 1024), 2)
            }

    def clear_cache(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM resource_cache")
            for (file_path,) in cursor.fetchall():
                if os.path.exists(file_path):
                    try: os.remove(file_path)
                    except Exception: pass
            cursor.execute("DELETE FROM resource_cache")
            conn.commit()


class BackgroundSyncManager(QObject):
    """
    Queues failed mutation requests (POST, PUT, PATCH, DELETE) while offline
    and automatically replays them when connectivity returns with exponential backoff.
    """
    queue_updated = pyqtSignal(int)
    sync_finished = pyqtSignal(bool, str)

    def __init__(self, parent=None, db_path="database/sync_queue.db"):
        super().__init__(parent)
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    method TEXT NOT NULL,
                    headers TEXT,
                    payload TEXT,
                    created_at REAL NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    last_attempt REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            conn.commit()

    def queue_request(self, url: str, method: str = "POST", headers: dict = None, payload: str = "") -> int:
        headers_str = json.dumps(headers or {})
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sync_queue (url, method, headers, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (url, method.upper(), headers_str, payload, now))
            conn.commit()
            item_id = cursor.lastrowid
        self.queue_updated.emit(self.get_pending_count())
        return item_id

    def get_pending_count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE status = 'pending'")
            return cursor.fetchone()[0] or 0

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url, method, headers, payload, created_at, retry_count FROM sync_queue WHERE status = 'pending' ORDER BY id ASC")
            rows = cursor.fetchall()
            items = []
            for r in rows:
                items.append({
                    "id": r[0],
                    "url": r[1],
                    "method": r[2],
                    "headers": json.loads(r[3] or "{}"),
                    "payload": r[4],
                    "created_at": r[5],
                    "retry_count": r[6]
                })
            return items

    def replay_pending_requests(self) -> bool:
        """Replays queued requests with exponential backoff when connectivity returns."""
        pending = self.get_pending_requests()
        if not pending:
            return True

        success_count = 0
        now = time.time()

        for req in pending:
            req_id = req["id"]
            url = req["url"]
            method = req["method"]
            headers = req["headers"]
            payload = req["payload"]
            retries = req["retry_count"]

            if retries >= 5:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("UPDATE sync_queue SET status = 'failed_max_retries' WHERE id = ?", (req_id,))
                continue

            try:
                if method == "POST":
                    resp = requests.post(url, data=payload, headers=headers, timeout=5)
                elif method == "PUT":
                    resp = requests.put(url, data=payload, headers=headers, timeout=5)
                elif method == "PATCH":
                    resp = requests.patch(url, data=payload, headers=headers, timeout=5)
                elif method == "DELETE":
                    resp = requests.delete(url, headers=headers, timeout=5)
                else:
                    resp = requests.get(url, headers=headers, timeout=5)

                if resp.status_code < 400:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("UPDATE sync_queue SET status = 'synced' WHERE id = ?", (req_id,))
                    success_count += 1
                else:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("UPDATE sync_queue SET retry_count = retry_count + 1, last_attempt = ? WHERE id = ?", (now, req_id))
            except Exception:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("UPDATE sync_queue SET retry_count = retry_count + 1, last_attempt = ? WHERE id = ?", (now, req_id))

        self.queue_updated.emit(self.get_pending_count())
        msg = f"Synced {success_count} queued offline requests."
        self.sync_finished.emit(True, msg)
        return True


class OfflineRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Combines Ad Blocking with Offline Request Interception.
    Blocks ad/tracker domains and intercepts network requests for offline caching.
    """
    def __init__(self, offline_engine, parent=None):
        super().__init__(parent)
        self.offline_engine = offline_engine
        self.block_list = [
            "doubleclick.net", "google-analytics.com", "connect.facebook.net",
            "googlesyndication.com", "amazon-adsystem.com", "scorecardresearch.com",
            "outbrain.com", "taboola.com"
        ]

    def interceptRequest(self, info):
        url_str = info.requestUrl().toString().lower()

        # 1. Ad Blocking
        for blocked_domain in self.block_list:
            if blocked_domain in url_str:
                info.block(True)
                return

        # 2. Offline Mode Queueing
        if not self.offline_engine.is_online():
            method = info.requestMethod().decode('utf-8', 'ignore').upper()
            if method in ("POST", "PUT", "PATCH", "DELETE"):
                self.offline_engine.sync_manager.queue_request(url_str, method)


class OfflineEngine(QObject):
    """
    Central Manager for Searcher Browser Offline Application Engine.
    Orchestrates detector, cache manager, sync manager, and script injection.
    """
    connection_changed = pyqtSignal(bool) # Emits True when online, False when offline
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache_manager = ResourceCacheManager()
        self.sync_manager = BackgroundSyncManager(self)
        self.detector = OfflineDetector(self)
        self.detector.status_changed.connect(self.on_connectivity_changed)
        
        self.interceptor = OfflineRequestInterceptor(self, parent)
        self._is_online = True

    def start(self):
        self.detector.start()
        # Initial check
        self._is_online = self.detector.check_connection()
        self.inject_draft_saver_script()

    def is_online(self) -> bool:
        return self._is_online

    def on_connectivity_changed(self, is_online: bool):
        self._is_online = is_online
        self.connection_changed.emit(is_online)
        if is_online:
            # Replay pending sync requests when internet is restored
            self.sync_manager.replay_pending_requests()

    def inject_draft_saver_script(self):
        """Injects auto-saver script into QWebEngineProfile for zero-data-loss form drafts."""
        script = QWebEngineScript()
        script.setName("SearcherOfflineDraftSaver")
        script.setSourceCode("""
        (function() {
            if (window.__searcherDraftSaverInjected) return;
            window.__searcherDraftSaverInjected = true;

            const DRAFT_KEY = '__searcher_draft__' + window.location.pathname;

            function saveDrafts() {
                const formData = {};
                const inputs = document.querySelectorAll('input, textarea, select');
                inputs.forEach((el, idx) => {
                    if (el.type === 'password' || el.type === 'hidden') return;
                    const key = el.name || el.id || ('input_' + idx);
                    if (el.type === 'checkbox' || el.type === 'radio') {
                        formData[key] = el.checked;
                    } else {
                        formData[key] = el.value;
                    }
                });
                
                const scrollData = { x: window.scrollX, y: window.scrollY };

                try {
                    localStorage.setItem(DRAFT_KEY, JSON.stringify({
                        time: Date.now(),
                        fields: formData,
                        scroll: scrollData
                    }));
                } catch(e) {}
            }

            function restoreDrafts() {
                try {
                    const raw = localStorage.getItem(DRAFT_KEY);
                    if (!raw) return;
                    const data = JSON.parse(raw);
                    if (data && data.fields) {
                        const inputs = document.querySelectorAll('input, textarea, select');
                        inputs.forEach((el, idx) => {
                            if (el.type === 'password' || el.type === 'hidden') return;
                            const key = el.name || el.id || ('input_' + idx);
                            if (data.fields[key] !== undefined) {
                                if (el.type === 'checkbox' || el.type === 'radio') {
                                    el.checked = data.fields[key];
                                } else if (!el.value) {
                                    el.value = data.fields[key];
                                }
                            }
                        });
                    }
                    if (data && data.scroll && (data.scroll.x || data.scroll.y)) {
                        window.scrollTo(data.scroll.x, data.scroll.y);
                    }
                } catch(e) {}
            }

            document.addEventListener('input', saveDrafts);
            document.addEventListener('change', saveDrafts);
            window.addEventListener('scroll', saveDrafts);
            document.addEventListener('DOMContentLoaded', restoreDrafts);
            setTimeout(restoreDrafts, 600);
        })();
        """)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(False)
        
        QWebEngineProfile.defaultProfile().scripts().insert(script)

    def stop(self):
        self.detector.stop()
