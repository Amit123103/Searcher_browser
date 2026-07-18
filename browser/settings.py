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


class SettingsDialog(QDialog):
    """Dialog UI for users to modify browser settings."""
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Settings")
        self.resize(1000, 750)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
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
            }
            QPushButton.ToggleInactive {
                background-color: transparent;
                color: #94a3b8;
                border-radius: 10px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: 500;
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
        
        logo_label = QLabel("S Searcher")
        logo_label.setObjectName("SidebarLogo")
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
        
        sidebar_layout.addWidget(logo_label)
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
        
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)
        
        left_col = QVBoxLayout()
        left_col.setSpacing(24)
        
        # Appearance Card
        from PyQt6.QtWidgets import QFrame
        app_card = QFrame()
        app_card.setProperty("class", "SettingsCard")
        app_layout = QVBoxLayout(app_card)
        
        app_title = QLabel("🎨 Appearance")
        app_title.setProperty("class", "CardTitle")
        app_layout.addWidget(app_title)
        
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
        
        btn_light = QPushButton("Light")
        btn_light.setProperty("class", "ToggleInactive")
        btn_dark = QPushButton("Dark")
        btn_dark.setProperty("class", "ToggleActive")
        tt_lay.addWidget(btn_light)
        tt_lay.addWidget(btn_dark)
        
        theme_inner_lay.addLayout(theme_labels)
        theme_inner_lay.addWidget(theme_toggle_bg)
        app_layout.addWidget(theme_inner)
        
        # Typography inner
        typo_inner = QFrame()
        typo_inner.setProperty("class", "InnerCard")
        typo_lay = QVBoxLayout(typo_inner)
        typo_lbl = QLabel("Typography")
        typo_lbl.setProperty("class", "InnerTitle")
        typo_lay.addWidget(typo_lbl)
        
        fonts_lay = QHBoxLayout()
        font1 = QLabel("Inter\n\nAa")
        font1.setStyleSheet("border: 1px solid #38bdf8; border-radius: 12px; padding: 12px; color: #fff;")
        font2 = QLabel("Poppins\n\nAa")
        font2.setStyleSheet("border: 1px solid #334155; border-radius: 12px; padding: 12px; color: #fff;")
        fonts_lay.addWidget(font1)
        fonts_lay.addWidget(font2)
        typo_lay.addLayout(fonts_lay)
        
        app_layout.addWidget(typo_inner)
        left_col.addWidget(app_card)
        
        # AI Prefs Card
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
        
        switch1 = QLabel("On")
        switch1.setStyleSheet("background-color: #0ea5e9; color: white; border-radius: 12px; padding: 4px 12px;")
        ins_lay.addWidget(switch1)
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
        
        switch2 = QLabel("Off")
        switch2.setStyleSheet("background-color: #1e293b; color: white; border-radius: 12px; padding: 4px 12px;")
        pref_lay.addWidget(switch2)
        ai_layout.addWidget(prefetch_inner)
        
        left_col.addWidget(ai_card)
        left_col.addStretch()
        
        # Right Column
        right_col = QVBoxLayout()
        right_col.setSpacing(24)
        
        user_card = QFrame()
        user_card.setObjectName("UserCard")
        user_layout = QVBoxLayout(user_card)
        user_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        avatar = QLabel()
        avatar.setFixedSize(80, 80)
        avatar.setStyleSheet("background-color: #1e293b; border-radius: 40px; margin-top: 10px;")
        
        uname = QLabel("Alex Nova")
        uname.setObjectName("UserName")
        uname.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        umail = QLabel("alex.nova@searcher.ai")
        umail.setObjectName("UserEmail")
        umail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        manage_btn = QPushButton("Manage Account")
        manage_btn.setObjectName("ManageAccountBtn")
        
        user_layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        user_layout.addWidget(uname)
        user_layout.addWidget(umail)
        user_layout.addWidget(manage_btn)
        
        right_col.addWidget(user_card)
        
        sync_card = QFrame()
        sync_card.setProperty("class", "SettingsCard")
        sync_layout = QVBoxLayout(sync_card)
        sync_title = QLabel("🔄 Sync Status")
        sync_title.setProperty("class", "CardTitle")
        sync_info = QLabel("🟢 Syncing to all devices\nLast synced: Just now")
        sync_info.setStyleSheet("color: #e2e8f0; font-size: 13px; line-height: 1.5; margin-top: 10px;")
        sync_layout.addWidget(sync_title)
        sync_layout.addWidget(sync_info)
        
        right_col.addWidget(sync_card)
        right_col.addStretch()
        
        grid_layout.addLayout(left_col, 2)
        grid_layout.addLayout(right_col, 1)
        
        content_layout.addLayout(grid_layout)
        main_layout.addWidget(content_container)
        
    def save_and_close(self):
        self.settings_manager.set("theme", "dark")
        self.accept()
