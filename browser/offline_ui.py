"""
Searcher Browser - Offline Manager UI Component
Provides status indicator badge and Offline Manager Dialog.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem, QFrame, 
                             QProgressBar, QMessageBox, QWidget, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
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
    Shows cache storage metrics, background sync queue, and prefetch progress.
    """
    def __init__(self, offline_engine, parent=None):
        super().__init__(parent)
        self.offline_engine = offline_engine
        self.setWindowTitle("Offline Application Engine Manager")
        self.setMinimumSize(560, 520)
        self.setup_ui()
        self.load_data()
        # Connect live engine signals
        self.offline_engine.cache_progress.connect(self._on_cache_progress)
        self.offline_engine.cache_batch_done.connect(self._on_cache_batch_done)
        self.offline_engine.connection_changed.connect(lambda _: self.load_data())
        self.offline_engine.sync_manager.queue_updated.connect(lambda _: self.load_data())

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QLabel { color: #F8FAFC; }
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
            QPushButton:hover { background-color: #2563EB; }
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
            QPushButton#dangerBtn:hover { background-color: rgba(239, 68, 68, 0.35); }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #1E293B;
                color: transparent;
                min-height: 8px;
                max-height: 8px;
            }
            QProgressBar::chunk {
                background-color: #38BDF8;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        header_row = QHBoxLayout()
        title_lbl = QLabel("⚡ Offline Application Engine")
        title_lbl.setStyleSheet("font-size: 17px; font-weight: bold; color: #38BDF8;")
        header_row.addWidget(title_lbl)
        header_row.addStretch()
        # Force-prefetch button
        self.prefetch_btn = QPushButton("📥 Cache Current Page")
        self.prefetch_btn.setObjectName("secondaryBtn")
        self.prefetch_btn.setToolTip("Pre-cache all resources of the current page for offline use")
        self.prefetch_btn.clicked.connect(self._on_force_prefetch)
        header_row.addWidget(self.prefetch_btn)
        layout.addLayout(header_row)

        # Status Card
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #1E293B; border-radius: 10px; border: 1px solid rgba(255,255,255,0.07); }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(8)

        # Connection state row
        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Connection:"))
        self.status_val_lbl = QLabel("Online")
        self.status_val_lbl.setStyleSheet("font-weight: bold; color: #4ADE80;")
        status_row.addWidget(self.status_val_lbl)
        status_row.addStretch()
        self.recheck_btn = QPushButton("Check Now")
        self.recheck_btn.setObjectName("secondaryBtn")
        self.recheck_btn.clicked.connect(self.on_recheck_connection)
        status_row.addWidget(self.recheck_btn)
        card_layout.addLayout(status_row)

        # Cache stats row
        cache_row = QHBoxLayout()
        cache_lbl = QLabel("Resource Cache:")
        cache_lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self.cache_val_lbl = QLabel("0 items  (0 MB / 200 MB)")
        self.cache_val_lbl.setStyleSheet("font-size: 12px;")
        cache_row.addWidget(cache_lbl)
        cache_row.addStretch()
        cache_row.addWidget(self.cache_val_lbl)
        card_layout.addLayout(cache_row)

        layout.addWidget(card)

        # Prefetch progress bar (hidden until prefetch starts)
        self.prefetch_label = QLabel("Background Cache Prefetch:")
        self.prefetch_label.setStyleSheet("font-size: 11px; color: #64748B;")
        self.prefetch_label.hide()
        layout.addWidget(self.prefetch_label)

        self.prefetch_progress = QProgressBar()
        self.prefetch_progress.setRange(0, 100)
        self.prefetch_progress.setValue(0)
        self.prefetch_progress.hide()
        layout.addWidget(self.prefetch_progress)

        # Sync queue section
        queue_row = QHBoxLayout()
        queue_lbl = QLabel("Pending Background Sync Requests:")
        queue_lbl.setStyleSheet("font-weight: 600; font-size: 12px; color: #CBD5E1;")
        queue_row.addWidget(queue_lbl)
        queue_row.addStretch()
        self.sync_now_btn = QPushButton("🔄 Replay Sync Now")
        self.sync_now_btn.clicked.connect(self.on_force_sync)
        queue_row.addWidget(self.sync_now_btn)
        layout.addLayout(queue_row)

        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)

        # Bottom row
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
        self.offline_engine._on_connectivity_changed(online)
        self.load_data()
        QMessageBox.information(self, "Network Status",
                                f"Status: {'🟢 Online' if online else '🟠 Offline'}")

    def on_force_sync(self):
        if not self.offline_engine.is_online():
            QMessageBox.warning(self, "Offline",
                                "Cannot sync — internet is disconnected.\nRequests will replay automatically when reconnected.")
            return
        self.offline_engine.sync_manager.replay_async()
        QMessageBox.information(self, "Sync Started",
                                "Background sync started. The queue will update automatically.")

    def on_clear_cache(self):
        res = QMessageBox.question(
            self, "Clear Cache",
            "Delete all offline cached resources?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if res == QMessageBox.StandardButton.Yes:
            self.offline_engine.cache_manager.clear_cache()
            self.load_data()
            QMessageBox.information(self, "Cache Cleared", "Offline resource cache cleared.")

    def _on_cache_progress(self, done: int, total: int):
        """Shows and updates the prefetch progress bar."""
        if total == 0:
            return
        self.prefetch_label.show()
        self.prefetch_progress.show()
        pct = int((done / total) * 100)
        self.prefetch_progress.setValue(pct)
        self.prefetch_label.setText(f"Caching resources: {done} / {total}")

    def _on_cache_batch_done(self, count: int):
        """Hides progress bar and refreshes stats after prefetch completes."""
        self.prefetch_progress.hide()
        self.prefetch_label.setText(f"✅ Cached {count} resource(s) — page ready for offline use.")
        self.load_data()

    def _on_force_prefetch(self):
        """
        Manually triggers resource harvesting for the current tab.
        Runs the resource-discovery JS on the active page and passes
        the discovered URLs to the prefetch engine.
        """
        main_window = self.parent()
        if not hasattr(main_window, 'tabs'):
            return
        browser = main_window.tabs.current_browser()
        if not browser:
            return

        js = """
(function() {
    const urls = [];
    document.querySelectorAll('link[href], script[src], img[src], source[src]').forEach(el => {
        const url = el.href || el.src;
        if (url && (url.startsWith('http://') || url.startsWith('https://'))) urls.push(url);
    });
    if (window.performance && window.performance.getEntriesByType) {
        window.performance.getEntriesByType('resource').forEach(e => {
            if (e.name && e.name.startsWith('http')) urls.push(e.name);
        });
    }
    return [...new Set(urls)];
})();
        """
        def _got_urls(result):
            if isinstance(result, list) and result:
                self.offline_engine.prefetch_page_resources(result)
                self.prefetch_label.setText(f"Queued {len(result)} resources for caching...")
                self.prefetch_label.show()
                self.prefetch_progress.show()
                self.prefetch_progress.setValue(0)

        browser.page().runJavaScript(js, _got_urls)
