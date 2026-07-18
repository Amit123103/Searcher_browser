from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QHBoxLayout, QLineEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

class PasswordManagerDialog(QDialog):
    """Dialog to manage saved passwords."""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Password Manager")
        self.resize(600, 400)
        self.setup_ui()
        self.load_passwords()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.pwd_tree = QTreeWidget()
        self.pwd_tree.setHeaderLabels(["URL", "Username", "Password"])
        self.pwd_tree.setColumnWidth(0, 250)
        self.pwd_tree.setColumnWidth(1, 150)
        # Double click to reveal password
        self.pwd_tree.itemDoubleClicked.connect(self.reveal_password)
        layout.addWidget(self.pwd_tree)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Password")
        add_btn.clicked.connect(self.add_password)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
    def load_passwords(self):
        self.pwd_tree.clear()
        records = self.db_manager.get_passwords()
        for pid, url, user, pwd in records:
            item = QTreeWidgetItem([url, user, "********"])
            item.setData(0, Qt.ItemDataRole.UserRole, pid)
            # Store real password in UserRole of the 3rd column
            item.setData(2, Qt.ItemDataRole.UserRole, pwd)
            self.pwd_tree.addTopLevelItem(item)
            
    def remove_selected(self):
        selected = self.pwd_tree.selectedItems()
        if not selected:
            return
        pid = selected[0].data(0, Qt.ItemDataRole.UserRole)
        self.db_manager.remove_password(pid)
        self.load_passwords()
        
    def reveal_password(self, item, column):
        if column == 2:
            real_pwd = item.data(2, Qt.ItemDataRole.UserRole)
            if item.text(2) == "********":
                item.setText(2, real_pwd)
            else:
                item.setText(2, "********")
                
    def add_password(self):
        # A simple dialog to manually add passwords
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Password")
        layout = QVBoxLayout(dialog)
        
        url_input = QLineEdit()
        url_input.setPlaceholderText("URL (e.g., https://github.com)")
        user_input = QLineEdit()
        user_input.setPlaceholderText("Username")
        pwd_input = QLineEdit()
        pwd_input.setPlaceholderText("Password")
        pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(QLabel("URL:"))
        layout.addWidget(url_input)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(user_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(pwd_input)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: dialog.accept())
        layout.addWidget(save_btn)
        
        if dialog.exec():
            u, usr, p = url_input.text().strip(), user_input.text().strip(), pwd_input.text()
            if u and usr and p:
                if self.db_manager.save_password(u, usr, p):
                    self.load_passwords()
                else:
                    QMessageBox.warning(self, "Error", "Could not save password.")
