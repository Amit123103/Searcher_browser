import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton)

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
        self.resize(300, 150)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Theme Setting
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        
        # Set current theme in combo box
        current_theme = self.settings_manager.get("theme", "dark").capitalize()
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
            
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        # Cache Management
        clear_cache_btn = QPushButton("Clear Cache && Browsing Data")
        clear_cache_btn.clicked.connect(self.clear_cache)
        layout.addWidget(clear_cache_btn)
        
        # Save Button
        save_btn = QPushButton("Save && Restart")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)
        
    def clear_cache(self):
        from PyQt6.QtWebEngineCore import QWebEngineProfile
        profile = QWebEngineProfile.defaultProfile()
        profile.clearHttpCache()
        profile.clearAllVisitedLinks()
        # Could also emit a signal to clear local db history if desired
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Cache Cleared", "Browser cache has been cleared.")
        
    def save_and_close(self):
        selected_theme = self.theme_combo.currentText().lower()
        self.settings_manager.set("theme", selected_theme)
        # Accept closes the dialog and returns QDialog.DialogCode.Accepted
        self.accept()
