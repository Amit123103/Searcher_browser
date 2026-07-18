import os
from PyQt6.QtWidgets import (QToolBar, QLineEdit, QCompleter, QWidget, 
                             QSizePolicy, QToolButton, QMenu)
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import Qt, QUrl

class NavigationBar(QToolBar):
    """
    Custom Toolbar for browser navigation and actions.
    Features a sleek layout, standard icons, and a dropdown menu for tools.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setMovable(False)
        # Styles are handled by the global theme in themes.py
        
        self.setup_ui()
        
    def setup_ui(self):
        style = self.style()
        
        # 1. Primary Navigation Actions
        self.back_action = QAction(style.standardIcon(style.StandardPixmap.SP_ArrowBack), "Back", self)
        self.back_action.setToolTip("Go back")
        self.back_action.triggered.connect(self.navigate_back)
        self.addAction(self.back_action)
        
        self.forward_action = QAction(style.standardIcon(style.StandardPixmap.SP_ArrowForward), "Forward", self)
        self.forward_action.setToolTip("Go forward")
        self.forward_action.triggered.connect(self.navigate_forward)
        self.addAction(self.forward_action)
        
        self.reload_action = QAction(style.standardIcon(style.StandardPixmap.SP_BrowserReload), "Refresh", self)
        self.reload_action.setToolTip("Reload page")
        self.reload_action.triggered.connect(self.navigate_reload)
        self.addAction(self.reload_action)
        
        self.home_action = QAction(style.standardIcon(style.StandardPixmap.SP_DirHomeIcon), "Home", self)
        self.home_action.setToolTip("Go to home")
        self.home_action.triggered.connect(self.navigate_home)
        self.addAction(self.home_action)
        
        # 2. Address Bar (Expanding)
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search with Google or enter address")
        self.url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # Setup Completer for Suggestions
        self.completer_model = QStandardItemModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.url_bar.setCompleter(self.completer)
        
        self.addWidget(self.url_bar)
        
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        
        # Voice Search Action
        self.voice_action = QAction(QIcon(os.path.join(assets_dir, 'mic.svg')), "Voice", self)
        self.voice_action.setToolTip("Voice Search")
        self.voice_action.triggered.connect(self.trigger_voice_search)
        self.addAction(self.voice_action)
        
        # Spacer before tools
        spacer = QWidget()
        spacer.setFixedWidth(10)
        self.addWidget(spacer)
        
        # 3. Quick Tools
        self.new_tab_action = QAction(QIcon(os.path.join(assets_dir, 'add.svg')), "New Tab", self)
        self.new_tab_action.setToolTip("New Tab")
        self.new_tab_action.triggered.connect(self.add_new_tab)
        self.addAction(self.new_tab_action)
        
        self.bookmark_action = QAction(QIcon(os.path.join(assets_dir, 'star.svg')), "Bookmark", self)
        self.bookmark_action.setToolTip("Bookmark current page")
        self.bookmark_action.triggered.connect(self.bookmark_page)
        self.addAction(self.bookmark_action)
        
        self.ai_toggle_action = QAction(QIcon(os.path.join(assets_dir, 'ai.svg')), "AI Assistant", self)
        self.ai_toggle_action.setToolTip("Toggle AI Assistant")
        self.ai_toggle_action.setCheckable(True)
        self.ai_toggle_action.triggered.connect(self.toggle_ai_sidebar)
        self.addAction(self.ai_toggle_action)
        
        # 4. Settings & More Menu
        menu_btn = QToolButton(self)
        menu_btn.setIcon(QIcon(os.path.join(assets_dir, 'menu.svg')))
        menu_btn.setToolTip("Customize and control")
        menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        main_menu = QMenu(self)
        
        history_action = QAction("History", self)
        history_action.triggered.connect(self.show_history)
        main_menu.addAction(history_action)
        
        bookmarks_mgr_action = QAction("Bookmarks", self)
        bookmarks_mgr_action.triggered.connect(self.show_bookmarks)
        main_menu.addAction(bookmarks_mgr_action)
        
        downloads_action = QAction("Downloads", self)
        downloads_action.triggered.connect(self.show_downloads)
        main_menu.addAction(downloads_action)
        
        passwords_action = QAction("Passwords", self)
        passwords_action.triggered.connect(self.show_passwords)
        main_menu.addAction(passwords_action)
        
        main_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        main_menu.addAction(settings_action)
        
        menu_btn.setMenu(main_menu)
        self.addWidget(menu_btn)

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
            
        if " " in url_text or "." not in url_text:
            if hasattr(self.parent_window, 'perform_search'):
                self.parent_window.perform_search(url_text)
            else:
                url = QUrl(f"https://www.google.com/search?q={url_text}")
                browser.setUrl(url)
        else:
            if not url_text.startswith(('http://', 'https://', 'file://')):
                url_text = "https://" + url_text
            url = QUrl(url_text)
            browser.setUrl(url)
        
    def update_url(self, qurl):
        url_str = qurl.toString()
        if url_str != "about:blank":
            self.url_bar.setText(url_str)
            self.url_bar.setCursorPosition(0)
