import os
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QStatusBar, QProgressBar, 
                             QMessageBox, QApplication, QMenu, QDockWidget)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

from browser.tabs import BrowserTabWidget
from browser.navigation import NavigationBar
from database.db_manager import DatabaseManager
from browser.settings import SettingsManager, SettingsDialog
from browser.history import HistoryDialog
from browser.bookmarks import BookmarksDialog
from browser.downloads import DownloadManagerDialog
from browser.themes import apply_theme
from browser.passwords import PasswordManagerDialog
from browser.adblocker import AdBlockerInterceptor
from browser.search_engine import SearchEngineThread

# AI Features
from browser.ai_service import AIService
from browser.ai_sidebar import AISidebar
from browser.voice import VoiceSearchDialog

class MainWindow(QMainWindow):
    """
    Main Window for Searcher Browser.
    Supports Incognito Mode, Ad Blocking, Session Restore, AI Sidebar, Voice Search, and more.
    """
    
    def __init__(self, is_incognito=False):
        super().__init__()
        self.is_incognito = is_incognito
        title_suffix = " (Incognito)" if is_incognito else ""
        self.setWindowTitle(f"Searcher{title_suffix}")
        self.resize(1200, 800)
        
        # Initialize Managers
        self.db_manager = DatabaseManager()
        self.settings_manager = SettingsManager()
        self.ai_service = AIService()
        
        # Profile Setup
        if self.is_incognito:
            self.profile = QWebEngineProfile("incognito", self)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        else:
            self.profile = QWebEngineProfile.defaultProfile()
            
        # Ad Blocker
        self.ad_blocker = AdBlockerInterceptor(self)
        self.profile.setUrlRequestInterceptor(self.ad_blocker)
        
        # Initialize Download Manager
        self.download_manager = DownloadManagerDialog(self)
        self.profile.downloadRequested.connect(self.download_manager.handle_download_requested)
        
        self.setup_ui()
        self.setup_menus()
        self.setup_shortcuts()
        self.apply_current_theme()
        
        # Populate Search Suggestions
        if not self.is_incognito:
            self.nav_bar.update_suggestions(self.db_manager.get_history(200))
            
        # Session Restore
        if not self.is_incognito and self.settings_manager.get("restore_session"):
            saved_session = self.settings_manager.get("saved_session", [])
            if saved_session:
                for url_str in saved_session:
                    self.tabs.add_new_tab(QUrl(url_str))
            else:
                self.load_default_tab()
        else:
            self.load_default_tab()
            
    def load_default_tab(self):
        start_page_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "assets", "start_page.html")
        start_url = QUrl.fromLocalFile(start_page_path)
        self.tabs.add_new_tab(start_url)
        
    def setup_ui(self):
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Initialize Tabs
        self.tabs = BrowserTabWidget(self)
        
        # Override the tabs method to use our specific profile
        original_add_tab = self.tabs.add_new_tab
        def new_add_tab(qurl=None, label="New Tab"):
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            
            page = QWebEnginePage(self.profile, self.tabs)
            browser = QWebEngineView(self.tabs)
            browser.setPage(page)
            
            if qurl is None:
                start_page_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "assets", "start_page.html")
                qurl = QUrl.fromLocalFile(start_page_path)
                
            browser.setUrl(qurl)
            
            browser.urlChanged.connect(lambda url, b=browser: self.tabs.on_url_changed(url, b))
            browser.titleChanged.connect(lambda title, b=browser: self.tabs.on_title_changed(title, b))
            browser.loadProgress.connect(lambda p, b=browser: self.tabs.on_load_progress(p, b))
            browser.loadStarted.connect(lambda b=browser: self.tabs.on_load_started(b))
            browser.loadFinished.connect(lambda ok, b=browser: self.tabs.on_load_finished(ok, b))
            
            i = self.tabs.addTab(browser, label)
            self.tabs.setCurrentIndex(i)
            return browser
            
        self.tabs.add_new_tab = new_add_tab
        
        # Initialize Navigation Bar
        self.nav_bar = NavigationBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.nav_bar)
        
        # Add Tabs to layout
        self.layout.addWidget(self.tabs)
        
        # Initialize Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Connect Signals
        self.tabs.url_changed.connect(self.nav_bar.update_url)
        self.tabs.title_changed.connect(self.update_window_title)
        self.tabs.load_progress.connect(self.update_progress)
        self.tabs.load_started.connect(self.on_load_started)
        self.tabs.load_finished.connect(self.on_load_finished)
        
        # AI Sidebar Setup
        self.ai_sidebar = AISidebar(self.ai_service, self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_sidebar)
        self.ai_sidebar.hide() # Hidden by default
        self.ai_sidebar.visibilityChanged.connect(self.nav_bar.ai_toggle_action.setChecked)

    def setup_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        
        incognito_action = QAction("New Incognito Window", self)
        incognito_action.setShortcut("Ctrl+Shift+N")
        incognito_action.triggered.connect(self.open_incognito)
        file_menu.addAction(incognito_action)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.tabs.add_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(
            lambda: self.tabs.close_tab(self.tabs.currentIndex())
        )
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.nav_bar.url_bar.setFocus)
        QShortcut(QKeySequence("Ctrl+Shift+T"), self).activated.connect(self.tabs.restore_closed_tab)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.show_history)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.bookmark_current_page)
        
    def open_incognito(self):
        self.incognito_window = MainWindow(is_incognito=True)
        self.incognito_window.show()

    def apply_current_theme(self):
        theme = self.settings_manager.get("theme", "dark")
        apply_theme(QApplication.instance(), theme)
        
    def update_window_title(self, title):
        suffix = " (Incognito)" if self.is_incognito else ""
        self.setWindowTitle(f"{title} - Searcher{suffix}")
        
    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        
    def on_load_started(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage("Loading...")
        
    def on_load_finished(self, ok):
        self.progress_bar.setVisible(False)
        browser = self.tabs.current_browser()
        if not browser:
            return
            
        url_str = browser.url().toString()
        
        if ok:
            self.status_bar.showMessage("Done", 2000)
            if not self.is_incognito and not url_str.startswith("file://"):
                title = browser.title()
                self.db_manager.add_history(url_str, title)
                self.nav_bar.update_suggestions(self.db_manager.get_history(200))
        else:
            self.status_bar.showMessage("Error loading page", 3000)
            if url_str.startswith("http"):
                error_page_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "assets", "error_page.html")
                browser.setUrl(QUrl.fromLocalFile(error_page_path))
                
    # --- Feature Dialogs and Actions ---
            
    def show_history(self):
        if self.is_incognito:
            QMessageBox.information(self, "Incognito", "History is disabled in Incognito mode.")
            return
        dialog = HistoryDialog(self.db_manager, self)
        dialog.exec()
        
    def show_bookmarks(self):
        dialog = BookmarksDialog(self.db_manager, self)
        dialog.exec()
        
    def show_downloads(self):
        self.download_manager.show()
        
    def show_passwords(self):
        if self.is_incognito:
            QMessageBox.information(self, "Incognito", "Password Manager is disabled in Incognito mode.")
            return
        dialog = PasswordManagerDialog(self.db_manager, self)
        dialog.exec()
        
    def show_settings(self):
        dialog = SettingsDialog(self.settings_manager, self)
        if dialog.exec():
            self.apply_current_theme()
            
    def bookmark_current_page(self):
        browser = self.tabs.current_browser()
        if not browser:
            return
        url_str = browser.url().toString()
        if url_str.startswith("file://"):
            return 
            
        title = browser.title()
        
        if self.db_manager.add_bookmark(url_str, title):
            self.status_bar.showMessage(f"Bookmarked: {title}", 3000)
        else:
            self.status_bar.showMessage("Already bookmarked or invalid URL", 3000)

    # --- AI Features Integration ---
    
    def toggle_ai_sidebar(self, checked):
        self.ai_sidebar.setVisible(checked)
        
    def get_current_page_text(self, callback):
        """Extracts text from the current webpage to pass to the AI."""
        browser = self.tabs.current_browser()
        if browser:
            browser.page().toPlainText(callback)
        else:
            callback("")
            
    def trigger_voice_search(self):
        dialog = VoiceSearchDialog(self)
        if dialog.exec():
            query = dialog.get_query()
            if query:
                self.perform_search(query)
                
    def perform_search(self, query):
        """Perform a custom search using the built-in meta-search engine."""
        browser = self.tabs.current_browser()
        if not browser:
            # If no browser, create a new tab first
            browser = self.tabs.add_new_tab()
            
        # Show loading screen
        loading_html = f"<html><body style='background:#202124;color:#e8eaed;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;'><h2>Searching for '{query}'...</h2></body></html>"
        # Use a custom scheme to identify it's a searcher internal page
        browser.setHtml(loading_html, QUrl(f"searcher://search?q={query}"))
        self.nav_bar.url_bar.setText(query)
        
        # Start background thread
        self.search_thread = SearchEngineThread(query, self)
        
        # We need to capture the 'browser' instance inside a closure or lambda
        def on_results_ready(html_content):
            browser.setHtml(html_content, QUrl(f"searcher://search?q={query}"))
            
        def on_error(error_msg):
            err_html = f"<html><body style='background:#202124;color:#f28b82;padding:40px;font-family:sans-serif;'><h2>Search Failed</h2><p>{error_msg}</p></body></html>"
            browser.setHtml(err_html, QUrl(f"searcher://search?q={query}"))
            
        self.search_thread.results_ready.connect(on_results_ready, Qt.ConnectionType.QueuedConnection)
        self.search_thread.error_occurred.connect(on_error, Qt.ConnectionType.QueuedConnection)
        self.search_thread.start()
                
    def smart_organize_tabs(self):
        """Uses AI to group and organize open tabs."""
        titles = []
        # Exclude new tab pages or blank pages if desired, but grab them all
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            titles.append(browser.title())
            
        groups = self.ai_service.organize_tabs(titles)
        
        # Visually reorder tabs based on groups
        new_order = []
        for group_name, indices in groups.items():
            new_order.extend(indices)
            
        # Reorder tabs by moving them
        # Note: In a real advanced browser we might use QTabWidget's drag/drop or custom tab grouping visual.
        # Here we just re-insert them. 
        # A simpler way is to prepend the group name to the tab title to show it worked!
        for group_name, indices in groups.items():
            for idx in indices:
                current_text = self.tabs.tabText(idx)
                if "]" not in current_text: # avoid double prepending
                    self.tabs.setTabText(idx, f"[{group_name}] {current_text[:20]}...")
                    
        self.status_bar.showMessage("Tabs organized by AI!", 3000)

    def closeEvent(self, event):
        """Save session on close."""
        if not self.is_incognito:
            saved_session = []
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                url_str = browser.url().toString()
                if url_str and not url_str.startswith("file://") and url_str != "about:blank":
                    saved_session.append(url_str)
            self.settings_manager.set("saved_session", saved_session)
            
        super().closeEvent(event)
