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
        self.resize(900, 650)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC; /* Light background for settings page as in mockup */
            }
            QWidget#Sidebar {
                background-color: #333C45; /* Dark sidebar */
                color: #94A3B8;
            }
            QLabel#SidebarLogo {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton#NewWorkspaceBtn {
                background-color: #38BDF8;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                margin: 10px;
            }
            QListWidget#SidebarList {
                background-color: transparent;
                border: none;
                color: #CBD5E1;
                font-size: 13px;
                outline: none;
            }
            QListWidget#SidebarList::item {
                padding: 12px 20px;
                border-radius: 8px;
                margin: 2px 10px;
            }
            QListWidget#SidebarList::item:selected {
                background-color: #475569;
                color: #FFFFFF;
            }
            QListWidget#SidebarList::item:hover:!selected {
                background-color: #3E4A5B;
            }
            
            /* Main Content */
            QWidget#MainContent {
                background-color: #F8FAFC;
            }
            QLabel#PageTitle {
                font-size: 28px;
                font-weight: bold;
                color: #93C5FD;
            }
            QLabel#PageSubtitle {
                font-size: 14px;
                color: #94A3B8;
                margin-bottom: 20px;
            }
            
            /* Cards */
            QFrame.SettingsCard {
                background-color: #78828A;
                border-radius: 20px;
                padding: 20px;
            }
            QLabel.CardTitle {
                font-size: 16px;
                font-weight: bold;
                color: #FFFFFF;
                margin-bottom: 10px;
            }
            QFrame.InnerCard {
                background-color: #3E4651;
                border-radius: 12px;
                padding: 15px;
                margin-top: 10px;
            }
            QLabel.InnerTitle {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 500;
            }
            QLabel.InnerSub {
                color: #94A3B8;
                font-size: 11px;
            }
            
            /* Toggle Buttons */
            QPushButton.ToggleBtn {
                background-color: #1E293B;
                border-radius: 12px;
                padding: 4px;
                border: none;
            }
            QPushButton.ToggleActive {
                background-color: #38BDF8;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 4px 12px;
                font-size: 11px;
            }
            QPushButton.ToggleInactive {
                background-color: transparent;
                color: #94A3B8;
                border-radius: 10px;
                padding: 4px 12px;
                font-size: 11px;
            }
            
            /* User Card */
            QFrame#UserCard {
                background-color: #78828A;
                border-radius: 20px;
                padding: 20px;
            }
            QLabel#UserName {
                font-size: 18px;
                font-weight: bold;
                color: #FFFFFF;
                margin-top: 10px;
            }
            QLabel#UserEmail {
                font-size: 12px;
                color: #E2E8F0;
                margin-bottom: 15px;
            }
            QPushButton#ManageAccountBtn {
                background-color: #3E4651;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 10px;
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
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        logo_label = QLabel("Searcher")
        logo_label.setObjectName("SidebarLogo")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        new_ws_btn = QPushButton("+ New Workspace")
        new_ws_btn.setObjectName("NewWorkspaceBtn")
        
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("SidebarList")
        
        items = ["General", "Appearance", "AI Preferences", "Privacy & Security", "Sync"]
        for item_text in items:
            item = QListWidgetItem(item_text)
            self.nav_list.addItem(item)
        self.nav_list.setCurrentRow(1) # Default to Appearance like mockup
        
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addWidget(new_ws_btn)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()
        
        privacy_label = QLabel(" Privacy\n Security")
        privacy_label.setStyleSheet("color: #94A3B8; padding: 20px; font-size: 11px;")
        sidebar_layout.addWidget(privacy_label)
        
        main_layout.addWidget(sidebar)
        
        # --- Main Content ---
        content_container = QWidget()
        content_container.setObjectName("MainContent")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        header_title = QLabel("Settings")
        header_title.setObjectName("PageTitle")
        header_subtitle = QLabel("Customize your Searcher experience and manage your preferences.")
        header_subtitle.setObjectName("PageSubtitle")
        
        content_layout.addWidget(header_title)
        content_layout.addWidget(header_subtitle)
        
        # Grid for cards
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(20)
        
        # Left Column Cards
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        
        # Appearance Card
        from PyQt6.QtWidgets import QFrame
        app_card = QFrame()
        app_card.setProperty("class", "SettingsCard")
        app_layout = QVBoxLayout(app_card)
        
        app_title = QLabel("🎨 Appearance")
        app_title.setProperty("class", "CardTitle")
        app_layout.addWidget(app_title)
        
        # Color Theme Inner
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
        theme_toggle_bg.setStyleSheet("background-color: #1E293B; border-radius: 12px; padding: 2px;")
        tt_lay = QHBoxLayout(theme_toggle_bg)
        tt_lay.setContentsMargins(2,2,2,2)
        tt_lay.setSpacing(0)
        
        btn_light = QPushButton("Light")
        btn_light.setProperty("class", "ToggleInactive")
        btn_dark = QPushButton("Dark")
        btn_dark.setProperty("class", "ToggleActive")
        btn_dark.clicked.connect(self.save_and_close) # Just as an example action
        
        tt_lay.addWidget(btn_light)
        tt_lay.addWidget(btn_dark)
        
        theme_inner_lay.addLayout(theme_labels)
        theme_inner_lay.addWidget(theme_toggle_bg)
        
        app_layout.addWidget(theme_inner)
        
        # Typography Inner (Placeholder for design)
        typo_inner = QFrame()
        typo_inner.setProperty("class", "InnerCard")
        typo_inner_lay = QVBoxLayout(typo_inner)
        typo_lbl = QLabel("Typography")
        typo_lbl.setProperty("class", "InnerTitle")
        typo_inner_lay.addWidget(typo_lbl)
        
        app_layout.addWidget(typo_inner)
        
        left_col.addWidget(app_card)
        
        # AI Prefs Card
        ai_card = QFrame()
        ai_card.setProperty("class", "SettingsCard")
        ai_layout = QVBoxLayout(ai_card)
        
        ai_title = QLabel("✨ AI Preferences")
        ai_title.setProperty("class", "CardTitle")
        ai_layout.addWidget(ai_title)
        
        # AI Insights
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
        
        ai_layout.addWidget(insight_inner)
        
        left_col.addWidget(ai_card)
        left_col.addStretch()
        
        # Right Column Cards
        right_col = QVBoxLayout()
        right_col.setSpacing(20)
        
        user_card = QFrame()
        user_card.setObjectName("UserCard")
        user_layout = QVBoxLayout(user_card)
        user_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mock Avatar
        avatar = QLabel()
        avatar.setFixedSize(60, 60)
        avatar.setStyleSheet("background-color: #1E293B; border-radius: 30px;")
        
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
        sync_info.setStyleSheet("color: #E2E8F0; font-size: 12px; margin-top: 10px;")
        sync_layout.addWidget(sync_title)
        sync_layout.addWidget(sync_info)
        
        right_col.addWidget(sync_card)
        right_col.addStretch()
        
        # Assemble
        grid_layout.addLayout(left_col, 2)
        grid_layout.addLayout(right_col, 1)
        
        content_layout.addLayout(grid_layout)
        
        main_layout.addWidget(content_container)
        
    def save_and_close(self):
        # We can simulate saving the theme
        self.settings_manager.set("theme", "dark")
        self.accept()
