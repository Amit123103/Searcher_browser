from PyQt6.QtWidgets import QTabWidget, QMenu, QToolButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QUrl, pyqtSignal, Qt, QUrlQuery
from PyQt6.QtWebEngineCore import QWebEnginePage

class SearcherPage(QWebEnginePage):
    """Custom page to intercept navigation requests."""
    
    def __init__(self, parent_browser, parent_tabs):
        super().__init__(parent_browser)
        self.parent_browser = parent_browser
        self.parent_tabs = parent_tabs
        
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Allow all navigation by default
        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def createWindow(self, _type):
        """Handle links that request opening in a new window (e.g. target='_blank') by opening a new tab."""
        new_browser = self.parent_tabs.add_new_tab()
        return new_browser.page()

class BrowserTabWidget(QTabWidget):
    """
    Custom Tab Widget for Searcher Browser to manage web engine views.
    Handles adding, closing, and tracking signals for multiple web pages.
    """
    
    url_changed = pyqtSignal(QUrl)
    title_changed = pyqtSignal(str)
    load_progress = pyqtSignal(int)
    load_started = pyqtSignal()
    load_finished = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True) # Removes extra borders around the tab widget
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.on_current_tab_changed)
        
        # Setup Context Menu for Tab Bar
        self.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self.show_tab_context_menu)
        
        # Track recently closed tabs for restoration
        self.closed_tabs = []
        
        # Inject custom "Searcher" branding script on Google
        from PyQt6.QtWebEngineCore import QWebEngineScript, QWebEngineProfile
        script = QWebEngineScript()
        script.setName("SearcherBranding")
        script.setSourceCode("""
        (function() {
            function injectSearcherBrand() {
                if (!window.location.hostname.includes('google.')) return;
                
                // Replace the top left logo in search results
                let logos = document.querySelectorAll('a#logo, a.logo, a[title="Go to Google Home"], a[href^="https://www.google.com/?"]');
                logos.forEach(a => {
                    if (a.dataset.searcherApplied) return;
                    a.innerHTML = '<div style="font-size:24px; font-weight:bold; color:#38bdf8; font-family:sans-serif; margin:8px 12px; display:flex; align-items:center; line-height: 1;">Searcher</div>';
                    a.dataset.searcherApplied = "true";
                    a.style.textDecoration = 'none';
                });
                
                // For main page Google logo
                let mainLogos = document.querySelectorAll('img[alt="Google"]');
                mainLogos.forEach(img => {
                    if (img.dataset.searcherApplied) return;
                    img.style.display = 'none';
                    let div = document.createElement('div');
                    div.innerText = 'Searcher';
                    div.style.fontSize = '80px';
                    div.style.fontWeight = 'bold';
                    div.style.color = '#38bdf8';
                    div.style.textAlign = 'center';
                    div.style.fontFamily = 'sans-serif';
                    img.parentElement.appendChild(div);
                    img.dataset.searcherApplied = "true";
                });
                
                // Change title
                if (document.title.includes('Google')) {
                    document.title = document.title.replace('Google Search', 'Searcher').replace('Google', 'Searcher');
                }
            }

            if (window.location.hostname.includes('google.')) {
                document.addEventListener('DOMContentLoaded', injectSearcherBrand);
                setInterval(injectSearcherBrand, 200); // Handle dynamic JS updates
            }
        })();
        """)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(False)
        QWebEngineProfile.defaultProfile().scripts().insert(script)
        
    def add_new_tab(self, qurl=None, label="New Tab"):
        """Adds a new tab containing a QWebEngineView."""
        if qurl is None:
            import os
            # Set default new tab to our local start page
            start_page = QUrl.fromLocalFile(os.path.abspath("assets/start_page.html"))
            qurl = start_page
            
        browser = QWebEngineView()
        # Set custom page to intercept navigation
        page = SearcherPage(browser, self)
        browser.setPage(page)
        browser.setUrl(qurl)
        
        # Connect signals for this specific browser view
        browser.urlChanged.connect(lambda url, b=browser: self.on_url_changed(url, b))
        browser.titleChanged.connect(lambda title, b=browser: self.on_title_changed(title, b))
        browser.loadProgress.connect(lambda p, b=browser: self.on_load_progress(p, b))
        browser.loadStarted.connect(lambda b=browser: self.on_load_started(b))
        browser.loadFinished.connect(lambda ok, b=browser: self.on_load_finished(ok, b))
        
        # Add tab and switch to it
        i = self.addTab(browser, label)
        self.setCurrentIndex(i)
        
        return browser
        
    def current_browser(self):
        """Returns the currently active QWebEngineView."""
        return self.currentWidget()
        
    def close_tab(self, i):
        """Closes the tab at index i. If it's the last tab, close the window."""
        if self.count() == 1:
            self.window().close()
            return
            
        # Save URL before closing
        browser = self.widget(i)
        if hasattr(browser, 'url'):
            url = browser.url().toString()
            if url and url != "about:blank":
                self.closed_tabs.append(url)
                # Keep only the last 10 closed tabs
                if len(self.closed_tabs) > 10:
                    self.closed_tabs.pop(0)
            
        # Delete the widget to free resources
        browser.deleteLater()
        self.removeTab(i)
        
    def restore_closed_tab(self):
        """Restores the most recently closed tab."""
        if self.closed_tabs:
            url = self.closed_tabs.pop()
            self.add_new_tab(QUrl(url))
            
    def show_tab_context_menu(self, position):
        menu = QMenu()
        organize_action = QAction("Smart Organize Tabs (AI)", self)
        organize_action.triggered.connect(self.trigger_smart_organize)
        menu.addAction(organize_action)
        menu.exec(self.tabBar().mapToGlobal(position))
        
    def trigger_smart_organize(self):
        # We need to call the AI service from the main window
        if hasattr(self.parent(), "smart_organize_tabs"):
            self.parent().smart_organize_tabs()
        
    # --- Signal Handlers ---
    # These propagate signals from the active web view to the main window
    
    def on_current_tab_changed(self, i):
        browser = self.current_browser()
        if browser:
            url = browser.url() if hasattr(browser, 'url') else QUrl("searcher://settings")
            title = browser.title() if hasattr(browser, 'title') else "Settings"
            self.url_changed.emit(url)
            self.title_changed.emit(title)
            
    def on_url_changed(self, qurl, browser):
        # Only emit if the signal came from the currently active tab
        if browser == self.current_browser():
            self.url_changed.emit(qurl)
            
    def on_title_changed(self, title, browser):
        i = self.indexOf(browser)
        if i >= 0:
            # Update the tab text
            display_title = title[:30] + '...' if len(title) > 30 else title
            self.setTabText(i, display_title)
        
        if browser == self.current_browser():
            self.title_changed.emit(title)
            
    def on_load_progress(self, p, browser):
        if browser == self.current_browser():
            self.load_progress.emit(p)
            
    def on_load_started(self, browser):
        if browser == self.current_browser():
            self.load_started.emit()
            
    def on_load_finished(self, ok, browser):
        if browser == self.current_browser():
            self.load_finished.emit(ok)
