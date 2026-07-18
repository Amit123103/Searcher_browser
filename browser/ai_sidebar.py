from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, 
                             QTextEdit, QLineEdit, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt

class AISidebar(QDockWidget):
    """
    Dockable widget providing an AI Assistant interface.
    Allows summarizing pages, generating notes, and asking questions.
    """
    
    def __init__(self, ai_service, parent=None):
        super().__init__("AI Assistant", parent)
        self.ai_service = ai_service
        self.parent_window = parent
        
        # Allow docking to left or right sides
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        
        self.setup_ui()
        
    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("padding: 5px; font-size: 14px;")
        self.chat_display.setPlaceholderText("Hi! I'm your AI Assistant. Ask me to summarize the page or generate notes...")
        layout.addWidget(self.chat_display)
        
        # Quick Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_summarize = QPushButton("Summarize Page")
        self.btn_summarize.clicked.connect(self.on_summarize)
        self.btn_notes = QPushButton("Generate Notes")
        self.btn_notes.clicked.connect(self.on_notes)
        
        btn_layout.addWidget(self.btn_summarize)
        btn_layout.addWidget(self.btn_notes)
        layout.addLayout(btn_layout)
        
        # Chat Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask a question...")
        self.input_field.returnPressed.connect(self.on_ask)
        
        self.btn_ask = QPushButton("Ask")
        self.btn_ask.clicked.connect(self.on_ask)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_ask)
        layout.addLayout(input_layout)
        
        self.setWidget(container)
        
    def append_message(self, sender, text):
        """Helper to append HTML formatted messages to the chat."""
        # Convert simple line breaks to HTML breaks for basic formatting
        html_text = text.replace('\n', '<br>')
        if sender == "You":
            color = "#8ab4f8"  # A nice blue
        else:
            color = "#f28b82"  # A nice red/pink for AI
            
        self.chat_display.append(f"<b style='color:{color};'>{sender}:</b> {html_text}<br>")
        
    def get_page_content(self, callback):
        """Asynchronously requests the page text from the main window."""
        if hasattr(self.parent_window, "get_current_page_text"):
            self.parent_window.get_current_page_text(callback)
        else:
            callback("")
            
    def on_summarize(self):
        self.append_message("You", "Please summarize this page.")
        # Callback pattern is necessary because toPlainText() in QWebEnginePage is asynchronous
        self.get_page_content(lambda text: self.append_message("AI Assistant", self.ai_service.summarize(text)))
        
    def on_notes(self):
        self.append_message("You", "Generate notes from this page.")
        self.get_page_content(lambda text: self.append_message("AI Assistant", self.ai_service.generate_notes(text)))
        
    def on_ask(self):
        question = self.input_field.text().strip()
        if not question:
            return
            
        self.input_field.clear()
        self.append_message("You", question)
        
        self.get_page_content(lambda text: self.append_message("AI Assistant", self.ai_service.answer_question(text, question)))
