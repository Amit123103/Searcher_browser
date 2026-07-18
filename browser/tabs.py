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
        if isMainFrame:
            url_str = url.toString()
            # Intercept Google Search queries and our custom local search scheme
            if url_str.startswith("https://www.google.com/search?q=") or url_str.startswith("https://searcher.local/search?q="):
                query = QUrlQuery(url).queryItemValue("q")
                if query:
                    # Delay the perform_search call so we return from here first
                    from PyQt6.QtCore import QTimer
                    main_window = self.parent_tabs.window()
                    if hasattr(main_window, 'perform_search'):
                        QTimer.singleShot(0, lambda: main_window.perform_search(query))
                    return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

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
        
        # Corner Container
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
        from PyQt6.QtGui import QIcon
        import os
        
        corner_container = QWidget(self)
        corner_layout = QHBoxLayout(corner_container)
        corner_layout.setContentsMargins(5, 5, 10, 5)
        corner_layout.setSpacing(10)
        
        # Add New Tab button (+)
        self.new_tab_btn = QToolButton(self)
        self.new_tab_btn.setText("+")
        self.new_tab_btn.setToolTip("Open a new tab")
        self.new_tab_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                color: #e2e8f0;
                font-size: 20px;
                font-weight: 400;
                padding: 0px 8px;
            }
            QToolButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 6px;
            }
        """)
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        
        # Ask Gemini button
        self.ask_ai_btn = QPushButton("Ask Gemini", self)
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        self.ask_ai_btn.setIcon(QIcon(os.path.join(assets_dir, 'ai.svg'))) # using ai.svg for now
        self.ask_ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a3443;
                color: #ffffff;
                border-radius: 14px;
                padding: 4px 12px;
                font-size: 13px;
                font-weight: 500;
                border: 1px solid #5a4453;
            }
            QPushButton:hover {
                background-color: #5a4453;
            }
        """)
        
        corner_layout.addWidget(self.new_tab_btn)
        corner_layout.addWidget(self.ask_ai_btn)
        
        self.setCornerWidget(corner_container, Qt.Corner.TopRightCorner)
        
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
        """Closes the tab at index i. If it's the last tab, don't close it (or open a new one)."""
        if self.count() < 2:
            return # Don't close the last tab
            
        # Save URL before closing
        browser = self.widget(i)
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
            self.url_changed.emit(browser.url())
            self.title_changed.emit(browser.title())
            
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
