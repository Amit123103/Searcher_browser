from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QHBoxLayout, 
                             QScrollArea, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QCursor

class AISidebar(QDockWidget):
    """
    Dockable widget providing the Workspace AI interface.
    """
    
    def __init__(self, ai_service, parent=None):
        super().__init__("Workspace AI", parent)
        self.ai_service = ai_service
        self.parent_window = parent
        
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        
        # We override the title bar to make it match the design if needed, but QSS handles most
        self.setStyleSheet("""
            QDockWidget {
                titlebar-close-icon: url(assets/close.svg);
                titlebar-normal-icon: url(assets/float.svg);
                font-weight: 600;
            }
            QDockWidget::title {
                text-align: left;
                background: #17191C;
                padding: 10px;
                color: #38BDF8;
            }
            QWidget#SidebarContainer {
                background-color: #17191C;
                border-left: 1px solid #23272E;
            }
            QFrame#SummaryCard {
                background-color: #1C1F26;
                border: 1px solid #2A2F38;
                border-radius: 12px;
            }
            QLabel#SummaryTitle {
                color: #94A3B8;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QLabel#SummaryText {
                color: #E2E8F0;
                font-size: 13px;
                line-height: 1.5;
            }
            QPushButton.ActionBtn {
                text-align: left;
                background-color: transparent;
                border: none;
                color: #E2E8F0;
                padding: 10px 5px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton.ActionBtn:hover {
                color: #38BDF8;
                background-color: rgba(56, 189, 248, 0.05);
                border-radius: 6px;
            }
            QLineEdit#ChatInput {
                background-color: #1C1F26;
                border: 1px solid #2A2F38;
                border-radius: 20px;
                padding: 10px 40px 10px 15px;
                color: #F8FAFC;
                font-size: 13px;
            }
            QLineEdit#ChatInput:focus {
                border: 1px solid #38BDF8;
            }
            QPushButton#SendBtn {
                background-color: #38BDF8;
                border: none;
                border-radius: 14px;
                width: 28px;
                height: 28px;
            }
            QPushButton#SendBtn:hover {
                background-color: #7DD3FC;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        container = QWidget()
        container.setObjectName("SidebarContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Summary Card
        summary_card = QFrame()
        summary_card.setObjectName("SummaryCard")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(8)
        
        summary_title = QLabel("📄 PAGE SUMMARY")
        summary_title.setObjectName("SummaryTitle")
        
        self.summary_text = QLabel("The article discusses the transition from screen-based interactions to ambient computing. Key points include the shift from traditional \"desktop\" metaphors to predictive, agentic workspaces, and the replacement of hierarchical menus with natural language intent mapping.")
        self.summary_text.setObjectName("SummaryText")
        self.summary_text.setWordWrap(True)
        
        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_card)
        
        # Action List
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(4)
        
        self.btn_quotes = self.create_action_btn("❞  Extract key quotes")
        self.btn_thread = self.create_action_btn("🔗  Generate social thread")
        self.btn_views = self.create_action_btn("🔍  Find opposing views")
        
        self.btn_quotes.clicked.connect(lambda: self.trigger_action("quotes"))
        self.btn_thread.clicked.connect(lambda: self.trigger_action("thread"))
        self.btn_views.clicked.connect(lambda: self.trigger_action("views"))
        
        actions_layout.addWidget(self.btn_quotes)
        actions_layout.addWidget(self.btn_thread)
        actions_layout.addWidget(self.btn_views)
        
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        # Chat Input Area
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)
        
        self.input_field = QLineEdit()
        self.input_field.setObjectName("ChatInput")
        self.input_field.setPlaceholderText("Ask about this page...")
        self.input_field.returnPressed.connect(self.on_ask)
        
        # Wrapper for absolute positioning of button inside LineEdit (simulated via layout)
        input_layout.addWidget(self.input_field)
        
        self.btn_ask = QPushButton("↑")
        self.btn_ask.setObjectName("SendBtn")
        self.btn_ask.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_ask.clicked.connect(self.on_ask)
        
        # Simple hack to put button inside input visual bounds
        self.input_field.setStyleSheet(self.input_field.styleSheet() + "padding-right: 40px;")
        btn_wrapper = QHBoxLayout()
        btn_wrapper.setContentsMargins(0,0,5,0)
        
        # Actually place it outside but looks inside due to negative margin
        input_layout.addWidget(self.btn_ask)
        
        layout.addWidget(input_container)
        
        self.setWidget(container)
        
    def create_action_btn(self, text):
        btn = QPushButton(text)
        btn.setProperty("class", "ActionBtn")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return btn
        
    def get_page_content(self, callback):
        if hasattr(self.parent_window, "get_current_page_text"):
            self.parent_window.get_current_page_text(callback)
        else:
            callback("")
            
    def trigger_action(self, action_type):
        self.get_page_content(lambda text: self.handle_action_response(action_type, text))
        
    def handle_action_response(self, action_type, text):
        # In a real app, this would use self.ai_service
        # We just update the summary text to show it's working for the mockup
        if action_type == "quotes":
            self.summary_text.setText("Key Quote: \"The paradigm is shifting rapidly toward ambient computing...\"")
        elif action_type == "thread":
            self.summary_text.setText("1/ Ambient computing is here. No more screens. \n2/ Predictive agentic workspaces replace the desktop...")
        elif action_type == "views":
            self.summary_text.setText("Opposing View: Privacy concerns limit the viability of always-on ambient microphones and sensors.")
        
    def on_ask(self):
        question = self.input_field.text().strip()
        if not question:
            return
            
        self.input_field.clear()
        self.summary_text.setText(f"You asked: {question}\n\nAI is thinking...")
        
        self.get_page_content(lambda text: self.summary_text.setText(self.ai_service.answer_question(text, question)))
