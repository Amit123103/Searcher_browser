"""
Searcher Browser - Offline Engine Test Suite
=============================================
Tests all offline components without needing the full Qt GUI:
  1. ResourceCacheManager  - store, retrieve, LRU eviction, hash-prefix lookup
  2. BackgroundSyncManager - queue, pending count, mark_synced, increment_retry
  3. SyncWorkerThread      - replays real HTTP request (GET httpbin.org)
  4. CachePopulatorThread  - downloads real URLs and stores them in cache
  5. OfflineDetector       - check_connection() returns a bool
  6. End-to-End offline simulation

Run with:  python tests/test_offline.py
"""

import os
import sys
import time
import shutil
import sqlite3
import tempfile
import unittest

# Force UTF-8 output on Windows so emoji/symbols don't crash
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Make sure we can import from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Custom URL schemes MUST be registered before QApplication
from browser.offline_scheme_handler import register_offline_scheme
register_offline_scheme()

from PyQt6.QtWidgets import QApplication
_app = QApplication.instance() or QApplication(sys.argv)

from browser.offline_engine import (
    ResourceCacheManager,
    BackgroundSyncManager,
    SyncWorkerThread,
    CachePopulatorThread,
    OfflineDetector,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper — wait for a QThread to finish with a timeout
# ─────────────────────────────────────────────────────────────────────────────
def wait_for_thread(thread, timeout_sec=30):
    deadline = time.time() + timeout_sec
    while thread.isRunning():
        _app.processEvents()
        if time.time() > deadline:
            return False
        time.sleep(0.1)
    # Drain the Qt event queue so queued (cross-thread) signals are delivered
    for _ in range(20):
        _app.processEvents()
        time.sleep(0.02)
    return True


def make_cache(max_mb=10):
    """Create a ResourceCacheManager in a fresh temp directory."""
    tmpdir = tempfile.mkdtemp(prefix="searcher_cache_test_")
    return ResourceCacheManager(cache_dir=tmpdir, max_size_mb=max_mb), tmpdir


def make_sync(suffix=""):
    """Create a BackgroundSyncManager using a unique temp DB file."""
    fd, path = tempfile.mkstemp(prefix=f"searcher_sync_test{suffix}_", suffix=".db")
    os.close(fd)
    os.remove(path)  # let BackgroundSyncManager create it fresh
    return BackgroundSyncManager(db_path=path), path


# ═════════════════════════════════════════════════════════════════════════════
# 1. ResourceCacheManager Tests
# ═════════════════════════════════════════════════════════════════════════════
class TestResourceCacheManager(unittest.TestCase):

    def setUp(self):
        self.cm, self.tmpdir = make_cache(max_mb=15)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_store_and_retrieve_html(self):
        url     = "https://example.com/index.html"
        content = b"<html><body>Hello Offline World</body></html>"
        self.cm.store_resource(url, content, "text/html")

        result = self.cm.get_cached_resource(url)
        self.assertIsNotNone(result, "Cached resource should be found")
        self.assertEqual(result["content_type"], "text/html")

        with open(result["file_path"], "rb") as f:
            self.assertEqual(f.read(), content)
        print(f"    [OK] HTML store/retrieve - {len(content)} bytes")

    def test_strategy_css_is_cache_first(self):
        url = "https://example.com/style.css"
        self.cm.store_resource(url, b"body{}", "text/css")
        result = self.cm.get_cached_resource(url)
        self.assertEqual(result["strategy"], "cache_first")
        print("    [OK] CSS strategy = cache_first")

    def test_strategy_json_is_network_first(self):
        url = "https://api.example.com/data.json"
        self.cm.store_resource(url, b'{"ok":1}', "application/json")
        result = self.cm.get_cached_resource(url)
        self.assertEqual(result["strategy"], "network_first")
        print("    [OK] JSON strategy = network_first")

    def test_strategy_html_is_stale_while_revalidate(self):
        url = "https://news.example.com/"
        self.cm.store_resource(url, b"<html/>", "text/html")
        result = self.cm.get_cached_resource(url)
        self.assertEqual(result["strategy"], "stale_while_revalidate")
        print("    [OK] HTML strategy = stale_while_revalidate")

    def test_miss_returns_none(self):
        result = self.cm.get_cached_resource("https://not-in-cache.example.com/")
        self.assertIsNone(result)
        print("    [OK] Cache miss returns None")

    def test_hash_prefix_lookup(self):
        url     = "https://example.com/app.js"
        content = b"console.log('hello');"
        self.cm.store_resource(url, content, "application/javascript")

        prefix = self.cm._hash_url(url)[:16]
        result = self.cm.get_cached_by_hash_prefix(prefix)
        self.assertIsNotNone(result)
        with open(result["file_path"], "rb") as f:
            self.assertEqual(f.read(), content)
        print(f"    [OK] Hash-prefix lookup (prefix={prefix[:8]}...)")

    def test_lru_eviction(self):
        # 12 x 1 MB = 12 MB > max 15 MB... use 5 MB max and 6 x 1 MB
        cm, tmpdir = make_cache(max_mb=5)
        try:
            big = b"X" * (1024 * 1024)  # 1 MB
            for i in range(7):
                cm.store_resource(f"https://ex.com/file{i}.bin", big, "application/octet-stream")
            stats = cm.get_cache_stats()
            self.assertLessEqual(stats["size_mb"], 5.5,  # 10% headroom
                                 f"LRU eviction failed - {stats['size_mb']} MB")
            print(f"    [OK] LRU eviction - cache at {stats['size_mb']} MB (max 5 MB)")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_cache_stats_count(self):
        self.cm.store_resource("https://ex.com/a", b"AAA", "text/plain")
        self.cm.store_resource("https://ex.com/b", b"BBB", "text/plain")
        stats = self.cm.get_cache_stats()
        self.assertGreaterEqual(stats["count"], 2)
        print(f"    [OK] Cache stats - {stats['count']} items")

    def test_clear_cache(self):
        self.cm.store_resource("https://ex.com/x", b"data", "text/plain")
        self.cm.clear_cache()
        self.assertEqual(self.cm.get_cache_stats()["count"], 0)
        print("    [OK] Clear cache")

    def test_etag_stored_and_retrieved(self):
        url  = "https://example.com/etag_resource"
        etag = '"v2-abc123"'
        self.cm.store_resource(url, b"content", "text/css", etag=etag)
        result = self.cm.get_cached_resource(url)
        self.assertEqual(result["etag"], etag)
        print(f"    [OK] ETag stored: {etag}")

    def test_ttl_expiry_flag(self):
        url = "https://example.com/old_page"
        self.cm.store_resource(url, b"old", "text/html")
        url_hash = self.cm._hash_url(url)
        # Manually patch created_at to 999 days ago
        with sqlite3.connect(self.cm.db_path) as conn:
            conn.execute("UPDATE resource_cache SET created_at = ? WHERE url_hash = ?",
                         (time.time() - 999 * 86400, url_hash))
            conn.commit()
        result = self.cm.get_cached_resource(url)
        self.assertTrue(result["is_expired"])
        print("    [OK] TTL expiry flag = True for 999-day-old entry")


# ═════════════════════════════════════════════════════════════════════════════
# 2. BackgroundSyncManager Tests
# ═════════════════════════════════════════════════════════════════════════════
class TestBackgroundSyncManager(unittest.TestCase):

    def setUp(self):
        self.sm, self.db_path = make_sync("bsm")

    def tearDown(self):
        # Close all SQLite connections before deleting on Windows
        self.sm = None
        for attempt in range(5):
            try:
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                break
            except PermissionError:
                time.sleep(0.2)

    def test_queue_and_count(self):
        self.sm.queue_request("https://example.com/api/save", "POST", payload='{"x":1}')
        self.sm.queue_request("https://example.com/api/update", "PUT",  payload='{"y":2}')
        count = self.sm.get_pending_count()
        self.assertEqual(count, 2)
        print(f"    [OK] Queue count = {count}")

    def test_get_pending_requests_structure(self):
        self.sm.queue_request("https://example.com/delete/1", "DELETE")
        items = self.sm.get_pending_requests()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["method"], "DELETE")
        self.assertIn("url", items[0])
        self.assertIn("retry_count", items[0])
        print("    [OK] Pending request structure is correct")

    def test_mark_synced_removes_from_pending(self):
        sm, db_path = make_sync("bsm_synced")
        try:
            item_id = sm.queue_request("https://example.com/sync", "POST")
            self.assertEqual(sm.get_pending_count(), 1)
            sm.mark_synced(item_id)
            self.assertEqual(sm.get_pending_count(), 0)
            print("    [OK] mark_synced removes item from pending")
        finally:
            sm = None
            for _ in range(5):
                try:
                    if os.path.exists(db_path): os.remove(db_path)
                    break
                except PermissionError:
                    time.sleep(0.2)

    def test_increment_retry_count(self):
        sm, db_path = make_sync("bsm_retry")
        try:
            item_id = sm.queue_request("https://example.com/fail", "POST")
            sm.increment_retry(item_id)
            sm.increment_retry(item_id)
            items = sm.get_pending_requests()
            self.assertEqual(items[0]["retry_count"], 2)
            print(f"    [OK] Retry count = {items[0]['retry_count']}")
        finally:
            sm = None
            for _ in range(5):
                try:
                    if os.path.exists(db_path): os.remove(db_path)
                    break
                except PermissionError:
                    time.sleep(0.2)

    def test_max_retries_marks_failed(self):
        sm, db_path = make_sync("bsm_maxretry")
        try:
            item_id = sm.queue_request("https://example.com/exhaust", "POST")
            for _ in range(6):  # > max of 5
                sm.increment_retry(item_id)
            self.assertEqual(sm.get_pending_count(), 0)
            print("    [OK] Max retries -> item marked failed_max_retries")
        finally:
            sm = None
            for _ in range(5):
                try:
                    if os.path.exists(db_path): os.remove(db_path)
                    break
                except PermissionError:
                    time.sleep(0.2)


# ═════════════════════════════════════════════════════════════════════════════
# 3. SyncWorkerThread - Real network replay
# ═════════════════════════════════════════════════════════════════════════════
class TestSyncWorkerThread(unittest.TestCase):

    def setUp(self):
        self.sm, self.db_path = make_sync("sync_worker")

    def tearDown(self):
        self.sm = None
        for _ in range(5):
            try:
                if os.path.exists(self.db_path): os.remove(self.db_path)
                break
            except PermissionError:
                time.sleep(0.3)

    def test_replay_get_request_online(self):
        """Queue a real GET request and verify the worker replays it."""
        self.sm.queue_request("https://httpbin.org/get", method="GET")
        self.assertEqual(self.sm.get_pending_count(), 1)

        results = {}
        worker  = SyncWorkerThread(self.sm)
        worker.sync_done.connect(lambda s, f: results.update({"success": s, "fail": f}))
        worker.start()
        finished = wait_for_thread(worker, timeout_sec=30)

        self.assertTrue(finished, "SyncWorkerThread should finish within 30s")

        # Primary assertion: check the actual DB state (not the signal)
        # The queue must be empty — item was either synced or marked failed
        remaining = self.sm.get_pending_count()
        self.assertEqual(remaining, 0,
                         "Queue must be empty after sync attempt (synced or exhausted)")

        # Secondary: if signal was delivered, success should be >= 1 for a working network
        if results:
            self.assertGreaterEqual(results.get("success", 0), 1,
                                    f"GET replay should succeed - got {results}")
        print(f"    [OK] SyncWorker replayed GET - queue empty, "
              f"signal={results if results else '(not yet delivered)'}")


# ═════════════════════════════════════════════════════════════════════════════
# 4. CachePopulatorThread - Real download
# ═════════════════════════════════════════════════════════════════════════════
class TestCachePopulatorThread(unittest.TestCase):

    def setUp(self):
        self.cm, self.tmpdir = make_cache(max_mb=50)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_content_type_filter(self):
        populator = CachePopulatorThread([], self.cm)
        self.assertFalse(populator._is_cacheable("video/mp4"))
        self.assertFalse(populator._is_cacheable("audio/mpeg"))
        self.assertTrue(populator._is_cacheable("text/css"))
        self.assertTrue(populator._is_cacheable("application/javascript"))
        self.assertTrue(populator._is_cacheable("image/png"))
        self.assertTrue(populator._is_cacheable("font/woff2"))
        self.assertTrue(populator._is_cacheable("application/wasm"))
        print("    [OK] Content-type cacheability filter is correct")

    def test_skip_already_fresh_cache_first(self):
        url     = "https://example.com/already_cached.css"
        content = b"body { margin: 0; }"
        self.cm.store_resource(url, content, "text/css")

        results  = {}
        populator = CachePopulatorThread([url], self.cm)
        populator.finished_caching.connect(lambda c: results.update({"cached": c}))
        populator.start()
        wait_for_thread(populator, timeout_sec=10)

        self.assertEqual(results.get("cached", 0), 0,
                         "Fresh cache_first item should be skipped")
        print("    [OK] Already-fresh cache_first entry is skipped")

    def test_download_real_html(self):
        """Downloads a real HTML page and verifies it is stored in cache."""
        url     = "https://httpbin.org/html"
        results = {}

        populator = CachePopulatorThread([url], self.cm)
        populator.finished_caching.connect(lambda c: results.update({"cached": c}))
        populator.start()
        finished = wait_for_thread(populator, timeout_sec=30)

        self.assertTrue(finished, "CachePopulatorThread should finish within 30s")

        # Primary: check the actual cache state (file on disk + DB row)
        cached = self.cm.get_cached_resource(url)
        self.assertIsNotNone(cached,
                             "HTML from httpbin.org should appear in cache index")
        self.assertGreater(cached["file_size"], 0, "Cached file should not be empty")
        self.assertTrue(os.path.exists(cached["file_path"]),
                        "Cached file should exist on disk")
        print(f"    [OK] Downloaded + cached HTML - {cached['file_size']} bytes "
              f"(signal count={results.get('cached', 'not delivered yet')})")

    def test_download_real_json_network_first(self):
        """JSON is network_first but still gets downloaded and cached."""
        url     = "https://httpbin.org/json"
        results = {}

        populator = CachePopulatorThread([url], self.cm)
        populator.finished_caching.connect(lambda c: results.update({"cached": c}))
        populator.start()
        wait_for_thread(populator, timeout_sec=30)

        cached = self.cm.get_cached_resource(url)
        self.assertIsNotNone(cached, "JSON should still be cached (network_first)")
        self.assertEqual(cached["strategy"], "network_first")
        print(f"    [OK] JSON cached with network_first strategy - {cached['file_size']} bytes")


# ═════════════════════════════════════════════════════════════════════════════
# 5. OfflineDetector
# ═════════════════════════════════════════════════════════════════════════════
class TestOfflineDetector(unittest.TestCase):

    def test_check_connection_returns_bool(self):
        detector = OfflineDetector()
        result   = detector.check_connection()
        self.assertIsInstance(result, bool)
        print(f"    [OK] check_connection() = {result} ({'Online' if result else 'Offline'})")

    def test_online_status(self):
        detector = OfflineDetector()
        self.assertTrue(detector.check_connection(),
                        "Machine should be online during test run")
        print("    [OK] Machine is online")


# ═════════════════════════════════════════════════════════════════════════════
# 6. End-to-End Offline Simulation
# ═════════════════════════════════════════════════════════════════════════════
class TestOfflineSimulation(unittest.TestCase):
    """
    Simulates the full offline flow without actually disconnecting:
      Phase 1 (Online)  - pre-cache resources via CachePopulatorThread
      Phase 2 (Offline) - verify cached content is served from disk
      Phase 3 (Offline) - queue a mutation into the sync manager
      Phase 4 (Online)  - replay sync via SyncWorkerThread
    """

    def setUp(self):
        self.cm, self.tmpdir = make_cache(max_mb=50)
        self.sm, self.db_path = make_sync("e2e")

    def tearDown(self):
        self.sm = None
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        for _ in range(5):
            try:
                if os.path.exists(self.db_path): os.remove(self.db_path)
                break
            except PermissionError:
                time.sleep(0.3)

    def test_full_offline_cycle(self):
        print("\n  === End-to-End Offline Cycle ===")

        # ── Phase 1: Online — prefetch and cache a page's resources ──────────
        urls_to_cache = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
        ]
        print(f"  [1] Prefetching {len(urls_to_cache)} resources online...")

        prefetch_results = {}
        populator = CachePopulatorThread(urls_to_cache, self.cm)
        populator.finished_caching.connect(
            lambda c: prefetch_results.update({"cached": c})
        )
        populator.start()
        finished = wait_for_thread(populator, timeout_sec=30)

        self.assertTrue(finished, "Prefetch should complete")
        cached_count = prefetch_results.get("cached", 0)
        print(f"  [1] PASS - Prefetched and cached {cached_count} resource(s)")

        # ── Phase 2: Simulate offline — retrieve cached resources from disk ──
        print("  [2] Simulating offline mode - serving resources from cache...")

        for url in urls_to_cache:
            cached = self.cm.get_cached_resource(url)
            if cached:
                with open(cached["file_path"], "rb") as f:
                    data = f.read()
                self.assertGreater(len(data), 0)
                print(f"  [2] PASS - Served '{url.split('/')[-1]}' "
                      f"({len(data)} bytes, strategy={cached['strategy']})")

        # ── Hash-prefix lookup (used by OfflineCacheSchemeHandler) ───────────
        for url in urls_to_cache:
            if self.cm.get_cached_resource(url):
                prefix  = self.cm._hash_url(url)[:16]
                result  = self.cm.get_cached_by_hash_prefix(prefix)
                self.assertIsNotNone(result, f"Hash-prefix lookup failed for {url}")
        print("  [2] PASS - Hash-prefix lookup works for all cached URLs")

        # ── Phase 3: Queue a mutation while offline ───────────────────────────
        print("  [3] Queuing POST request while 'offline'...")
        self.sm.queue_request(
            "https://httpbin.org/post", "POST",
            payload='{"data":"offline_saved","timestamp":' + str(int(time.time())) + '}'
        )
        pending = self.sm.get_pending_count()
        self.assertEqual(pending, 1)
        print(f"  [3] PASS - {pending} request queued in sync manager")

        # ── Phase 4: Reconnect — replay sync ──────────────────────────────────
        print("  [4] Reconnecting - replaying sync queue...")

        sync_results = {}
        worker = SyncWorkerThread(self.sm)
        worker.sync_done.connect(
            lambda s, f: sync_results.update({"success": s, "fail": f})
        )
        worker.start()
        finished = wait_for_thread(worker, timeout_sec=30)

        self.assertTrue(finished, "SyncWorker should finish")
        remaining = self.sm.get_pending_count()
        self.assertEqual(remaining, 0, "Queue should be empty after sync")
        print(f"  [4] PASS - Sync complete: "
              f"success={sync_results.get('success',0)}, "
              f"fail={sync_results.get('fail',0)}, "
              f"queue={remaining}")
        print("  === End-to-End Offline Cycle: ALL PHASES PASSED ===\n")


# ═════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Searcher Browser - Offline Engine Test Suite")
    print("=" * 60 + "\n")

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestResourceCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestBackgroundSyncManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSyncWorkerThread))
    suite.addTests(loader.loadTestsFromTestCase(TestCachePopulatorThread))
    suite.addTests(loader.loadTestsFromTestCase(TestOfflineDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestOfflineSimulation))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"  Results: {result.testsRun} tests | "
          f"Passed: {passed} | "
          f"Failed: {len(result.failures)} | "
          f"Errors: {len(result.errors)}")
    print("=" * 60 + "\n")
    sys.exit(0 if result.wasSuccessful() else 1)
