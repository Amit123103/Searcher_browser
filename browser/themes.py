"""
Theme definitions for the Searcher Browser.
"""

def get_dark_theme():
    return """
    QMainWindow {
        background-color: #121417;
    }
    QToolBar {
        background-color: #121417;
        border-bottom: 1px solid #2a2a2a;
        padding: 5px;
        spacing: 5px;
    }
    QToolButton {
        background: transparent;
        border: none;
        border-radius: 4px;
        padding: 6px;
        color: #e8eaed;
    }
    QToolButton:hover {
        background: #2a2a2a;
    }
    QLineEdit {
        background-color: #1a1c1e;
        color: #ffffff;
        border-radius: 16px;
        padding: 8px 16px;
        font-size: 13px;
        border: 1px solid #2a2a2a;
        margin: 4px 10px;
    }
    QLineEdit:focus {
        border: 1px solid #38bdf8;
    }
    QTabBar {
        background-color: #121417;
    }
    QTabBar::tab {
        background-color: transparent;
        color: #9ca3af;
        padding: 10px 20px;
        border: none;
        min-width: 120px;
        font-size: 13px;
        border-bottom: 2px solid transparent;
    }
    QTabBar::tab:selected {
        color: #ffffff;
        border-bottom: 2px solid #38bdf8;
    }
    QTabBar::tab:hover:!selected {
        background-color: #1c1e22;
        border-radius: 6px;
    }
    QStatusBar {
        background-color: #121417;
        color: #9ca3af;
    }
    QProgressBar {
        border: none;
        border-radius: 2px;
        background-color: #252525;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: #38bdf8;
        border-radius: 2px;
    }
    QDialog {
        background-color: #121417;
        color: #ffffff;
    }
    QLabel {
        color: #ffffff;
    }
    QPushButton {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #333333;
        padding: 8px 16px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #333333;
        border: 1px solid #00d2ff;
    }
    QListWidget {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #333333;
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
