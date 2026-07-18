from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, 
                             QPushButton, QHBoxLayout, QListWidgetItem)
from PyQt6.QtCore import QUrl, Qt

class HistoryDialog(QDialog):
    """Dialog to view and manage browsing history."""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.parent_window = parent
        self.setWindowTitle("Browsing History")
        self.resize(600, 400)
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.history_list)
        
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
    def load_history(self):
        self.history_list.clear()
        records = self.db_manager.get_history(100)
        for url, title, visit_time in records:
            # Format display string
            display_text = f"{visit_time[:16]} | {title} - {url}"
            item = QListWidgetItem(display_text)
            # Store the URL in the item's UserRole for easy retrieval
            item.setData(Qt.ItemDataRole.UserRole, url)
            self.history_list.addItem(item)
            
    def clear_history(self):
        self.db_manager.clear_history()
        self.load_history()
        
    def on_item_double_clicked(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        # Open URL in a new tab if parent exists
        if self.parent_window and hasattr(self.parent_window, 'tabs'):
            self.parent_window.tabs.add_new_tab(QUrl(url))
        self.accept()
