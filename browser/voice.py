from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtCore import Qt, QTimer

class VoiceSearchDialog(QDialog):
    """
    Mock Voice Search Dialog.
    In a full implementation, this would use SpeechRecognition and PyAudio.
    Here we simulate the process to avoid heavy dependencies on the demo machine.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Voice Search")
        self.resize(300, 150)
        # Make it look like a sleek popup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setStyleSheet("QDialog { border: 2px solid #8ab4f8; border-radius: 10px; }")
        
        self.search_query = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QLabel("🎤 Listening...")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate progress simulating active listening
        layout.addWidget(self.progress)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        # Simulate voice recognition finishing after 2 seconds
        QTimer.singleShot(2000, self.simulate_recognition)
        
    def simulate_recognition(self):
        # We simulate a spoken query for demo purposes
        self.search_query = "What is the current weather?"
        self.status_label.setText(f"Heard: '{self.search_query}'")
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        
        # Accept automatically after a brief pause so user can read what was heard
        QTimer.singleShot(1500, self.accept)
        
    def get_query(self):
        return self.search_query
