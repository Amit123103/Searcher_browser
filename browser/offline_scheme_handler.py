"""
Searcher Browser - Offline Cache Scheme Handler
===============================================
Registers a custom URL scheme 'searcher-cache://' with the Qt WebEngine profile.
When the browser is offline and requests a resource that exists in the local
ResourceCacheManager, the OfflineRequestInterceptor redirects the request to:

    searcher-cache://<url_hash>

This handler then reads the cached file from disk and returns it to the
renderer, making the page load from the local cache as if it came from the network.

Why a custom scheme?
  QWebEngineUrlRequestInterceptor can only block or redirect — it cannot serve
  bytes back to the browser. A QWebEngineUrlSchemeHandler CAN serve bytes.
  This is the standard Qt6 way to implement browser-level offline caching.
"""

import os
from PyQt6.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlScheme, QWebEngineUrlRequestJob
from PyQt6.QtCore import QBuffer, QByteArray


def register_offline_scheme():
    """
    Must be called BEFORE QApplication is created (Qt requirement).
    Registers the 'searcher-cache' URL scheme so Qt allows it in the renderer.
    """
    scheme = QWebEngineUrlScheme(b"searcher-cache")
    scheme.setFlags(
        QWebEngineUrlScheme.Flag.SecureScheme |
        QWebEngineUrlScheme.Flag.LocalScheme |
        QWebEngineUrlScheme.Flag.LocalAccessAllowed |
        QWebEngineUrlScheme.Flag.CorsEnabled
    )
    QWebEngineUrlScheme.registerScheme(scheme)


class OfflineCacheSchemeHandler(QWebEngineUrlSchemeHandler):
    """
    Serves cached web resources from disk when the browser is offline.

    URL format:  searcher-cache://<16-char-hash-prefix>
    The handler looks up the hash in the ResourceCacheManager's SQLite index,
    reads the file, and writes it to the QWebEngineUrlRequestJob response.

    Caching strategies honoured:
      - cache_first  : always serve from cache (static assets: CSS, JS, fonts)
      - network_first: only serve from cache when offline (APIs)
      - stale_while_revalidate: serve cache immediately, update in background
    """

    def __init__(self, cache_manager, parent=None):
        super().__init__(parent)
        self.cache_manager = cache_manager

    def requestStarted(self, job: QWebEngineUrlRequestJob):
        """
        Called by Qt whenever the renderer requests a searcher-cache:// URL.
        Reads the cached file and writes it to the response.
        """
        url_str = job.requestUrl().toString()
        # The host part of searcher-cache://HASH is the url_hash prefix
        url_hash_prefix = job.requestUrl().host()

        # Look up by hash prefix in the cache index
        cached = self.cache_manager.get_cached_by_hash_prefix(url_hash_prefix)

        if cached and os.path.exists(cached["file_path"]):
            try:
                with open(cached["file_path"], "rb") as f:
                    data = f.read()

                content_type = (cached.get("content_type") or "application/octet-stream").encode("utf-8")
                buf = QBuffer()
                buf.setData(QByteArray(data))
                buf.open(QBuffer.OpenModeFlag.ReadOnly)
                job.reply(content_type, buf)
                return
            except Exception as e:
                print(f"[OfflineCacheSchemeHandler] Error reading cache file: {e}")

        # Not found in cache — fail the request
        job.fail(QWebEngineUrlRequestJob.Error.UrlNotFound)
