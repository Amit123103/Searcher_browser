import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, 
                             QPushButton, QHBoxLayout, QListWidgetItem, QFileDialog, QSystemTrayIcon)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

class DownloadManagerDialog(QDialog):
    """Dialog to track and manage downloads."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.resize(500, 300)
        self.setup_ui()
        
        # Setup tray icon for notifications
        self.tray_icon = QSystemTrayIcon(self)
        # Using a standard icon for simplicity
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowDown))
        self.tray_icon.show()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.download_list = QListWidget()
        layout.addWidget(self.download_list)
        
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Finished")
        clear_btn.clicked.connect(self.clear_finished)
        close_btn = QPushButton("Close")
        # We use hide() instead of accept() because this might be opened/closed multiple times
        close_btn.clicked.connect(self.hide)
        
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
    def handle_download_requested(self, download_item: QWebEngineDownloadRequest):
        """Intercepts the download request, prompts the user, and starts tracking."""
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", download_item.downloadFileName())
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)
        
        if save_path:
            download_item.setDownloadDirectory(os.path.dirname(save_path))
            download_item.setDownloadFileName(os.path.basename(save_path))
            
            # Create a list item to represent this download
            list_item = QListWidgetItem(f"Starting: {download_item.downloadFileName()}")
            self.download_list.addItem(list_item)
            
            # Connect signals to update the UI
            download_item.stateChanged.connect(
                lambda state, item=list_item, d=download_item: self.update_download_state(state, item, d)
            )
            download_item.receivedBytesChanged.connect(
                lambda item=list_item, d=download_item: self.update_download_progress(item, d)
            )
            
            download_item.accept()
            self.show()
            
    def update_download_state(self, state, list_item, download_item):
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            list_item.setText(f"Completed: {download_item.downloadFileName()}")
            self.tray_icon.showMessage(
                "Download Complete", 
                f"{download_item.downloadFileName()} has finished downloading.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            list_item.setText(f"Cancelled: {download_item.downloadFileName()}")
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            list_item.setText(f"Interrupted: {download_item.downloadFileName()}")
            
    def update_download_progress(self, list_item, download_item):
        received = download_item.receivedBytes()
        total = download_item.totalBytes()
        if total > 0:
            percent = int((received / total) * 100)
            list_item.setText(f"Downloading: {download_item.downloadFileName()} ({percent}%)")
        else:
            list_item.setText(f"Downloading: {download_item.downloadFileName()} ({received} bytes)")
            
    def clear_finished(self):
        # Remove completed/cancelled/interrupted items
        for i in range(self.download_list.count() - 1, -1, -1):
            item = self.download_list.item(i)
            text = item.text()
            if text.startswith(("Completed:", "Cancelled:", "Interrupted:")):
                self.download_list.takeItem(i)
