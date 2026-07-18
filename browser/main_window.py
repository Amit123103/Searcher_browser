import os
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QStatusBar, QProgressBar, 
                             QMessageBox, QApplication, QMenu, QDockWidget)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QKeySequence, QShortcut, QAction, QIcon
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

from browser.tabs import BrowserTabWidget
from browser.navigation import NavigationBar
from database.db_manager import DatabaseManager
from browser.settings import SettingsManager, SettingsTab
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
        
        # Set Window Icon
        icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "assets", "logo.png")
        self.setWindowIcon(QIcon(icon_path))
        
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
        
        # Initialize Navigation Bar
        self.nav_bar = NavigationBar(self)
        
        # Top Row for Tabs and Buttons (Chrome-style: tabs on very top)
        from PyQt6.QtWidgets import QToolButton, QPushButton, QHBoxLayout
        from PyQt6.QtGui import QIcon
        
        top_row_widget = QWidget()
        top_row_widget.setObjectName("tabBarRow")
        top_row_widget.setStyleSheet("""
            #tabBarRow {
                background-color: #161b22;
                padding: 0px;
            }
        """)
        top_row_layout = QHBoxLayout(top_row_widget)
        top_row_layout.setContentsMargins(8, 4, 8, 0)
        top_row_layout.setSpacing(4)
        
        # Tab bar takes the main space
        self.tabs.tabBar().setExpanding(False)
        top_row_layout.addWidget(self.tabs.tabBar(), 1)
        
        # Add New Tab button (+)
        self.new_tab_btn = QToolButton(self)
        self.new_tab_btn.setObjectName("newTabBtn")
        self.new_tab_btn.setText("+")
        self.new_tab_btn.setToolTip("Open a new tab")
        self.new_tab_btn.clicked.connect(lambda: self.tabs.add_new_tab())
        top_row_layout.addWidget(self.new_tab_btn)
        
        top_row_layout.addStretch()
        
        # Ask Gemini button (right side, like Chrome)
        self.ask_ai_btn = QPushButton("✨ Ask Gemini", self)
        self.ask_ai_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d1f3d;
                color: #d4b8ff;
                border-radius: 14px;
                padding: 4px 14px;
                font-size: 12px;
                font-weight: 500;
                border: 1px solid #3d2f4d;
            }
            QPushButton:hover {
                background-color: #3d2f4d;
            }
        """)
        self.ask_ai_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ask_ai_btn.clicked.connect(self.toggle_ai_sidebar)
        top_row_layout.addWidget(self.ask_ai_btn)
        
        # Window control buttons (minimize, maximize, close)
        for btn_text, btn_action, btn_style in [
            ("—", lambda: self.showMinimized(), ""),
            ("☐", lambda: self.toggle_maximize(), ""),
            ("✕", lambda: self.close(), "QPushButton:hover { background-color: #e81123; }")
        ]:
            btn = QPushButton(btn_text)
            btn.setFixedSize(32, 28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: #8b949e;
                    border: none;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: #30363d;
                    color: #ffffff;
                }}
                {btn_style}
            """)
            btn.clicked.connect(btn_action)
            top_row_layout.addWidget(btn)
        
        # Add Tabs top row first, then Toolbar
        self.layout.addWidget(top_row_widget)
        self.layout.addWidget(self.nav_bar)
        
        # Add the tab widget content area (the stacked pages)
        self.layout.addWidget(self.tabs)
        
        # (Removed redundant nav_bar creation)
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
        self.ai_sidebar.visibilityChanged.connect(self.nav_bar.ai_btn.setChecked)

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
        # Check if settings tab is already open
        for i in range(self.tabs.count()):
            if getattr(self.tabs.widget(i), 'is_settings_tab', False):
                self.tabs.setCurrentIndex(i)
                return
                
        settings_tab = SettingsTab(self.settings_manager, self)
        settings_tab.is_settings_tab = True
        index = self.tabs.addTab(settings_tab, "Settings")
        self.tabs.setCurrentIndex(index)
            
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

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    # --- AI Features Integration ---
    
    def toggle_ai_sidebar(self, checked=None):
        if checked is None:
            # Toggle: if visible, hide; if hidden, show
            self.ai_sidebar.setVisible(not self.ai_sidebar.isVisible())
        else:
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
                if hasattr(browser, 'url'):
                    try:
                        url_str = browser.url().toString()
                        if url_str and not url_str.startswith("file://") and url_str != "about:blank":
                            saved_session.append(url_str)
                    except Exception:
                        pass
            self.settings_manager.set("saved_session", saved_session)
            
        super().closeEvent(event)
