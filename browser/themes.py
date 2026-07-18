"""
Theme definitions for the Searcher Browser.
"""

def get_dark_theme():
    return """
    QMainWindow {
        background-color: #202124;
    }
    QToolBar {
        background-color: #2b2b2b;
        border: none;
        padding: 5px;
        spacing: 5px;
    }
    QLineEdit {
        background-color: #171717;
        color: #e8eaed;
        border-radius: 15px;
        padding: 5px 15px;
        font-size: 14px;
        border: 1px solid #5f6368;
    }
    QTabBar::tab {
        background-color: #202124;
        color: #9aa0a6;
        padding: 8px 20px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-width: 150px;
    }
    QTabBar::tab:selected {
        background-color: #323639;
        color: #e8eaed;
    }
    QStatusBar {
        background-color: #202124;
        color: #e8eaed;
    }
    QProgressBar {
        border: 1px solid #5f6368;
        border-radius: 3px;
        text-align: center;
        color: #e8eaed;
    }
    QProgressBar::chunk {
        background-color: #8ab4f8;
    }
    QDialog {
        background-color: #202124;
        color: #e8eaed;
    }
    QLabel {
        color: #e8eaed;
    }
    QPushButton {
        background-color: #323639;
        color: #e8eaed;
        border: 1px solid #5f6368;
        padding: 5px 15px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #404447;
    }
    QListWidget {
        background-color: #202124;
        color: #e8eaed;
        border: 1px solid #5f6368;
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
