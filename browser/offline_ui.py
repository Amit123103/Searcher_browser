"""
Searcher Browser - Offline Manager UI Component
Provides status indicator badge and Offline Manager Dialog.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, QFrame, 
                             QProgressBar, QMessageBox, QWidget, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor


class OfflineStatusBadge(QPushButton):
    """
    Sleek navigation bar indicator badge that displays current connection status
    and pending offline sync count.
    """
    def __init__(self, offline_engine, parent=None):
        super().__init__(parent)
        self.offline_engine = offline_engine
        self.setObjectName("offlineStatusBadge")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to open Offline Application Manager")
        
        # Connect signals
        self.offline_engine.connection_changed.connect(self.update_status)
        self.offline_engine.sync_manager.queue_updated.connect(self.on_queue_updated)
        
        self.clicked.connect(self.show_offline_dialog)
        self.update_status(self.offline_engine.is_online())

    def update_status(self, is_online: bool):
        pending = self.offline_engine.sync_manager.get_pending_count()
        if is_online:
            if pending > 0:
                self.setText(f"🟢 Online ({pending} Syncing)")
                self.setStyleSheet("""
                    QPushButton#offlineStatusBadge {
                        background: rgba(34, 197, 94, 0.15);
                        color: #4ADE80;
                        border: 1px solid rgba(34, 197, 94, 0.3);
                        border-radius: 12px;
                        padding: 4px 10px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                    QPushButton#offlineStatusBadge:hover {
                        background: rgba(34, 197, 94, 0.25);
                    }
                """)
            else:
                self.setText("🟢 Online")
                self.setStyleSheet("""
                    QPushButton#offlineStatusBadge {
                        background: rgba(34, 197, 94, 0.12);
                        color: #4ADE80;
                        border: 1px solid rgba(34, 197, 94, 0.25);
                        border-radius: 12px;
                        padding: 4px 10px;
                        font-size: 11px;
                        font-weight: 500;
                    }
                    QPushButton#offlineStatusBadge:hover {
                        background: rgba(34, 197, 94, 0.22);
                    }
                """)
        else:
            txt = "🟠 Offline Mode"
            if pending > 0:
                txt += f" ({pending} Queued)"
            self.setText(txt)
            self.setStyleSheet("""
                QPushButton#offlineStatusBadge {
                    background: rgba(245, 158, 11, 0.18);
                    color: #FBBF24;
                    border: 1px solid rgba(245, 158, 11, 0.35);
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: 600;
                }
                QPushButton#offlineStatusBadge:hover {
                    background: rgba(245, 158, 11, 0.28);
                }
            """)

    def on_queue_updated(self, count: int):
        self.update_status(self.offline_engine.is_online())

    def show_offline_dialog(self):
        dialog = OfflineManagerDialog(self.offline_engine, self.window())
        dialog.exec()


class OfflineManagerDialog(QDialog):
    """
    Offline Application Manager Dashboard Dialog.
    Displays cache storage metrics, sync queue items, and management actions.
    """
    def __init__(self, offline_engine, parent=None):
        super().__init__(parent)
        self.offline_engine = offline_engine
        self.setWindowTitle("Offline Application Engine Manager")
        self.setFixedSize(540, 480)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QLabel { color: #F8FAFC; }
            QFrame.Card {
                background-color: #1E293B;
                border-radius: 12px;
                padding: 16px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            QListWidget {
                background-color: #0B0F19;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #CBD5E1;
                font-size: 12px;
            }
            QPushButton {
                background-color: #3B82F6;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton#secondaryBtn {
                background-color: rgba(255, 255, 255, 0.08);
                color: #CBD5E1;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }
            QPushButton#secondaryBtn:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: #FFFFFF;
            }
            QPushButton#dangerBtn {
                background-color: rgba(239, 68, 68, 0.2);
                color: #FCA5A5;
                border: 1px solid rgba(239, 68, 68, 0.4);
            }
            QPushButton#dangerBtn:hover {
                background-color: rgba(239, 68, 68, 0.35);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        title_lbl = QLabel("⚡ Offline Application Engine")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        layout.addWidget(title_lbl)

        # Status & Storage Card
        card = QFrame()
        card.setObjectName("card")
        card.setProperty("class", "Card")
        card_layout = QVBoxLayout(card)

        # Row 1: Connection status
        status_row = QHBoxLayout()
        status_title = QLabel("Connection State:")
        status_title.setStyleSheet("font-weight: 600; font-size: 13px;")
        self.status_val_lbl = QLabel("Online")
        self.status_val_lbl.setStyleSheet("font-weight: bold; color: #4ADE80; font-size: 13px;")
        status_row.addWidget(status_title)
        status_row.addWidget(self.status_val_lbl)
        status_row.addStretch()
        
        self.recheck_btn = QPushButton("Check Connection")
        self.recheck_btn.setObjectName("secondaryBtn")
        self.recheck_btn.clicked.connect(self.on_recheck_connection)
        status_row.addWidget(self.recheck_btn)
        card_layout.addLayout(status_row)

        # Row 2: Cache Usage
        cache_row = QHBoxLayout()
        cache_lbl = QLabel("Resource Cache Storage:")
        cache_lbl.setStyleSheet("font-size: 12px; color: #94A3B8;")
        self.cache_val_lbl = QLabel("0 Files (0 MB / 200 MB)")
        self.cache_val_lbl.setStyleSheet("font-size: 12px; font-weight: 500;")
        cache_row.addWidget(cache_lbl)
        cache_row.addStretch()
        cache_row.addWidget(self.cache_val_lbl)
        card_layout.addLayout(cache_row)

        layout.addWidget(card)

        # Queue Section Header
        queue_header_row = QHBoxLayout()
        queue_lbl = QLabel("Pending Background Sync Requests:")
        queue_lbl.setStyleSheet("font-weight: 600; font-size: 13px; color: #CBD5E1;")
        queue_header_row.addWidget(queue_lbl)
        queue_header_row.addStretch()

        self.sync_now_btn = QPushButton("🔄 Replay Sync Now")
        self.sync_now_btn.clicked.connect(self.on_force_sync)
        queue_header_row.addWidget(self.sync_now_btn)
        layout.addLayout(queue_header_row)

        # List Widget for Queued Requests
        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)

        # Bottom Actions Row
        bottom_row = QHBoxLayout()
        self.clear_cache_btn = QPushButton("Clear Offline Cache")
        self.clear_cache_btn.setObjectName("dangerBtn")
        self.clear_cache_btn.clicked.connect(self.on_clear_cache)
        bottom_row.addWidget(self.clear_cache_btn)

        bottom_row.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryBtn")
        close_btn.clicked.connect(self.accept)
        bottom_row.addWidget(close_btn)

        layout.addLayout(bottom_row)

    def load_data(self):
        # Update Connection Status
        is_online = self.offline_engine.is_online()
        if is_online:
            self.status_val_lbl.setText("🟢 Online (Connected)")
            self.status_val_lbl.setStyleSheet("font-weight: bold; color: #4ADE80; font-size: 13px;")
        else:
            self.status_val_lbl.setText("🟠 Offline (Disconnected)")
            self.status_val_lbl.setStyleSheet("font-weight: bold; color: #FBBF24; font-size: 13px;")

        # Update Cache Stats
        stats = self.offline_engine.cache_manager.get_cache_stats()
        self.cache_val_lbl.setText(f"{stats['count']} items ({stats['size_mb']} MB / {stats['max_mb']} MB)")

        # Update Queue List
        self.queue_list.clear()
        pending = self.offline_engine.sync_manager.get_pending_requests()
        if not pending:
            item = QListWidgetItem("No pending requests in background sync queue.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.queue_list.addItem(item)
        else:
            for req in pending:
                txt = f"[{req['method']}] {req['url']} (Retries: {req['retry_count']})"
                item = QListWidgetItem(txt)
                self.queue_list.addItem(item)

    def on_recheck_connection(self):
        online = self.offline_engine.detector.check_connection()
        self.offline_engine.on_connectivity_changed(online)
        self.load_data()
        QMessageBox.information(self, "Network Status", f"Network Status: {'Online' if online else 'Offline'}")

    def on_force_sync(self):
        if not self.offline_engine.is_online():
            QMessageBox.warning(self, "Offline Mode", "Cannot sync while internet is disconnected. Reconnect to sync pending requests.")
            return
        self.offline_engine.sync_manager.replay_pending_requests()
        self.load_data()
        QMessageBox.information(self, "Sync Complete", "Background sync completed.")

    def on_clear_cache(self):
        res = QMessageBox.question(self, "Clear Cache", "Are you sure you want to clear all offline cached resources?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            self.offline_engine.cache_manager.clear_cache()
            self.load_data()
            QMessageBox.information(self, "Cache Cleared", "Offline resource cache cleared successfully.")
