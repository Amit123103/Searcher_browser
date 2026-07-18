from PyQt6.QtWidgets import QToolBar, QLineEdit, QCompleter
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QUrl

class NavigationBar(QToolBar):
    """
    Main Navigation Toolbar for Searcher Browser.
    Provides buttons for basic navigation and an address bar for URLs and searches.
    """
    
    def __init__(self, parent=None):
        super().__init__("Navigation", parent)
        self.setMovable(False) # Lock toolbar in place
        self.parent_window = parent
        
        self.setup_ui()
        
    def setup_ui(self):
        # Back Action
        self.back_action = QAction("Back", self)
        self.back_action.setStatusTip("Go back to previous page")
        self.back_action.triggered.connect(self.navigate_back)
        self.addAction(self.back_action)
        
        # Forward Action
        self.forward_action = QAction("Forward", self)
        self.forward_action.setStatusTip("Go forward to next page")
        self.forward_action.triggered.connect(self.navigate_forward)
        self.addAction(self.forward_action)
        
        # Reload Action
        self.reload_action = QAction("Refresh", self)
        self.reload_action.setStatusTip("Reload current page")
        self.reload_action.triggered.connect(self.navigate_reload)
        self.addAction(self.reload_action)
        
        # Home Action
        self.home_action = QAction("Home", self)
        self.home_action.setStatusTip("Go to home page")
        self.home_action.triggered.connect(self.navigate_home)
        self.addAction(self.home_action)
        
        self.addSeparator()
        
        # Address Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search with Google or enter address")
        self.url_bar.setStyleSheet("padding: 5px; border-radius: 15px; border: 1px solid #ccc;")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # Setup Completer for Suggestions
        self.completer_model = QStandardItemModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.url_bar.setCompleter(self.completer)
        
        self.addWidget(self.url_bar)
        
        # Voice Search Action
        self.voice_action = QAction("🎤", self)
        self.voice_action.setStatusTip("Voice Search")
        self.voice_action.triggered.connect(self.trigger_voice_search)
        self.addAction(self.voice_action)
        
        self.addSeparator()
        
        # New Tab Action
        self.new_tab_action = QAction("New Tab", self)
        self.new_tab_action.setStatusTip("Open a new tab")
        self.new_tab_action.triggered.connect(self.add_new_tab)
        self.addAction(self.new_tab_action)
        
        self.addSeparator()
        
        # Bookmark Action
        self.bookmark_action = QAction("Bookmark", self)
        self.bookmark_action.setStatusTip("Bookmark current page")
        self.bookmark_action.triggered.connect(self.bookmark_page)
        self.addAction(self.bookmark_action)
        
        # AI Assistant Toggle
        self.ai_toggle_action = QAction("AI Assistant", self)
        self.ai_toggle_action.setStatusTip("Toggle AI Sidebar")
        self.ai_toggle_action.setCheckable(True)
        self.ai_toggle_action.triggered.connect(self.toggle_ai_sidebar)
        self.addAction(self.ai_toggle_action)
        
        self.addSeparator()
        
        # History Action
        self.history_action = QAction("History", self)
        self.history_action.setStatusTip("View browsing history")
        self.history_action.triggered.connect(self.show_history)
        self.addAction(self.history_action)
        
        # Bookmarks Manager Action
        self.bookmarks_mgr_action = QAction("Bookmarks", self)
        self.bookmarks_mgr_action.setStatusTip("View bookmarks")
        self.bookmarks_mgr_action.triggered.connect(self.show_bookmarks)
        self.addAction(self.bookmarks_mgr_action)
        
        # Downloads Action
        self.downloads_action = QAction("Downloads", self)
        self.downloads_action.setStatusTip("View downloads")
        self.downloads_action.triggered.connect(self.show_downloads)
        self.addAction(self.downloads_action)
        
        # Passwords Action
        self.passwords_action = QAction("Passwords", self)
        self.passwords_action.setStatusTip("Manage saved passwords")
        self.passwords_action.triggered.connect(self.show_passwords)
        self.addAction(self.passwords_action)
        
        # Settings Action
        self.settings_action = QAction("Settings", self)
        self.settings_action.setStatusTip("Browser settings")
        self.settings_action.triggered.connect(self.show_settings)
        self.addAction(self.settings_action)

    def update_suggestions(self, history_records):
        self.completer_model.clear()
        # Add history records to completer
        for url, title, _ in history_records:
            self.completer_model.appendRow(QStandardItem(url))
            if title:
                self.completer_model.appendRow(QStandardItem(title))

    def current_browser(self):
        """Helper to get the current web view from the parent window's tabs."""
        if hasattr(self.parent_window, 'tabs'):
            return self.parent_window.tabs.current_browser()
        return None
        
    def navigate_back(self):
        browser = self.current_browser()
        if browser:
            browser.back()
            
    def navigate_forward(self):
        browser = self.current_browser()
        if browser:
            browser.forward()
            
    def navigate_reload(self):
        browser = self.current_browser()
        if browser:
            browser.reload()
            
    def navigate_home(self):
        browser = self.current_browser()
        if browser:
            # Phase 1: Hardcoded Google home
            browser.setUrl(QUrl("https://www.google.com"))
            
    def add_new_tab(self):
        if hasattr(self.parent_window, 'tabs'):
            self.parent_window.tabs.add_new_tab()
            
    def bookmark_page(self):
        if hasattr(self.parent_window, 'bookmark_current_page'):
            self.parent_window.bookmark_current_page()
            
    def show_history(self):
        if hasattr(self.parent_window, 'show_history'):
            self.parent_window.show_history()
            
    def show_bookmarks(self):
        if hasattr(self.parent_window, 'show_bookmarks'):
            self.parent_window.show_bookmarks()
            
    def show_downloads(self):
        if hasattr(self.parent_window, 'show_downloads'):
            self.parent_window.show_downloads()
            
    def show_passwords(self):
        if hasattr(self.parent_window, 'show_passwords'):
            self.parent_window.show_passwords()
            
    def show_settings(self):
        if hasattr(self.parent_window, 'show_settings'):
            self.parent_window.show_settings()
            
    def toggle_ai_sidebar(self, checked):
        if hasattr(self.parent_window, 'toggle_ai_sidebar'):
            self.parent_window.toggle_ai_sidebar(checked)
            
    def trigger_voice_search(self):
        if hasattr(self.parent_window, 'trigger_voice_search'):
            self.parent_window.trigger_voice_search()

    def navigate_to_url(self):
        browser = self.current_browser()
        if not browser:
            return
            
        url_text = self.url_bar.text().strip()
        
        if not url_text:
            return
            
        # Basic heuristic to distinguish search vs URL:
        # If it has spaces or doesn't have a dot, we treat it as a search
        if " " in url_text or "." not in url_text:
            url = QUrl(f"https://www.google.com/search?q={url_text}")
        else:
            if not url_text.startswith(('http://', 'https://', 'file://')):
                url_text = "https://" + url_text
            url = QUrl(url_text)
            
        browser.setUrl(url)
        
    def update_url(self, qurl):
        """Called when the active tab's URL changes to update the address bar."""
        # Only update if it's a valid http/https URL (ignore about:blank etc if needed)
        url_str = qurl.toString()
        if url_str != "about:blank":
            self.url_bar.setText(url_str)
            self.url_bar.setCursorPosition(0)
