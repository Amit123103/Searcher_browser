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
        self.back_btn = QToolButton(self)
        self.back_btn.setObjectName("navBackBtn")
        self.back_btn.setToolTip("Go back")
        self.back_btn.clicked.connect(self.navigate_back)
        self.addWidget(self.back_btn)
        
        self.forward_btn = QToolButton(self)
        self.forward_btn.setObjectName("navForwardBtn")
        self.forward_btn.setToolTip("Go forward")
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.addWidget(self.forward_btn)
        
        self.reload_btn = QToolButton(self)
        self.reload_btn.setObjectName("navReloadBtn")
        self.reload_btn.setToolTip("Reload page")
        self.reload_btn.clicked.connect(self.navigate_reload)
        self.addWidget(self.reload_btn)
        
        # 2. Address Bar (Expanding)
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
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
        
        # Spacer before tools
        spacer = QWidget()
        spacer.setFixedWidth(10)
        self.addWidget(spacer)
        
        # 3. Quick Tools
        self.ai_btn = QToolButton(self)
        self.ai_btn.setObjectName("navAiBtn")
        self.ai_btn.setToolTip("Toggle AI Assistant")
        self.ai_btn.setCheckable(True)
        self.ai_btn.clicked.connect(self.toggle_ai_sidebar)
        self.addWidget(self.ai_btn)
        
        self.bookmark_btn = QToolButton(self)
        self.bookmark_btn.setObjectName("navBookmarkBtn")
        self.bookmark_btn.setToolTip("Bookmark current page")
        self.bookmark_btn.clicked.connect(self.bookmark_page)
        self.addWidget(self.bookmark_btn)
        
        # 4. Profile & Menu
        self.profile_btn = QToolButton(self)
        self.profile_btn.setText("P")
        self.profile_btn.setToolTip("Profile")
        self.profile_btn.setStyleSheet("""
            QToolButton {
                background-color: #87ceeb;
                color: #0d1117;
                border-radius: 12px;
                font-weight: bold;
                padding: 4px;
                min-width: 16px;
                min-height: 16px;
            }
        """)
        self.addWidget(self.profile_btn)
        
        self.menu_btn = QToolButton(self)
        self.menu_btn.setObjectName("navMenuBtn")
        self.menu_btn.setToolTip("Customize and control")
        self.menu_btn.clicked.connect(self.show_settings)
        
        self.addWidget(self.menu_btn)

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
