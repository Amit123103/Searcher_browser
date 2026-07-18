from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class AdBlockerInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Basic Ad Blocker interceptor.
    Checks incoming URL requests against a simple block list and blocks them if they match.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Basic list of known tracker and ad domains for Phase 3
        self.block_list = [
            "doubleclick.net",
            "google-analytics.com",
            "connect.facebook.net",
            "googlesyndication.com",
            "amazon-adsystem.com",
            "scorecardresearch.com",
            "outbrain.com",
            "taboola.com"
        ]
        
    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        
        # Simple substring check (in a real browser this would use EasyList and complex parsing)
        for blocked_domain in self.block_list:
            if blocked_domain in url:
                # Optionally log blocked requests for debugging
                # print(f"AdBlocker blocked: {url}")
                info.block(True)
                return
