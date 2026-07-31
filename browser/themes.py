"""
Theme definitions for the Searcher Browser.
"""

def get_dark_theme():
    return """
    QMainWindow {
        background-color: #0B0F19;
        color: #F8FAFC;
    }
    
    /* Top Bar / Titlebar Row */
    QWidget#titleBarRow {
        background-color: #0B0F19;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Window Control Dots */
    QPushButton#winControlClose {
        background-color: #FF5F56;
        border: none;
        border-radius: 6px;
        color: transparent;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton#winControlClose:hover {
        background-color: #FF3B30;
        color: #580000;
    }
    
    QPushButton#winControlMin {
        background-color: #FFBD2E;
        border: none;
        border-radius: 6px;
        color: transparent;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton#winControlMin:hover {
        background-color: #FFCC00;
        color: #584000;
    }
    
    QPushButton#winControlMax {
        background-color: #27C93F;
        border: none;
        border-radius: 6px;
        color: transparent;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton#winControlMax:hover {
        background-color: #34C759;
        color: #004000;
    }

    /* Navigation Toolbar */
    QToolBar#navBar {
        background-color: #1E293B;
        border: none;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding: 4px 10px;
        spacing: 6px;
    }

    QToolButton {
        background-color: transparent;
        border: none;
        border-radius: 8px;
        padding: 5px;
        color: #94A3B8;
        min-width: 28px;
        min-height: 28px;
    }
    QToolButton:hover {
        background-color: rgba(255, 255, 255, 0.08);
        color: #F8FAFC;
    }
    QToolButton:pressed {
        background-color: rgba(56, 189, 248, 0.2);
        color: #38BDF8;
    }
    QToolButton:checked {
        background-color: rgba(56, 189, 248, 0.25);
        border: 1px solid rgba(56, 189, 248, 0.4);
    }
    QToolButton:disabled {
        background-color: transparent;
        opacity: 0.3;
    }

    QToolButton#newTabBtn {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        margin-left: 2px;
        min-width: 28px;
        min-height: 28px;
    }
    QToolButton#newTabBtn:hover {
        background-color: rgba(255, 255, 255, 0.12);
    }

    /* URL / Address Bar */
    QLineEdit#urlBar {
        background-color: #0F172A;
        color: #F8FAFC;
        border-radius: 16px;
        padding: 6px 14px;
        font-size: 13px;
        font-family: 'Segoe UI', system-ui, sans-serif;
        border: 1px solid rgba(255, 255, 255, 0.1);
        selection-background-color: #38BDF8;
        selection-color: #0F172A;
    }
    QLineEdit#urlBar:hover {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background-color: #131E36;
    }
    QLineEdit#urlBar:focus {
        background-color: #0F172A;
        border: 1.5px solid #38BDF8;
    }

    /* Completer Popup */
    QAbstractItemView {
        background-color: #0F172A;
        color: #F8FAFC;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        padding: 4px;
        selection-background-color: #1E293B;
        selection-color: #38BDF8;
    }

    /* Tab Bar */
    QTabBar {
        background-color: transparent;
        qproperty-drawBase: 0;
    }
    QTabBar::tab {
        background-color: #0F172A;
        color: #94A3B8;
        padding: 7px 24px 7px 12px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border-bottom-left-radius: 0px;
        border-bottom-right-radius: 0px;
        min-width: 120px;
        max-width: 220px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 3px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background-color: #1E293B;
        color: #F8FAFC;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 1px solid #1E293B;
    }
    QTabBar::tab:hover:!selected {
        background-color: #162035;
        color: #CBD5E1;
    }

    /* Menus & Tooltips */
    QMenu {
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 6px;
    }
    QMenu::item {
        padding: 6px 24px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #38BDF8;
        color: #0F172A;
    }
    QToolTip {
        background-color: #0F172A;
        color: #F8FAFC;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 11px;
    }

    QStatusBar {
        background-color: #0B0F19;
        color: #64748B;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    QProgressBar {
        border: none;
        border-radius: 3px;
        background-color: #1E293B;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: #38BDF8;
        border-radius: 3px;
    }
    """

def get_light_theme():
    return """
    QMainWindow {
        background-color: #E2E8F0;
        color: #0F172A;
    }
    QWidget#titleBarRow {
        background-color: #E2E8F0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    }
    QPushButton#winControlClose {
        background-color: #FF5F56;
        border: none;
        border-radius: 6px;
        color: transparent;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton#winControlClose:hover {
        background-color: #FF3B30;
        color: #580000;
    }
    QPushButton#winControlMin {
        background-color: #FFBD2E;
        border: none;
        border-radius: 6px;
        color: transparent;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton#winControlMin:hover {
        background-color: #FFCC00;
        color: #584000;
    }
    QPushButton#winControlMax {
        background-color: #27C93F;
        border: none;
        border-radius: 6px;
        color: transparent;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton#winControlMax:hover {
        background-color: #34C759;
        color: #004000;
    }
    QToolBar#navBar {
        background-color: #FFFFFF;
        border: none;
        border-bottom: 1px solid #CBD5E1;
        padding: 4px 10px;
        spacing: 6px;
    }
    QToolButton {
        background-color: transparent;
        border: none;
        border-radius: 8px;
        padding: 5px;
        color: #475569;
        min-width: 28px;
        min-height: 28px;
    }
    QToolButton:hover {
        background-color: #F1F5F9;
        color: #0F172A;
    }
    QToolButton:pressed {
        background-color: #E2E8F0;
    }
    QLineEdit#urlBar {
        background-color: #F1F5F9;
        color: #0F172A;
        border-radius: 16px;
        padding: 6px 14px;
        font-size: 13px;
        border: 1px solid #CBD5E1;
    }
    QLineEdit#urlBar:focus {
        background-color: #FFFFFF;
        border: 1.5px solid #0EA5E9;
    }
    QTabBar::tab {
        background-color: #CBD5E1;
        color: #475569;
        padding: 7px 24px 7px 12px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-width: 120px;
        max-width: 220px;
        font-size: 12px;
        margin-right: 3px;
    }
    QTabBar::tab:selected {
        background-color: #FFFFFF;
        color: #0F172A;
        font-weight: 600;
    }
    """

def apply_theme(app, theme_name="dark"):
    if theme_name == "light":
        app.setStyleSheet(get_light_theme())
    else:
        app.setStyleSheet(get_dark_theme())
