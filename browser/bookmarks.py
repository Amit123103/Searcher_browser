from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, 
                             QPushButton, QHBoxLayout, QListWidgetItem)
from PyQt6.QtCore import QUrl, Qt

class BookmarksDialog(QDialog):
    """Dialog to view and manage bookmarks."""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.parent_window = parent
        self.setWindowTitle("Bookmarks")
        self.resize(600, 400)
        self.setup_ui()
        self.load_bookmarks()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.bookmarks_list)
        
        btn_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
    def load_bookmarks(self):
        self.bookmarks_list.clear()
        records = self.db_manager.get_bookmarks()
        for url, title, added_time in records:
            display_text = f"{title} - {url}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, url)
            self.bookmarks_list.addItem(item)
            
    def remove_selected(self):
        selected_items = self.bookmarks_list.selectedItems()
        if not selected_items:
            return
            
        url = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.db_manager.remove_bookmark(url)
        self.load_bookmarks()
        
    def on_item_double_clicked(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if self.parent_window and hasattr(self.parent_window, 'tabs'):
            self.parent_window.tabs.add_new_tab(QUrl(url))
        self.accept()
