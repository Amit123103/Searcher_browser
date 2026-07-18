"""
Theme definitions for the Searcher Browser.
"""

def get_dark_theme():
    return """
    QMainWindow {
        background-color: #0B1220;
    }
    QToolBar {
        background-color: #0B1220;
        border: none;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding: 8px 16px;
        spacing: 12px;
    }
    QToolButton {
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 8px;
        color: #94A3B8;
        qproperty-iconSize: 18px 18px;
    }
    QToolButton:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    QToolButton:disabled {
        background: transparent;
        color: #555555;
    }
    QToolButton#navBackBtn:disabled { qproperty-icon: url(assets/icons/back_black.svg); }
    QToolButton#navForwardBtn:disabled { qproperty-icon: url(assets/icons/forward_black.svg); }
    QToolButton#navBackBtn { qproperty-icon: url(assets/icons/back_white.svg); }
    QToolButton#navForwardBtn { qproperty-icon: url(assets/icons/forward_white.svg); }
    QToolButton#navReloadBtn { qproperty-icon: url(assets/icons/reload_white.svg); }
    QToolButton#navAiBtn { qproperty-icon: url(assets/icons/ai_white.svg); }
    QToolButton#navMobileBtn { qproperty-icon: url(assets/icons/mobile_white.svg); }
    QToolButton#navBookmarkBtn { qproperty-icon: url(assets/icons/star_white.svg); }
    QToolButton#navMenuBtn { qproperty-icon: url(assets/icons/menu_white.svg); }
    
    QToolButton#newTabBtn {
        background: transparent;
        border: none;
        color: #e2e8f0;
        font-size: 20px;
        font-weight: 400;
        padding: 0px 8px;
        margin-top: 8px;
    }
    QToolButton#newTabBtn:hover {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 6px;
    }
    
    QLineEdit {
        background-color: rgba(0, 0, 0, 0.2);
        color: #F8FAFC;
        border-radius: 18px;
        padding: 10px 16px;
        font-size: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin: 0px 16px;
    }
    QLineEdit:focus {
        background-color: rgba(0, 0, 0, 0.4);
        border: 1px solid #3B82F6;
    }
    QTabBar {
        background-color: #0B1220;
    }
    QTabBar::tab {
        background-color: rgba(255, 255, 255, 0.05);
        color: #F8FAFC;
        padding: 8px 28px 8px 16px;
        border-radius: 12px;
        min-width: 100px;
        max-width: 200px;
        font-size: 13px;
        margin-right: 8px;
        border: 1px solid transparent;
        margin-top: 8px;
    }
    QTabBar::tab:selected {
        background-color: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    QTabBar::tab:hover:!selected {
        background-color: rgba(255, 255, 255, 0.1);
    }
    QTabBar::close-button {
        image: url(assets/icons/close_white.svg);
        subcontrol-position: right;
        margin-right: 8px;
        width: 10px;
        height: 10px;
    }
    QTabBar::close-button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
    }
    QStatusBar {
        background-color: #0B1220;
        color: #94A3B8;
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
        qproperty-iconSize: 14px 14px;
    }
    QToolButton:hover {
        background: rgba(0, 0, 0, 0.05);
    }
    QToolButton:disabled {
        background: transparent;
        color: #cccccc;
    }
    QToolButton#navBackBtn:disabled { qproperty-icon: url(assets/icons/back_black.svg); /* would be better if we had grey icon, but we can just use opacity if QSS supported it. Wait, QSS has no opacity. Let's just use the white one for light theme if it looks disabled? No, let's leave the same icon. The icon itself might not fade, but there is no back_grey.svg */ }
    QToolButton#navForwardBtn:disabled { qproperty-icon: url(assets/icons/forward_black.svg); }
    QToolButton#navBackBtn { qproperty-icon: url(assets/icons/back_black.svg); }
    QToolButton#navForwardBtn { qproperty-icon: url(assets/icons/forward_black.svg); }
    QToolButton#navReloadBtn { qproperty-icon: url(assets/icons/reload_black.svg); }
    QToolButton#navAiBtn { qproperty-icon: url(assets/icons/ai_black.svg); }
    QToolButton#navMobileBtn { qproperty-icon: url(assets/icons/mobile_black.svg); }
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
