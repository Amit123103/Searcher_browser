"""
Searcher Browser - Complete Offline Application Engine
======================================================
Manages Offline Detection, Resource Caching, Request Interception,
Local Storage & Draft Preservation, Background Syncing, and Cache Cleanup.

Architecture (Chromium-inspired):
  OfflineEngine              — central orchestrator
  OfflineDetector            — polls internet every 4s (QThread)
  ResourceCacheManager       — SQLite-indexed disk cache (LRU, 200 MB)
  CachePopulatorThread       — downloads & caches sub-resources after page load
  BackgroundSyncManager      — queues failed mutations (POST/PUT/PATCH/DELETE)
  SyncWorkerThread           — replays sync queue off the UI thread
  OfflineRequestInterceptor  — intercepts all requests; redirects to cache when offline

Caching Strategies:
  cache_first            — static assets (CSS, JS, fonts, images, WASM)
  network_first          — API endpoints (JSON, XHR)
  stale_while_revalidate — HTML pages (serve stale immediately, update in background)
"""

import os
import re
import time
import json
import hashlib
import sqlite3
import requests
from typing import Dict, Any, List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QUrl
from PyQt6.QtWebEngineCore import (
    QWebEngineUrlRequestInterceptor, QWebEngineScript, QWebEngineProfile
)


# ---------------------------------------------------------------------------
# Connectivity Detector
# ---------------------------------------------------------------------------

class OfflineDetector(QThread):
    """
    Background worker that monitors internet connectivity.
    Emits status_changed(bool) whenever online/offline status flips.
    Checks multiple reliable endpoints with short timeouts for fast detection.
    """
    status_changed = pyqtSignal(bool)

    def __init__(self, parent=None, check_interval: int = 5):
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
            self.msleep(self.check_interval * 1000)

    def check_connection(self) -> bool:
        """
        Tries lightweight HEAD requests against Cloudflare DNS and Google.
        Returns True as soon as any endpoint responds with < 500.
        Fails fast: 2-second timeout per attempt, stops at first success.
        """
        endpoints = [
            "https://1.1.1.1",
            "https://8.8.8.8",
            "https://www.google.com",
        ]
        for endpoint in endpoints:
            try:
                resp = requests.head(endpoint, timeout=2.0, allow_redirects=True)
                if resp.status_code < 500:
                    return True
            except Exception:
                continue
        return False

    def stop(self):
        self._running = False
        self.quit()
        self.wait(3000)


# ---------------------------------------------------------------------------
# Resource Cache Manager
# ---------------------------------------------------------------------------

class ResourceCacheManager:
    """
    Manages local caching of web resources.

    Storage layout:
        database/offline_cache/
            cache_index.db      — SQLite index of all cached items
            <hash16>.<ext>      — individual cached resource files

    Supports:
        - Cache-First  (static: CSS, JS, fonts, WASM, images)
        - Network-First (API JSON)
        - Stale-While-Revalidate (HTML)
        - LRU eviction when total size exceeds max_size_mb
        - ETag-based conditional revalidation
    """

    STRATEGY_BY_CONTENT_TYPE = {
        "text/css":              "cache_first",
        "application/javascript":"cache_first",
        "text/javascript":       "cache_first",
        "font":                  "cache_first",
        "image":                 "cache_first",
        "application/wasm":      "cache_first",
        "text/html":             "stale_while_revalidate",
        "application/json":      "network_first",
        "text/plain":            "stale_while_revalidate",
    }

    # Default TTLs (seconds)
    TTL_STATIC = 7 * 24 * 3600    # 7 days for CSS/JS/fonts
    TTL_HTML   = 1 * 24 * 3600    # 1 day for HTML
    TTL_API    = 5 * 60           # 5 minutes for API responses

    def __init__(self, cache_dir: str = "database/offline_cache", max_size_mb: int = 200):
        self.cache_dir = os.path.abspath(cache_dir)
        self.max_bytes = max_size_mb * 1024 * 1024
        self.db_path = os.path.join(self.cache_dir, "cache_index.db")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS resource_cache (
                    url_hash     TEXT PRIMARY KEY,
                    url          TEXT NOT NULL,
                    content_type TEXT,
                    file_path    TEXT NOT NULL,
                    file_size    INTEGER NOT NULL DEFAULT 0,
                    created_at   REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    ttl          INTEGER NOT NULL DEFAULT 86400,
                    etag         TEXT DEFAULT '',
                    strategy     TEXT DEFAULT 'cache_first'
                )
            """)
            conn.commit()

    # ------------------------------------------------------------------
    # Hash helpers
    # ------------------------------------------------------------------

    def _hash_url(self, url: str) -> str:
        """Full SHA-256 hex digest of the URL string."""
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def _ext_for_type(self, content_type: str) -> str:
        ct = content_type.lower()
        if "html"       in ct: return ".html"
        if "css"        in ct: return ".css"
        if "javascript" in ct: return ".js"
        if "json"       in ct: return ".json"
        if "wasm"       in ct: return ".wasm"
        if "font"       in ct: return ".font"
        if "svg"        in ct: return ".svg"
        if "image"      in ct: return ".img"
        return ".bin"

    def _strategy_for_type(self, content_type: str) -> str:
        ct = content_type.lower()
        for key, strat in self.STRATEGY_BY_CONTENT_TYPE.items():
            if key in ct:
                return strat
        return "cache_first"

    def _ttl_for_strategy(self, strategy: str) -> int:
        if strategy == "network_first":     return self.TTL_API
        if strategy == "stale_while_revalidate": return self.TTL_HTML
        return self.TTL_STATIC

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_cached_resource(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Returns cached resource metadata dict or None.
        Updates last_accessed timestamp on hit (LRU touch).
        Includes is_expired flag so callers can decide to revalidate.
        """
        url_hash = self._hash_url(url)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT url, content_type, file_path, file_size,
                       created_at, last_accessed, ttl, etag, strategy
                FROM resource_cache WHERE url_hash = ?
            """, (url_hash,)).fetchone()

            if row:
                u, ct, fp, fs, created, accessed, ttl, etag, strategy = row
                if os.path.exists(fp):
                    now = time.time()
                    conn.execute(
                        "UPDATE resource_cache SET last_accessed = ? WHERE url_hash = ?",
                        (now, url_hash)
                    )
                    conn.commit()
                    return {
                        "url":          u,
                        "content_type": ct,
                        "file_path":    fp,
                        "file_size":    fs,
                        "etag":         etag,
                        "strategy":     strategy,
                        "is_expired":   (now - created) > ttl,
                    }
        return None

    def get_cached_by_hash_prefix(self, hash_prefix: str) -> Optional[Dict[str, Any]]:
        """
        Look up a cache entry by the first 16 chars of the URL hash.
        Used by OfflineCacheSchemeHandler which receives the hash in the URL.
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT url, content_type, file_path, file_size, etag, strategy
                FROM resource_cache
                WHERE url_hash LIKE ?
                LIMIT 1
            """, (hash_prefix + "%",)).fetchone()
            if row:
                u, ct, fp, fs, etag, strategy = row
                if os.path.exists(fp):
                    return {
                        "url":          u,
                        "content_type": ct,
                        "file_path":    fp,
                        "file_size":    fs,
                        "etag":         etag,
                        "strategy":     strategy,
                    }
        return None

    def store_resource(
        self,
        url: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        etag: str = "",
        strategy: str = "",
    ) -> str:
        """
        Writes content to disk and indexes it in SQLite.
        Returns the file path.
        Auto-selects strategy and TTL based on content_type if not given.
        """
        if not content:
            return ""

        url_hash  = self._hash_url(url)
        ext       = self._ext_for_type(content_type)
        strat     = strategy or self._strategy_for_type(content_type)
        ttl       = self._ttl_for_strategy(strat)
        file_name = f"{url_hash[:16]}{ext}"
        file_path = os.path.join(self.cache_dir, file_name)

        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except OSError as e:
            print(f"[Cache] Failed to write {file_path}: {e}")
            return ""

        file_size = len(content)
        now = time.time()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO resource_cache
                    (url_hash, url, content_type, file_path, file_size,
                     created_at, last_accessed, ttl, etag, strategy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (url_hash, url, content_type, file_path, file_size,
                  now, now, ttl, etag, strat))
            conn.commit()

        self.enforce_storage_limit()
        return file_path

    def enforce_storage_limit(self):
        """LRU eviction — removes oldest-accessed items until under 80% of max."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT SUM(file_size) FROM resource_cache").fetchone()
            total = row[0] or 0
            if total <= self.max_bytes:
                return

            rows = conn.execute(
                "SELECT url_hash, file_path, file_size FROM resource_cache ORDER BY last_accessed ASC"
            ).fetchall()

            target = self.max_bytes * 0.8
            for url_hash, fp, fs in rows:
                if os.path.exists(fp):
                    try: os.remove(fp)
                    except Exception: pass
                conn.execute("DELETE FROM resource_cache WHERE url_hash = ?", (url_hash,))
                total -= fs
                if total <= target:
                    break
            conn.commit()

    def get_cache_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*), SUM(file_size) FROM resource_cache").fetchone()
            count     = row[0] or 0
            size_bytes = row[1] or 0
            return {
                "count":  count,
                "size_mb": round(size_bytes / (1024 * 1024), 2),
                "max_mb":  round(self.max_bytes / (1024 * 1024), 2),
            }

    def clear_cache(self):
        with sqlite3.connect(self.db_path) as conn:
            for (fp,) in conn.execute("SELECT file_path FROM resource_cache").fetchall():
                if os.path.exists(fp):
                    try: os.remove(fp)
                    except Exception: pass
            conn.execute("DELETE FROM resource_cache")
            conn.commit()


# ---------------------------------------------------------------------------
# Background Cache Populator Thread
# ---------------------------------------------------------------------------

class CachePopulatorThread(QThread):
    """
    Downloads and caches a list of URLs in the background after a page loads.
    This is how we pre-populate the cache for offline use without blocking the UI.

    Strategy selection:
      - image/*, font/*, text/css, application/javascript → cache_first
      - text/html                                         → stale_while_revalidate
      - application/json                                  → network_first

    Skips:
      - blob: and data: URLs (can't cache)
      - Already-fresh cache entries (strategy = cache_first, not expired)
    """
    progress        = pyqtSignal(int, int)   # (cached_so_far, total)
    resource_cached = pyqtSignal(str)        # emits URL when one item is cached
    finished_caching = pyqtSignal(int)       # emits total count cached this run

    # Only download these content types — skip video/audio streams
    CACHEABLE_TYPES = {
        "text/html", "text/css", "text/javascript",
        "application/javascript", "application/x-javascript",
        "application/json", "application/wasm",
        "image/", "font/", "application/font",
    }

    def __init__(self, urls: List[str], cache_manager: ResourceCacheManager, parent=None):
        super().__init__(parent)
        self.urls = urls
        self.cache_manager = cache_manager
        self._running = True

    def run(self):
        cached_count = 0
        total = len(self.urls)

        for i, url in enumerate(self.urls):
            if not self._running:
                break

            # Skip non-HTTP(S) URLs
            if not url.startswith(("http://", "https://")):
                self.progress.emit(i + 1, total)
                continue

            # Check if already freshly cached
            existing = self.cache_manager.get_cached_resource(url)
            if existing and not existing["is_expired"] and existing["strategy"] == "cache_first":
                self.progress.emit(i + 1, total)
                continue

            try:
                # Use ETag conditional GET if we have a previous entry
                headers = {}
                if existing and existing.get("etag"):
                    headers["If-None-Match"] = existing["etag"]

                resp = requests.get(url, timeout=8, stream=False, headers=headers)

                # 304 Not Modified — content still valid
                if resp.status_code == 304:
                    self.progress.emit(i + 1, total)
                    continue

                if resp.status_code != 200:
                    self.progress.emit(i + 1, total)
                    continue

                content_type = resp.headers.get("Content-Type", "application/octet-stream").split(";")[0].strip()

                # Only cache supported types
                if not self._is_cacheable(content_type):
                    self.progress.emit(i + 1, total)
                    continue

                # Enforce per-file size limit (skip files > 10 MB — e.g. video chunks)
                content = resp.content
                if len(content) > 10 * 1024 * 1024:
                    self.progress.emit(i + 1, total)
                    continue

                etag = resp.headers.get("ETag", "")
                self.cache_manager.store_resource(url, content, content_type, etag=etag)
                cached_count += 1
                self.resource_cached.emit(url)

            except Exception:
                pass  # Network error — skip silently

            self.progress.emit(i + 1, total)

        self.finished_caching.emit(cached_count)

    def _is_cacheable(self, content_type: str) -> bool:
        ct = content_type.lower()
        for t in self.CACHEABLE_TYPES:
            if ct.startswith(t) or t in ct:
                return True
        return False

    def stop(self):
        self._running = False
        self.quit()
        self.wait(2000)


# ---------------------------------------------------------------------------
# Background Sync Manager
# ---------------------------------------------------------------------------

class BackgroundSyncManager(QObject):
    """
    Queues failed mutation requests (POST/PUT/PATCH/DELETE) while offline.
    Replays them via SyncWorkerThread when connectivity returns.
    Uses exponential backoff: up to 5 retries, fails after that.
    """
    queue_updated = pyqtSignal(int)
    sync_finished = pyqtSignal(bool, str)

    def __init__(self, parent=None, db_path: str = "database/sync_queue.db"):
        super().__init__(parent)
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self._sync_worker: Optional["SyncWorkerThread"] = None

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    url          TEXT NOT NULL,
                    method       TEXT NOT NULL,
                    headers      TEXT DEFAULT '{}',
                    payload      TEXT DEFAULT '',
                    created_at   REAL NOT NULL,
                    retry_count  INTEGER DEFAULT 0,
                    last_attempt REAL DEFAULT 0,
                    status       TEXT DEFAULT 'pending'
                )
            """)
            conn.commit()

    def queue_request(self, url: str, method: str = "POST", headers: dict = None, payload: str = "") -> int:
        """Adds a request to the offline sync queue."""
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO sync_queue (url, method, headers, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (url, method.upper(), json.dumps(headers or {}), payload, now))
            conn.commit()
            item_id = cursor.lastrowid
        self.queue_updated.emit(self.get_pending_count())
        return item_id

    def get_pending_count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM sync_queue WHERE status = 'pending'"
            ).fetchone()
            return row[0] or 0

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT id, url, method, headers, payload, created_at, retry_count
                FROM sync_queue WHERE status = 'pending' ORDER BY id ASC
            """).fetchall()
            return [
                {
                    "id": r[0], "url": r[1], "method": r[2],
                    "headers": json.loads(r[3] or "{}"),
                    "payload": r[4], "created_at": r[5], "retry_count": r[6],
                }
                for r in rows
            ]

    def replay_async(self):
        """Starts a background SyncWorkerThread to replay queued requests."""
        if self._sync_worker and self._sync_worker.isRunning():
            return  # Already syncing

        worker = SyncWorkerThread(self)
        worker.sync_done.connect(self._on_sync_done)
        worker.finished.connect(worker.deleteLater)
        self._sync_worker = worker
        worker.start()

    def _on_sync_done(self, success_count: int, fail_count: int):
        msg = f"Synced {success_count} requests. {fail_count} failed."
        self.queue_updated.emit(self.get_pending_count())
        self.sync_finished.emit(True, msg)

    def mark_synced(self, req_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE sync_queue SET status = 'synced' WHERE id = ?", (req_id,))
            conn.commit()

    def increment_retry(self, req_id: int):
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT retry_count FROM sync_queue WHERE id = ?", (req_id,)
            ).fetchone()
            if row and row[0] >= 5:
                conn.execute(
                    "UPDATE sync_queue SET status = 'failed_max_retries' WHERE id = ?", (req_id,)
                )
            else:
                conn.execute(
                    "UPDATE sync_queue SET retry_count = retry_count + 1, last_attempt = ? WHERE id = ?",
                    (now, req_id)
                )
            conn.commit()


# ---------------------------------------------------------------------------
# Sync Worker Thread
# ---------------------------------------------------------------------------

class SyncWorkerThread(QThread):
    """
    Replays queued offline mutations on a background thread so the UI
    never blocks during network requests.

    Exponential backoff per item: waits 2^retry seconds before retrying.
    Max 5 retries per item; after that, marked 'failed_max_retries'.
    """
    sync_done = pyqtSignal(int, int)   # (success_count, fail_count)

    def __init__(self, sync_manager: BackgroundSyncManager, parent=None):
        super().__init__(parent)
        self.sync_manager = sync_manager

    def run(self):
        pending = self.sync_manager.get_pending_requests()
        success_count = 0
        fail_count = 0

        for req in pending:
            req_id  = req["id"]
            url     = req["url"]
            method  = req["method"]
            headers = req["headers"]
            payload = req["payload"]
            retries = req["retry_count"]

            # Exponential backoff: skip if not enough time has passed
            if retries > 0:
                wait_seconds = min(2 ** retries, 300)
                elapsed = time.time() - (req.get("last_attempt") or 0)
                if elapsed < wait_seconds:
                    continue

            try:
                fn_map = {
                    "POST":   requests.post,
                    "PUT":    requests.put,
                    "PATCH":  requests.patch,
                    "DELETE": requests.delete,
                    "GET":    requests.get,
                }
                fn = fn_map.get(method, requests.get)
                kwargs = {"headers": headers, "timeout": 8}
                if method in ("POST", "PUT", "PATCH") and payload:
                    kwargs["data"] = payload

                resp = fn(url, **kwargs)

                if resp.status_code < 400:
                    self.sync_manager.mark_synced(req_id)
                    success_count += 1
                else:
                    self.sync_manager.increment_retry(req_id)
                    fail_count += 1

            except Exception:
                self.sync_manager.increment_retry(req_id)
                fail_count += 1

        self.sync_done.emit(success_count, fail_count)


# ---------------------------------------------------------------------------
# Request Interceptor
# ---------------------------------------------------------------------------

class OfflineRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Intercepts all outbound browser requests.

    When ONLINE:
      - Blocks known ad/tracker domains.
      - Allows everything else through.

    When OFFLINE:
      - Mutations (POST/PUT/PATCH/DELETE): queued in BackgroundSyncManager.
      - GET requests for cached resources: redirected to searcher-cache://<hash>.
      - GET requests not in cache: allowed to fail naturally (browser shows error).

    Why not serve bytes here?
      Qt's interceptor can only block() or redirect() — it cannot write response
      bytes. Bytes are served by OfflineCacheSchemeHandler (offline_scheme_handler.py).
    """

    AD_DOMAINS = [
        "doubleclick.net", "google-analytics.com", "connect.facebook.net",
        "googlesyndication.com", "amazon-adsystem.com", "scorecardresearch.com",
        "outbrain.com", "taboola.com", "ads.twitter.com", "static.ads-twitter.com",
        "pixel.facebook.com", "analytics.google.com", "googletagmanager.com",
    ]

    def __init__(self, offline_engine, parent=None):
        super().__init__(parent)
        self.offline_engine = offline_engine

    def interceptRequest(self, info):
        url_str = info.requestUrl().toString()
        url_lower = url_str.lower()

        # 1. Ad / tracker blocking (always active)
        for domain in self.AD_DOMAINS:
            if domain in url_lower:
                info.block(True)
                return

        # 2. Skip non-HTTP schemes (data:, blob:, file:, searcher-cache:, etc.)
        if not url_str.startswith(("http://", "https://")):
            return

        # 3. Offline handling
        if not self.offline_engine.is_online():
            method = info.requestMethod().decode("utf-8", "ignore").upper()

            if method in ("POST", "PUT", "PATCH", "DELETE"):
                # Queue mutation for later replay
                self.offline_engine.sync_manager.queue_request(url_str, method)
                info.block(True)
                return

            # GET — try to serve from cache
            cached = self.offline_engine.cache_manager.get_cached_resource(url_str)
            if cached:
                hash_prefix = self.offline_engine.cache_manager._hash_url(url_str)[:16]
                cache_url = QUrl(f"searcher-cache://{hash_prefix}")
                info.redirect(cache_url)


# ---------------------------------------------------------------------------
# Central Offline Engine
# ---------------------------------------------------------------------------

class OfflineEngine(QObject):
    """
    Central orchestrator for all offline features.

    Lifecycle:
      1. Instantiated before UI (in MainWindow.__init__)
      2. start() called after UI is ready — starts detector + injects scripts
      3. stop() called in closeEvent

    Exposes:
      - is_online()                           → current connectivity bool
      - prefetch_page_resources(url_list)     → triggers CachePopulatorThread
      - get_cached_response(url)             → (bytes, content_type) or None
      - connection_changed signal
      - cache_progress signal (for UI progress bar)
    """

    connection_changed = pyqtSignal(bool)    # True = online, False = offline
    cache_progress     = pyqtSignal(int, int) # (done, total) during prefetch
    cache_batch_done   = pyqtSignal(int)     # total items cached in last batch

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cache_manager = ResourceCacheManager()
        self.sync_manager  = BackgroundSyncManager(self)
        self.detector      = OfflineDetector(self)
        self._is_online    = True
        self._populator: Optional[CachePopulatorThread] = None

        # The interceptor is set on the profile by main_window.py
        self.interceptor = OfflineRequestInterceptor(self, parent)

        # Wire detector
        self.detector.status_changed.connect(self._on_connectivity_changed)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self):
        """Start the connectivity detector and inject browser-side scripts."""
        self.detector.start()
        # Initial connectivity probe (blocking, but short: 2s max)
        self._is_online = self.detector.check_connection()
        self._inject_browser_scripts()

    def stop(self):
        """Clean shutdown — stop all threads."""
        if self._populator and self._populator.isRunning():
            self._populator.stop()
        self.detector.stop()

    def is_online(self) -> bool:
        return self._is_online

    def prefetch_page_resources(self, url_list: List[str]):
        """
        Called by tabs.py after a page finishes loading online.
        Starts a CachePopulatorThread to download & cache all sub-resources.
        Cancels any previous populator that might still be running.
        """
        if not self._is_online or not url_list:
            return

        # Cancel previous populator if still running
        if self._populator and self._populator.isRunning():
            self._populator.stop()

        populator = CachePopulatorThread(url_list, self.cache_manager, self)
        populator.progress.connect(self.cache_progress)
        populator.finished_caching.connect(self.cache_batch_done)
        populator.finished.connect(populator.deleteLater)
        populator.start()
        self._populator = populator

    def get_cached_response(self, url: str) -> Optional[Tuple[bytes, str]]:
        """
        Returns (content_bytes, content_type) for a cached URL, or None.
        Used by offline_scheme_handler for direct serving.
        """
        cached = self.cache_manager.get_cached_resource(url)
        if cached and os.path.exists(cached["file_path"]):
            try:
                with open(cached["file_path"], "rb") as f:
                    return f.read(), cached["content_type"]
            except Exception:
                pass
        return None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_connectivity_changed(self, is_online: bool):
        self._is_online = is_online
        self.connection_changed.emit(is_online)
        if is_online:
            # Replay pending sync requests in background (off UI thread)
            self.sync_manager.replay_async()

    def _inject_browser_scripts(self):
        """
        Injects two scripts into every page via QWebEngineProfile:

        1. Draft Saver — saves all form fields + scroll position to localStorage
           so user input is never lost during offline navigation or page crashes.

        2. PWA Detector — detects if the site registers its own Service Worker
           and emits a console message so the browser can note it and avoid
           interfering. Also exposes navigator.onLine polyfill updates.
        """
        profile = QWebEngineProfile.defaultProfile()

        # ------ Script 1: Draft Saver ------
        draft_script = QWebEngineScript()
        draft_script.setName("SearcherDraftSaver")
        draft_script.setSourceCode("""
(function() {
    if (window.__searcherDraftSaverInjected) return;
    window.__searcherDraftSaverInjected = true;

    const DRAFT_KEY = '__searcher_draft__' + window.location.pathname;

    function saveDrafts() {
        const data = { time: Date.now(), fields: {}, scroll: { x: window.scrollX, y: window.scrollY } };
        document.querySelectorAll('input, textarea, select').forEach((el, idx) => {
            if (el.type === 'password' || el.type === 'hidden') return;
            const key = el.name || el.id || ('input_' + idx);
            data.fields[key] = (el.type === 'checkbox' || el.type === 'radio') ? el.checked : el.value;
        });
        try { localStorage.setItem(DRAFT_KEY, JSON.stringify(data)); } catch(e) {}
    }

    function restoreDrafts() {
        try {
            const raw = localStorage.getItem(DRAFT_KEY);
            if (!raw) return;
            const data = JSON.parse(raw);
            if (!data || !data.fields) return;
            document.querySelectorAll('input, textarea, select').forEach((el, idx) => {
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
            if (data.scroll) window.scrollTo(data.scroll.x, data.scroll.y);
        } catch(e) {}
    }

    document.addEventListener('input', saveDrafts);
    document.addEventListener('change', saveDrafts);
    window.addEventListener('scroll', () => { clearTimeout(window.__searcherScrollTimer); window.__searcherScrollTimer = setTimeout(saveDrafts, 300); });
    document.addEventListener('DOMContentLoaded', restoreDrafts);
    setTimeout(restoreDrafts, 800);
})();
        """)
        draft_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        draft_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        draft_script.setRunsOnSubFrames(False)
        profile.scripts().insert(draft_script)

        # ------ Script 2: PWA / Service Worker Detector + Resource Harvester ------
        pwa_script = QWebEngineScript()
        pwa_script.setName("SearcherPWADetector")
        pwa_script.setSourceCode("""
(function() {
    if (window.__searcherPWADetectorInjected) return;
    window.__searcherPWADetectorInjected = true;

    // Detect if site registers its own Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(regs => {
            if (regs.length > 0) {
                console.log('[Searcher] Site has ' + regs.length + ' Service Worker(s) — native offline support active.');
            }
        }).catch(() => {});
    }

    // Harvest all resource URLs for browser-level pre-caching
    window.addEventListener('load', function() {
        const urls = [];
        document.querySelectorAll('link[href], script[src], img[src], source[src]').forEach(el => {
            const url = el.href || el.src;
            if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
                urls.push(url);
            }
        });
        // Also grab @font-face and CSS background URLs via performance entries
        if (window.performance && window.performance.getEntriesByType) {
            window.performance.getEntriesByType('resource').forEach(entry => {
                if (entry.name && entry.name.startsWith('http')) {
                    urls.push(entry.name);
                }
            });
        }
        // Deduplicate
        const unique = [...new Set(urls)];
        if (unique.length > 0) {
            console.log('[Searcher:Resources]' + JSON.stringify(unique.slice(0, 150)));
        }
    });
})();
        """)
        pwa_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        pwa_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        pwa_script.setRunsOnSubFrames(False)
        profile.scripts().insert(pwa_script)
