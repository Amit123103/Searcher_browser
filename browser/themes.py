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
    
    /* Window Control Buttons — injected per-platform */
    {WIN_CONTROL_STYLES}

    /* Navigation Toolbar */
    QToolBar#navBar {
        background-color: #1E293B;
        border: none;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0px 4px;
        spacing: 4px;
    }

    QToolBar#navBar QWidget {
        margin: 0px;
    }

    QToolButton {
        background-color: transparent;
        border: none;
        border-radius: 8px;
        padding: 5px;
        color: #94A3B8;
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
    }
    QToolButton#newTabBtn:hover {
        background-color: rgba(255, 255, 255, 0.12);
    }

    /* URL / Address Bar */
    QLineEdit#urlBar {
        background-color: #0F172A;
        color: #F8FAFC;
        border-radius: 14px;
        padding: 4px 14px 4px 6px;
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
        color: #64748B;
        padding: 7px 6px 7px 14px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border-bottom-left-radius: 0px;
        border-bottom-right-radius: 0px;
        min-width: 120px;
        max-width: 220px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 2px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background-color: #1E293B;
        color: #F8FAFC;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-bottom: 2px solid #38BDF8;
    }
    QTabBar::tab:hover:!selected {
        background-color: #131C2E;
        color: #94A3B8;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-bottom: none;
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
    /* Window Control Buttons — injected per-platform */
    {WIN_CONTROL_STYLES}
    QToolBar#navBar {
        background-color: #FFFFFF;
        border: none;
        border-bottom: 1px solid #CBD5E1;
        padding: 0px 4px;
        spacing: 4px;
    }
    QToolButton {
        background-color: transparent;
        border: none;
        border-radius: 8px;
        padding: 5px;
        color: #475569;
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
        border-radius: 14px;
        padding: 4px 14px 4px 6px;
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

def _get_win_control_styles_for_platform(theme_name="dark"):
    """Generate window control button QSS that matches the current OS."""
    import sys
    platform = sys.platform
    
    if platform == 'darwin':
        # macOS Traffic Light Dots
        return """
    QPushButton#winControlClose {
        background-color: #FF5F56;
        border: none;
        border-radius: 7px;
        color: transparent;
        font-weight: bold;
        font-size: 9px;
    }
    QPushButton#winControlClose:hover {
        background-color: #FF3B30;
        color: #4D0000;
    }
    QPushButton#winControlMin {
        background-color: #FFBD2E;
        border: none;
        border-radius: 7px;
        color: transparent;
        font-weight: bold;
        font-size: 9px;
    }
    QPushButton#winControlMin:hover {
        background-color: #FFCC00;
        color: #4D3600;
    }
    QPushButton#winControlMax {
        background-color: #27C93F;
        border: none;
        border-radius: 7px;
        color: transparent;
        font-weight: bold;
        font-size: 9px;
    }
    QPushButton#winControlMax:hover {
        background-color: #34C759;
        color: #003300;
    }
    """
    else:
        # Windows 10/11 & Linux — rectangular Chrome-style buttons
        is_dark = (theme_name == "dark")
        bg = "transparent"
        fg = "#C8CCD0" if is_dark else "#3C4043"
        hover_min_bg = "rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.06)"
        hover_max_bg = "rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.06)"
        hover_close_bg = "#E81123"
        hover_close_fg = "#FFFFFF"
        pressed_close_bg = "#F1707A"
        pressed_min_bg = "rgba(255,255,255,0.12)" if is_dark else "rgba(0,0,0,0.10)"
        
        return f"""
    QPushButton#winControlMin, QPushButton#winControlMax {{
        background-color: {bg};
        border: none;
        border-radius: 0px;
        color: {fg};
        font-size: 11px;
        font-family: 'Segoe MDL2 Assets', 'Segoe UI Symbol', sans-serif;
    }}
    QPushButton#winControlMin:hover {{
        background-color: {hover_min_bg};
    }}
    QPushButton#winControlMin:pressed {{
        background-color: {pressed_min_bg};
    }}
    QPushButton#winControlMax:hover {{
        background-color: {hover_max_bg};
    }}
    QPushButton#winControlMax:pressed {{
        background-color: {pressed_min_bg};
    }}
    QPushButton#winControlClose {{
        background-color: {bg};
        border: none;
        border-radius: 0px;
        color: {fg};
        font-size: 11px;
        font-family: 'Segoe MDL2 Assets', 'Segoe UI Symbol', sans-serif;
    }}
    QPushButton#winControlClose:hover {{
        background-color: {hover_close_bg};
        color: {hover_close_fg};
    }}
    QPushButton#winControlClose:pressed {{
        background-color: {pressed_close_bg};
        color: {hover_close_fg};
    }}
    """

def apply_theme(app, theme_name="dark"):
    win_styles = _get_win_control_styles_for_platform(theme_name)
    if theme_name == "light":
        stylesheet = get_light_theme().replace("{WIN_CONTROL_STYLES}", win_styles)
    else:
        stylesheet = get_dark_theme().replace("{WIN_CONTROL_STYLES}", win_styles)
    app.setStyleSheet(stylesheet)
