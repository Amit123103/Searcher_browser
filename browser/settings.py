import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, QWidget)
from PyQt6.QtCore import Qt

class SettingsManager:
    """Manages application settings stored in a JSON file."""
    
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.settings = {
            "theme": "dark",
            "default_search_engine": "https://www.google.com/search?q=",
            "restore_session": True,
            "saved_session": []
        }
        self.load_settings()
        
    def load_settings(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.settings.update(json.load(f))
            else:
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get(self, key, default=None):
        return self.settings.get(key, default)
        
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()


class SettingsTab(QWidget):
    """Settings UI for users to modify browser settings."""
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.main_window = parent
        self.setWindowTitle("Settings")
        self.setObjectName("SettingsTab")
        
        self.setStyleSheet("""
            SettingsTab {
                background-color: #ffffff;
            }
            QScrollArea {
                background-color: #ffffff;
                border: none;
            }
            QWidget#Sidebar {
                background-color: #4b5563;
                color: #e5e7eb;
            }
            QLabel#SidebarLogo {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding-top: 20px;
                padding-left: 20px;
            }
            QLabel#SidebarLogoSub {
                color: #9ca3af;
                font-size: 11px;
                padding-left: 20px;
                margin-bottom: 20px;
            }
            QPushButton#NewWorkspaceBtn {
                background-color: #0ea5e9;
                color: #ffffff;
                border: none;
                border-radius: 18px;
                padding: 10px;
                font-weight: 600;
                margin: 0 20px 20px 20px;
            }
            QLabel#SettingsCategory {
                color: #9ca3af;
                font-size: 11px;
                font-weight: 600;
                padding-left: 20px;
                margin-bottom: 5px;
            }
            QListWidget#SidebarList {
                background-color: transparent;
                border: none;
                color: #e5e7eb;
                font-size: 13px;
                outline: none;
            }
            QListWidget#SidebarList::item {
                padding: 12px 20px;
                border-radius: 8px;
                margin: 2px 10px;
            }
            QListWidget#SidebarList::item:selected {
                background-color: rgba(0, 0, 0, 0.15);
                color: #38bdf8;
            }
            QListWidget#SidebarList::item:hover:!selected {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QLabel#SidebarFooter {
                color: #9ca3af;
                font-size: 12px;
                padding: 20px;
                line-height: 2;
            }
            
            /* Main Content */
            QWidget#MainContent {
                background-color: #ffffff;
            }
            QLabel#PageTitle {
                font-size: 36px;
                font-weight: bold;
                color: #bae6fd;
            }
            QLabel#PageSubtitle {
                font-size: 15px;
                color: #94a3b8;
                margin-bottom: 30px;
            }
            
            /* Cards */
            QFrame.SettingsCard {
                background-color: #64748b;
                border-radius: 24px;
                padding: 24px;
            }
            QLabel.CardTitle {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 16px;
            }
            QFrame.InnerCard {
                background-color: #475569;
                border-radius: 16px;
                padding: 16px;
                margin-top: 12px;
            }
            QLabel.InnerTitle {
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
            }
            QLabel.InnerSub {
                color: #cbd5e1;
                font-size: 12px;
                margin-top: 4px;
            }
            
            /* Toggle Buttons for Theme */
            QPushButton.ToggleBtn {
                background-color: #1e293b;
                border-radius: 12px;
                padding: 4px;
                border: none;
            }
            QPushButton.ToggleActive {
                background-color: #0ea5e9;
                color: #ffffff;
                border-radius: 10px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 500;
                border: none;
            }
            QPushButton.ToggleInactive {
                background-color: transparent;
                color: #94a3b8;
                border-radius: 10px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 500;
                border: none;
            }
            
            /* User Card */
            QFrame#UserCard {
                background-color: #64748b;
                border-radius: 24px;
                padding: 24px;
            }
            QLabel#UserName {
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
                margin-top: 12px;
            }
            QLabel#UserEmail {
                font-size: 13px;
                color: #cbd5e1;
                margin-bottom: 20px;
            }
            QPushButton#ManageAccountBtn {
                background-color: #334155;
                color: #ffffff;
                border-radius: 14px;
                padding: 12px;
                border: none;
                font-weight: 500;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_container = QWidget()
        logo_lay = QHBoxLayout(logo_container)
        logo_lay.setContentsMargins(20, 20, 20, 0)
        logo_lay.setSpacing(10)
        
        logo_img = QLabel()
        from PyQt6.QtGui import QPixmap
        import os
        icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "assets", "logo.png")
        pixmap = QPixmap(icon_path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_img.setPixmap(pixmap)
        
        logo_label = QLabel("Searcher")
        logo_label.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
        
        logo_lay.addWidget(logo_img)
        logo_lay.addWidget(logo_label)
        logo_lay.addStretch()
        logo_sub = QLabel("AI-First Browsing")
        logo_sub.setObjectName("SidebarLogoSub")
        
        new_ws_btn = QPushButton("+ New Workspace")
        new_ws_btn.setObjectName("NewWorkspaceBtn")
        
        category_lbl = QLabel("Settings")
        category_lbl.setObjectName("SettingsCategory")
        
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("SidebarList")
        
        items = ["General", "Appearance", "AI Preferences", "Privacy & Security", "Sync"]
        for item_text in items:
            item = QListWidgetItem(item_text)
            self.nav_list.addItem(item)
        self.nav_list.setCurrentRow(1)
        
        sidebar_layout.addWidget(logo_container)
        sidebar_layout.addWidget(logo_sub)
        sidebar_layout.addWidget(new_ws_btn)
        sidebar_layout.addWidget(category_lbl)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()
        
        footer_label = QLabel("Privacy\nSecurity\n\n© 2024 Searcher AI. Encrypted Connection.")
        footer_label.setObjectName("SidebarFooter")
        sidebar_layout.addWidget(footer_label)
        
        main_layout.addWidget(sidebar)
        
        # --- Main Content ---
        content_container = QWidget()
        content_container.setObjectName("MainContent")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(60, 40, 60, 40)
        
        header_title = QLabel("Settings")
        header_title.setObjectName("PageTitle")
        header_subtitle = QLabel("Customize your Searcher experience and manage your preferences.")
        header_subtitle.setObjectName("PageSubtitle")
        
        content_layout.addWidget(header_title)
        content_layout.addWidget(header_subtitle)
        
        from PyQt6.QtWidgets import QStackedWidget
        self.stacked_pages = QStackedWidget()
        
        def create_page(layout_content):
            page = QWidget()
            page_lay = QVBoxLayout(page)
            page_lay.setContentsMargins(0, 20, 0, 0)
            page_lay.addLayout(layout_content)
            page_lay.addStretch()
            return page

        # ==========================================
        # 0. General Page
        # ==========================================
        gen_lay = QVBoxLayout()
        from PyQt6.QtWidgets import QFrame
        user_card = QFrame()
        user_card.setProperty("class", "SettingsCard")
        user_layout = QVBoxLayout(user_card)
        user_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        avatar = QLabel()
        avatar.setFixedSize(80, 80)
        avatar.setStyleSheet("background-color: #1e293b; border-radius: 40px; margin-top: 10px;")
        
        uname = QLabel("Alex Nova")
        uname.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 12px;")
        uname.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        umail = QLabel("alex.nova@searcher.ai")
        umail.setStyleSheet("font-size: 13px; color: #cbd5e1; margin-bottom: 20px;")
        umail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        manage_btn = QPushButton("Manage Account")
        manage_btn.setStyleSheet("background-color: #334155; color: #ffffff; border-radius: 14px; padding: 12px; border: none; font-weight: 500;")
        
        user_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        user_layout.addWidget(uname)
        user_layout.addWidget(umail)
        user_layout.addWidget(manage_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        gen_lay.addWidget(user_card)

        # ==========================================
        # 1. Appearance Page
        # ==========================================
        app_lay = QVBoxLayout()
        app_lay.setSpacing(24)
        
        app_card = QFrame()
        app_card.setProperty("class", "SettingsCard")
        app_card_layout = QVBoxLayout(app_card)
        
        app_title = QLabel("🎨 Appearance")
        app_title.setProperty("class", "CardTitle")
        app_card_layout.addWidget(app_title)
        
        theme_inner = QFrame()
        theme_inner.setProperty("class", "InnerCard")
        theme_inner_lay = QHBoxLayout(theme_inner)
        
        theme_labels = QVBoxLayout()
        theme_lbl = QLabel("Color Theme")
        theme_lbl.setProperty("class", "InnerTitle")
        theme_sub = QLabel("Choose between Light and Dark mode.")
        theme_sub.setProperty("class", "InnerSub")
        theme_labels.addWidget(theme_lbl)
        theme_labels.addWidget(theme_sub)
        
        theme_toggle_bg = QWidget()
        theme_toggle_bg.setStyleSheet("background-color: #1e293b; border-radius: 12px; padding: 2px;")
        tt_lay = QHBoxLayout(theme_toggle_bg)
        tt_lay.setContentsMargins(2,2,2,2)
        tt_lay.setSpacing(0)
        
        self.btn_light = QPushButton("Light")
        self.btn_dark = QPushButton("Dark")
        
        current_theme = self.settings_manager.get("theme", "dark")
        if current_theme == "light":
            self.btn_light.setProperty("class", "ToggleActive")
            self.btn_dark.setProperty("class", "ToggleInactive")
        else:
            self.btn_light.setProperty("class", "ToggleInactive")
            self.btn_dark.setProperty("class", "ToggleActive")
            
        self.btn_light.clicked.connect(lambda: self.toggle_theme("light"))
        self.btn_dark.clicked.connect(lambda: self.toggle_theme("dark"))
            
        tt_lay.addWidget(self.btn_light)
        tt_lay.addWidget(self.btn_dark)
        
        theme_inner_lay.addLayout(theme_labels)
        theme_inner_lay.addWidget(theme_toggle_bg)
        app_card_layout.addWidget(theme_inner)
        
        typo_inner = QFrame()
        typo_inner.setProperty("class", "InnerCard")
        typo_lay = QVBoxLayout(typo_inner)
        typo_lbl = QLabel("Typography")
        typo_lbl.setProperty("class", "InnerTitle")
        typo_lay.addWidget(typo_lbl)
        
        fonts_lay = QHBoxLayout()
        self.btn_inter = QPushButton("Inter\n\nAa")
        self.btn_poppins = QPushButton("Poppins\n\nAa")
        
        active_font_style = "border: 1px solid #38bdf8; border-radius: 12px; padding: 12px; color: #fff; background-color: #1e293b; text-align: left;"
        inactive_font_style = "border: 1px solid #334155; border-radius: 12px; padding: 12px; color: #fff; background-color: transparent; text-align: left;"
        
        current_font = self.settings_manager.get("typography", "Inter")
        self.btn_inter.setStyleSheet(active_font_style if current_font == "Inter" else inactive_font_style)
        self.btn_poppins.setStyleSheet(active_font_style if current_font == "Poppins" else inactive_font_style)
        
        self.btn_inter.clicked.connect(lambda: self.toggle_typography("Inter"))
        self.btn_poppins.clicked.connect(lambda: self.toggle_typography("Poppins"))
        
        fonts_lay.addWidget(self.btn_inter)
        fonts_lay.addWidget(self.btn_poppins)
        typo_lay.addLayout(fonts_lay)
        
        app_card_layout.addWidget(typo_inner)
        app_lay.addWidget(app_card)

        # ==========================================
        # 2. AI Preferences Page
        # ==========================================
        ai_lay = QVBoxLayout()
        ai_card = QFrame()
        ai_card.setProperty("class", "SettingsCard")
        ai_layout = QVBoxLayout(ai_card)
        
        ai_title = QLabel("✨ AI Preferences")
        ai_title.setProperty("class", "CardTitle")
        ai_layout.addWidget(ai_title)
        
        insight_inner = QFrame()
        insight_inner.setProperty("class", "InnerCard")
        ins_lay = QHBoxLayout(insight_inner)
        ins_labels = QVBoxLayout()
        ins_l1 = QLabel("Enable AI Workspace Insights")
        ins_l1.setProperty("class", "InnerTitle")
        ins_l2 = QLabel("Allow Searcher to suggest contextual actions while browsing.")
        ins_l2.setProperty("class", "InnerSub")
        ins_labels.addWidget(ins_l1)
        ins_labels.addWidget(ins_l2)
        ins_lay.addLayout(ins_labels)
        
        self.switch_insights = QPushButton()
        self.switch_insights.setCursor(Qt.CursorShape.PointingHandCursor)
        self.switch_insights.clicked.connect(lambda: self.toggle_switch("insights"))
        ins_lay.addWidget(self.switch_insights)
        ai_layout.addWidget(insight_inner)
        
        prefetch_inner = QFrame()
        prefetch_inner.setProperty("class", "InnerCard")
        pref_lay = QHBoxLayout(prefetch_inner)
        pref_labels = QVBoxLayout()
        pref_l1 = QLabel("Pre-fetch AI Summaries")
        pref_l1.setProperty("class", "InnerTitle")
        pref_l2 = QLabel("Automatically generate page summaries in the background.")
        pref_l2.setProperty("class", "InnerSub")
        pref_labels.addWidget(pref_l1)
        pref_labels.addWidget(pref_l2)
        pref_lay.addLayout(pref_labels)
        
        self.switch_prefetch = QPushButton()
        self.switch_prefetch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.switch_prefetch.clicked.connect(lambda: self.toggle_switch("prefetch"))
        pref_lay.addWidget(self.switch_prefetch)
        
        self.update_switch_ui("insights", self.settings_manager.get("ai_insights", True))
        self.update_switch_ui("prefetch", self.settings_manager.get("ai_prefetch", False))
        ai_layout.addWidget(prefetch_inner)
        ai_lay.addWidget(ai_card)

        # ==========================================
        # 3. Privacy & Security Page
        # ==========================================
        priv_lay = QVBoxLayout()
        priv_card = QFrame()
        priv_card.setProperty("class", "SettingsCard")
        priv_card_lay = QVBoxLayout(priv_card)
        priv_title = QLabel("🔒 Privacy & Security")
        priv_title.setProperty("class", "CardTitle")
        priv_info = QLabel("Manage your data, cookies, and tracking preferences.")
        priv_info.setStyleSheet("color: #cbd5e1; font-size: 14px; margin-top: 10px;")
        priv_card_lay.addWidget(priv_title)
        priv_card_lay.addWidget(priv_info)
        priv_lay.addWidget(priv_card)

        # ==========================================
        # 4. Sync Page
        # ==========================================
        sync_lay = QVBoxLayout()
        sync_card = QFrame()
        sync_card.setProperty("class", "SettingsCard")
        sync_layout = QVBoxLayout(sync_card)
        sync_title = QLabel("🔄 Sync Status")
        sync_title.setProperty("class", "CardTitle")
        sync_info = QLabel("🟢 Syncing to all devices\nLast synced: Just now")
        sync_info.setStyleSheet("color: #e2e8f0; font-size: 13px; line-height: 1.5; margin-top: 10px;")
        sync_layout.addWidget(sync_title)
        sync_layout.addWidget(sync_info)
        sync_lay.addWidget(sync_card)

        # Add all pages to stacked widget
        self.stacked_pages.addWidget(create_page(gen_lay))
        self.stacked_pages.addWidget(create_page(app_lay))
        self.stacked_pages.addWidget(create_page(ai_lay))
        self.stacked_pages.addWidget(create_page(priv_lay))
        self.stacked_pages.addWidget(create_page(sync_lay))
        
        content_layout.addWidget(self.stacked_pages)
        
        # Connect Navigation
        self.nav_list.currentRowChanged.connect(self.stacked_pages.setCurrentIndex)
        
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_container)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        main_layout.addWidget(scroll_area)

    def toggle_theme(self, theme_name):
        self.settings_manager.set("theme", theme_name)
        if theme_name == "light":
            self.btn_light.setProperty("class", "ToggleActive")
            self.btn_dark.setProperty("class", "ToggleInactive")
        else:
            self.btn_light.setProperty("class", "ToggleInactive")
            self.btn_dark.setProperty("class", "ToggleActive")
            
        self.btn_light.style().unpolish(self.btn_light)
        self.btn_light.style().polish(self.btn_light)
        self.btn_dark.style().unpolish(self.btn_dark)
        self.btn_dark.style().polish(self.btn_dark)
        
        # Apply theme to parent if available
        if self.main_window and hasattr(self.main_window, "apply_current_theme"):
            self.main_window.apply_current_theme()
            
    def toggle_typography(self, font_name):
        self.settings_manager.set("typography", font_name)
        active_font_style = "border: 1px solid #38bdf8; border-radius: 12px; padding: 12px; color: #fff; background-color: #1e293b; text-align: left;"
        inactive_font_style = "border: 1px solid #334155; border-radius: 12px; padding: 12px; color: #fff; background-color: transparent; text-align: left;"
        self.btn_inter.setStyleSheet(active_font_style if font_name == "Inter" else inactive_font_style)
        self.btn_poppins.setStyleSheet(active_font_style if font_name == "Poppins" else inactive_font_style)
            
    def toggle_switch(self, setting_key):
        full_key = f"ai_{setting_key}"
        current = self.settings_manager.get(full_key, setting_key == "insights")
        new_val = not current
        self.settings_manager.set(full_key, new_val)
        self.update_switch_ui(setting_key, new_val)
        
    def update_switch_ui(self, key, is_on):
        btn = self.switch_insights if key == "insights" else self.switch_prefetch
        if is_on:
            btn.setText("On")
            btn.setStyleSheet("background-color: #0ea5e9; color: white; border-radius: 12px; padding: 4px 12px; border: none; font-weight: 500;")
        else:
            btn.setText("Off")
            btn.setStyleSheet("background-color: #1e293b; color: #94a3b8; border-radius: 12px; padding: 4px 12px; border: none; font-weight: 500;")

        
    def save_and_close(self):
        self.settings_manager.set("theme", "dark")
        self.accept()
