"""
Theme definitions for the Searcher Browser.
"""

def get_dark_theme():
    return """
    QMainWindow {
        background-color: #2b1b24;
    }
    QToolBar {
        background-color: #3b2333;
        border: none;
        padding: 5px;
        spacing: 5px;
    }
    QToolButton {
        background: transparent;
        border: none;
        border-radius: 6px;
        padding: 6px;
        color: #e2e8f0;
    }
    QToolButton:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    QToolButton#navBackBtn { qproperty-icon: url(assets/icons/back_white.svg); }
    QToolButton#navForwardBtn { qproperty-icon: url(assets/icons/forward_white.svg); }
    QToolButton#navReloadBtn { qproperty-icon: url(assets/icons/reload_white.svg); }
    QToolButton#navAiBtn { qproperty-icon: url(assets/icons/ai_white.svg); }
    QToolButton#navBookmarkBtn { qproperty-icon: url(assets/icons/star_white.svg); }
    QToolButton#navMenuBtn { qproperty-icon: url(assets/icons/menu_white.svg); }
    
    QToolButton#newTabBtn {
        background: transparent;
        border: none;
        color: #e2e8f0;
        font-size: 20px;
        font-weight: 400;
        padding: 0px 8px;
    }
    QToolButton#newTabBtn:hover {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 6px;
    }
    
    QLineEdit {
        background-color: #20141a;
        color: #ffffff;
        border-radius: 18px;
        padding: 8px 16px;
        font-size: 13px;
        border: 1px solid #3b2333;
        margin: 4px 10px;
    }
    QLineEdit:focus {
        border: 1px solid #6b4d5f;
    }
    QTabBar {
        background-color: #2b1b24;
    }
    QTabBar::tab {
        background-color: transparent;
        color: #a997a3;
        padding: 8px 16px;
        border: none;
        min-width: 120px;
        max-width: 200px;
        font-size: 13px;
        font-weight: 500;
        margin-top: 8px;
        border-right: 1px solid #452c3b;
    }
    QTabBar::tab:selected {
        background-color: #3b2333;
        color: #ffffff;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        border-right: none;
    }
    QTabBar::tab:hover:!selected {
        background-color: rgba(255, 255, 255, 0.05);
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
    }
    QStatusBar {
        background-color: #0d1117;
        color: #8b949e;
    }
    QProgressBar {
        border: none;
        border-radius: 2px;
        background-color: #30363d;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: #38bdf8;
        border-radius: 2px;
    }
    QDialog {
        background-color: #0d1117;
        color: #ffffff;
    }
    QLabel {
        color: #ffffff;
    }
    QPushButton {
        background-color: #1e293b;
        color: #ffffff;
        border: 1px solid #30363d;
        padding: 8px 16px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #334155;
        border: 1px solid #0ea5e9;
    }
    QListWidget {
        background-color: #161b22;
        color: #ffffff;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    """

def get_light_theme():
    return """
    QMainWindow {
        background-color: #ffffff;
    }
    QToolBar {
        background-color: #f1f3f4;
        border: none;
        padding: 5px;
        spacing: 5px;
    }
    QToolButton {
        background: transparent;
        border: none;
        border-radius: 6px;
        padding: 6px;
        color: #202124;
    }
    QToolButton:hover {
        background: rgba(0, 0, 0, 0.05);
    }
    QToolButton#navBackBtn { qproperty-icon: url(assets/icons/back_black.svg); }
    QToolButton#navForwardBtn { qproperty-icon: url(assets/icons/forward_black.svg); }
    QToolButton#navReloadBtn { qproperty-icon: url(assets/icons/reload_black.svg); }
    QToolButton#navAiBtn { qproperty-icon: url(assets/icons/ai_black.svg); }
    QToolButton#navBookmarkBtn { qproperty-icon: url(assets/icons/star_black.svg); }
    QToolButton#navMenuBtn { qproperty-icon: url(assets/icons/menu_black.svg); }
    
    QToolButton#newTabBtn {
        background: transparent;
        border: none;
        color: #202124;
        font-size: 20px;
        font-weight: 400;
        padding: 0px 8px;
    }
    QToolButton#newTabBtn:hover {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 6px;
    }
    
    QLineEdit {
        background-color: #ffffff;
        color: #202124;
        border-radius: 15px;
        padding: 5px 15px;
        font-size: 14px;
        border: 1px solid #dfe1e5;
    }
    QTabBar::tab {
        background-color: #dee1e6;
        color: #5f6368;
        padding: 8px 20px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-width: 150px;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #202124;
    }
    QTabBar::close-button {
        image: url(assets/icons/close_black.svg);
    }
    QTabBar::close-button:hover {
        background: rgba(0, 0, 0, 0.05);
        border-radius: 2px;
    }
    QStatusBar {
        background-color: #f1f3f4;
        color: #202124;
    }
    QProgressBar {
        border: 1px solid #dfe1e5;
        border-radius: 3px;
        text-align: center;
        color: #202124;
    }
    QProgressBar::chunk {
        background-color: #1a73e8;
    }
    QDialog {
        background-color: #ffffff;
        color: #202124;
    }
    QLabel {
        color: #202124;
    }
    QPushButton {
        background-color: #f1f3f4;
        color: #202124;
        border: 1px solid #dfe1e5;
        padding: 5px 15px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #e4e7eb;
    }
    QListWidget {
        background-color: #ffffff;
        color: #202124;
        border: 1px solid #dfe1e5;
    }
    """

def apply_theme(app, theme_name):
    """Applies the selected theme to the application."""
    if theme_name.lower() == "light":
        app.setStyleSheet(get_light_theme())
    else:
        app.setStyleSheet(get_dark_theme())
