"""
Theme definitions for the Searcher Browser.
"""

def get_dark_theme():
    return """
    QMainWindow {
        background-color: #111315;
    }
    QToolBar {
        background-color: #17191C;
        border-bottom: 1px solid #23272E;
        padding: 8px;
        spacing: 8px;
    }
    QLineEdit {
        background-color: #0E1012;
        color: #E2E8F0;
        border-radius: 18px;
        padding: 8px 18px;
        font-size: 14px;
        border: 1px solid #2A2F38;
    }
    QLineEdit:focus {
        border: 1px solid #38BDF8;
    }
    QTabBar::tab {
        background-color: transparent;
        color: #94A3B8;
        padding: 10px 24px;
        border: none;
        min-width: 120px;
        font-weight: 500;
        border-bottom: 2px solid transparent;
    }
    QTabBar::tab:selected {
        color: #F8FAFC;
        border-bottom: 2px solid #38BDF8;
    }
    QTabBar::tab:hover:!selected {
        background-color: #1C1F26;
        border-radius: 6px;
    }
    QStatusBar {
        background-color: #111315;
        color: #94A3B8;
    }
    QProgressBar {
        border: none;
        border-radius: 2px;
        background-color: #1C1F26;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: #38BDF8;
        border-radius: 2px;
    }
    QDialog {
        background-color: #17191C;
        color: #E2E8F0;
    }
    QLabel {
        color: #E2E8F0;
    }
    QPushButton {
        background-color: #1C1F26;
        color: #E2E8F0;
        border: 1px solid #2A2F38;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: #23272E;
        border: 1px solid #38BDF8;
    }
    QListWidget {
        background-color: #17191C;
        color: #E2E8F0;
        border: 1px solid #2A2F38;
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
