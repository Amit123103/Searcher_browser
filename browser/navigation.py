import os
from PyQt6.QtWidgets import (QToolBar, QLineEdit, QCompleter, QWidget, 
                             QSizePolicy, QToolButton, QMenu)
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QMouseEvent

class ClickableUrlBar(QLineEdit):
    """Custom URL bar that becomes editable when clicked on home page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_home = False
        
    def mousePressEvent(self, event: QMouseEvent):
        """Make editable when clicked on home page."""
        if self.isReadOnly():
            self.setReadOnly(False)
            self.clear()
            self.setPlaceholderText("Search or type URL...")
            self.setFocus()
        super().mousePressEvent(event)

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
        self.back_btn.setToolTip("Go back (Alt+Left)")
        self.back_btn.setText("←")
        self.back_btn.clicked.connect(self.navigate_back)
        self.back_btn.setEnabled(False)
        self.addWidget(self.back_btn)
        
        self.forward_btn = QToolButton(self)
        self.forward_btn.setObjectName("navForwardBtn")
        self.forward_btn.setToolTip("Go forward (Alt+Right)")
        self.forward_btn.setText("→")
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.forward_btn.setEnabled(False)
        self.addWidget(self.forward_btn)
        
        self.reload_btn = QToolButton(self)
        self.reload_btn.setObjectName("navReloadBtn")
        self.reload_btn.setToolTip("Reload page")
        self.reload_btn.clicked.connect(self.navigate_reload)
        self.addWidget(self.reload_btn)
        
        # 2. Address Bar (Expanding)
        self.url_bar = ClickableUrlBar()
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
        
        self.mobile_btn = QToolButton(self)
        self.mobile_btn.setObjectName("navMobileBtn")
        self.mobile_btn.setToolTip("Toggle Mobile View")
        self.mobile_btn.setCheckable(True)
        self.mobile_btn.clicked.connect(self.toggle_mobile_view)
        self.addWidget(self.mobile_btn)
        
        self.bookmark_btn = QToolButton(self)
        self.bookmark_btn.setObjectName("navBookmarkBtn")
        self.bookmark_btn.setToolTip("Bookmark current page")
        self.bookmark_btn.clicked.connect(self.bookmark_page)
        self.addWidget(self.bookmark_btn)
        
        # 4. Menu
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
            try:
                if hasattr(browser, 'page') and hasattr(browser.page(), 'history'):
                    if browser.page().history().canGoBack():
                        browser.page().history().back()
                        return
                if hasattr(browser, 'back'):
                    browser.back()
            except Exception as e:
                print(f"Back navigation error: {e}")
            
    def navigate_forward(self):
        browser = self.current_browser()
        if browser:
            try:
                if hasattr(browser, 'page') and hasattr(browser.page(), 'history'):
                    if browser.page().history().canGoForward():
                        browser.page().history().forward()
                        return
                if hasattr(browser, 'forward'):
                    browser.forward()
            except Exception as e:
                print(f"Forward navigation error: {e}")
            
    def navigate_reload(self):
        browser = self.current_browser()
        if browser and hasattr(browser, 'reload'):
            browser.reload()
    
    def update_navigation_buttons(self):
        """Update back/forward button states based on current browser history."""
        browser = self.current_browser()
        if browser:
            try:
                if hasattr(browser, 'page') and hasattr(browser.page(), 'history'):
                    history = browser.page().history()
                    self.back_btn.setEnabled(history.canGoBack())
                    self.forward_btn.setEnabled(history.canGoForward())
                else:
                    self.back_btn.setEnabled(False)
                    self.forward_btn.setEnabled(False)
            except Exception as e:
                print(f"Error updating navigation buttons: {e}")
                self.back_btn.setEnabled(False)
                self.forward_btn.setEnabled(False)
        else:
            self.back_btn.setEnabled(False)
            self.forward_btn.setEnabled(False)
            
    def navigate_home(self):
        browser = self.current_browser()
        if browser and hasattr(browser, 'setUrl'):
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
            
    def toggle_mobile_view(self, checked):
        if hasattr(self.parent_window, 'toggle_mobile_view'):
            self.parent_window.toggle_mobile_view(checked)
            
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
        
        # Check if it's a search query (no domain indicators)
        if " " in url_text or ("." not in url_text and not url_text.startswith(('http://', 'https://'))):
            # Redirect to custom Searcher search results page
            import os
            search_page = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'search_results.html'))
            search_url = QUrl.fromLocalFile(search_page).toString() + f"?q={url_text}"
            url = QUrl(search_url)
            browser.setUrl(url)
        else:
            # It's a URL
            if not url_text.startswith(('http://', 'https://', 'file://')):
                url_text = "https://" + url_text
            url = QUrl(url_text)
            browser.setUrl(url)
        
    def update_url(self, qurl):
        url_str = qurl.toString()
        
        # Hide file path for start page - show friendly text instead
        if "start_page.html" in url_str or url_str == "about:blank":
            self.url_bar.setText("🏠 Searcher - Home")
            self.url_bar.setReadOnly(True)
            self.url_bar.is_home = True
            self.url_bar.setCursorPosition(0)
        else:
            self.url_bar.setReadOnly(False)
            self.url_bar.is_home = False
            if url_str != "about:blank":
                self.url_bar.setText(url_str)
                self.url_bar.setCursorPosition(0)
