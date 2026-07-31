import os
from PyQt6.QtWidgets import (QToolBar, QLineEdit, QCompleter, QWidget, 
                             QSizePolicy, QToolButton, QMenu)
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem, QIcon, QMouseEvent
from PyQt6.QtCore import Qt, QUrl, QSize

def get_asset_icon(name, theme="dark"):
    suffix = "white" if theme == "dark" else "black"
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icons", f"{name}_{suffix}.svg"))
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()

class ClickableUrlBar(QLineEdit):
    """Custom URL bar that becomes editable when clicked on home page."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_home = False
        self.setObjectName("urlBar")
        
    def mousePressEvent(self, event: QMouseEvent):
        """Make editable when clicked on home page."""
        if self.isReadOnly():
            self.setReadOnly(False)
            self.clear()
            self.setPlaceholderText("Search Google or enter URL...")
            self.setFocus()
        super().mousePressEvent(event)

class NavigationBar(QToolBar):
    """
    Custom Toolbar for browser navigation and actions.
    Features a sleek layout, standard vector icons, and a dropdown menu for tools.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setObjectName("navBar")
        self.setMovable(False)
        self.setIconSize(QSize(18, 18))
        
        self.setup_ui()
        
    def setup_ui(self):
        theme = "dark"
        if hasattr(self.parent_window, "settings_manager"):
            theme = self.parent_window.settings_manager.get("theme", "dark")
            
        # 1. Primary Navigation Actions
        self.back_btn = QToolButton(self)
        self.back_btn.setObjectName("navBackBtn")
        self.back_btn.setToolTip("Go back (Alt+Left)")
        self.back_btn.setIcon(get_asset_icon("back", theme))
        self.back_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.back_btn.clicked.connect(self.navigate_back)
        self.back_btn.setEnabled(False)
        self.addWidget(self.back_btn)
        
        self.forward_btn = QToolButton(self)
        self.forward_btn.setObjectName("navForwardBtn")
        self.forward_btn.setToolTip("Go forward (Alt+Right)")
        self.forward_btn.setIcon(get_asset_icon("forward", theme))
        self.forward_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.forward_btn.setEnabled(False)
        self.addWidget(self.forward_btn)
        
        self.reload_btn = QToolButton(self)
        self.reload_btn.setObjectName("navReloadBtn")
        self.reload_btn.setToolTip("Reload page (F5)")
        self.reload_btn.setIcon(get_asset_icon("reload", theme))
        self.reload_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.reload_btn.clicked.connect(self.navigate_reload)
        self.addWidget(self.reload_btn)
        
        # 2. Address Bar (Expanding)
        self.url_bar = ClickableUrlBar()
        self.url_bar.setPlaceholderText("Search Google or enter URL...")
        self.url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # Add Security Lock Leading Action to URL Bar
        self.url_lock_action = self.url_bar.addAction(get_asset_icon("lock", theme), QLineEdit.ActionPosition.LeadingPosition)
        
        # Setup Completer for Suggestions
        self.completer_model = QStandardItemModel()
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.url_bar.setCompleter(self.completer)
        
        self.addWidget(self.url_bar)
        
        # Quick Tools
        self.ai_btn = QToolButton(self)
        self.ai_btn.setObjectName("navAiBtn")
        self.ai_btn.setToolTip("Toggle AI Assistant")
        self.ai_btn.setIcon(get_asset_icon("ai", theme))
        self.ai_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.ai_btn.setCheckable(True)
        self.ai_btn.clicked.connect(self.toggle_ai_sidebar)
        self.addWidget(self.ai_btn)
        
        self.mobile_btn = QToolButton(self)
        self.mobile_btn.setObjectName("navMobileBtn")
        self.mobile_btn.setToolTip("Toggle Mobile View")
        self.mobile_btn.setIcon(get_asset_icon("mobile", theme))
        self.mobile_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.mobile_btn.setCheckable(True)
        self.mobile_btn.clicked.connect(self.toggle_mobile_view)
        self.addWidget(self.mobile_btn)
        
        self.bookmark_btn = QToolButton(self)
        self.bookmark_btn.setObjectName("navBookmarkBtn")
        self.bookmark_btn.setToolTip("Bookmark this page (Ctrl+D)")
        self.bookmark_btn.setIcon(get_asset_icon("star", theme))
        self.bookmark_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.bookmark_btn.clicked.connect(self.bookmark_page)
        self.addWidget(self.bookmark_btn)
        
        # Menu Button with Dropdown
        self.menu_btn = QToolButton(self)
        self.menu_btn.setObjectName("navMenuBtn")
        self.menu_btn.setToolTip("Menu & Settings")
        self.menu_btn.setIcon(get_asset_icon("menu", theme))
        self.menu_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setup_menu_dropdown()
        self.addWidget(self.menu_btn)

    def setup_menu_dropdown(self):
        menu = QMenu(self)
        
        new_tab_act = QAction("New Tab", self)
        new_tab_act.setShortcut("Ctrl+T")
        new_tab_act.triggered.connect(self.add_new_tab)
        menu.addAction(new_tab_act)
        
        incognito_act = QAction("New Incognito Window", self)
        incognito_act.setShortcut("Ctrl+Shift+N")
        incognito_act.triggered.connect(lambda: self.parent_window.open_incognito() if hasattr(self.parent_window, "open_incognito") else None)
        menu.addAction(incognito_act)
        
        menu.addSeparator()
        
        hist_act = QAction("History", self)
        hist_act.setShortcut("Ctrl+H")
        hist_act.triggered.connect(self.show_history)
        menu.addAction(hist_act)
        
        bm_act = QAction("Bookmarks", self)
        bm_act.triggered.connect(self.show_bookmarks)
        menu.addAction(bm_act)
        
        dl_act = QAction("Downloads", self)
        dl_act.triggered.connect(self.show_downloads)
        menu.addAction(dl_act)
        
        pwd_act = QAction("Passwords", self)
        pwd_act.triggered.connect(self.show_passwords)
        menu.addAction(pwd_act)
        
        menu.addSeparator()
        
        sett_act = QAction("Settings", self)
        sett_act.triggered.connect(self.show_settings)
        menu.addAction(sett_act)
        
        menu.addSeparator()
        
        exit_act = QAction("Exit Searcher", self)
        exit_act.triggered.connect(lambda: self.parent_window.close() if self.parent_window else None)
        menu.addAction(exit_act)
        
        self.menu_btn.setMenu(menu)

    def update_suggestions(self, history_records):
        self.completer_model.clear()
        for url, title, _ in history_records:
            self.completer_model.appendRow(QStandardItem(url))
            if title:
                self.completer_model.appendRow(QStandardItem(title))

    def current_browser(self):
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
        
        if not url_text or url_text == "🏠 Searcher - Home":
            return
        
        # Check if it's a search query
        if " " in url_text or ("." not in url_text and not url_text.startswith(('http://', 'https://'))):
            search_page = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'search_results.html'))
            search_url = QUrl.fromLocalFile(search_page).toString() + f"?q={url_text}"
            url = QUrl(search_url)
            browser.setUrl(url)
        else:
            if not url_text.startswith(('http://', 'https://', 'file://')):
                url_text = "https://" + url_text
            url = QUrl(url_text)
            browser.setUrl(url)
        
    def update_url(self, qurl):
        url_str = qurl.toString()
        theme = "dark"
        if hasattr(self.parent_window, "settings_manager"):
            theme = self.parent_window.settings_manager.get("theme", "dark")
            
        if "start_page.html" in url_str or url_str == "about:blank":
            self.url_bar.setText("🏠 Searcher - Home")
            self.url_bar.setReadOnly(True)
            self.url_bar.is_home = True
            self.url_bar.setCursorPosition(0)
            self.url_lock_action.setIcon(get_asset_icon("search", theme))
        else:
            self.url_bar.setReadOnly(False)
            self.url_bar.is_home = False
            if url_str != "about:blank":
                self.url_bar.setText(url_str)
                self.url_bar.setCursorPosition(0)
            if url_str.startswith("https://"):
                self.url_lock_action.setIcon(get_asset_icon("lock", theme))
            else:
                self.url_lock_action.setIcon(get_asset_icon("search", theme))
