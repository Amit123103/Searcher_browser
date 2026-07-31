"""
Searcher Browser - Searcher AI Sidebar
=======================================
Dockable sidebar providing the Searcher AI Assistant interface.
Includes greeting header, quick action cards (Summarize, Ask, Notes, Explain),
interactive chat stream, and real-time page context analysis.
"""

import os
from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QHBoxLayout, 
                             QScrollArea, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QCursor, QPixmap

class SearcherAITitleBar(QWidget):
    """Custom Header Bar for Searcher AI Sidebar."""
    
    def __init__(self, parent_sidebar=None):
        super().__init__(parent_sidebar)
        self.sidebar = parent_sidebar
        self.setFixedHeight(44)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 10, 8)
        layout.setSpacing(8)
        
        # Searcher AI Logo / Icon
        icon_lbl = QLabel()
        icons_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icons"))
        ai_icon_path = os.path.join(icons_dir, "ai_white.svg")
        if os.path.exists(ai_icon_path):
            pix = QIcon(ai_icon_path).pixmap(18, 18)
            icon_lbl.setPixmap(pix)
        layout.addWidget(icon_lbl)
        
        # Title Label: "Searcher AI"
        title_lbl = QLabel("Searcher AI")
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #F8FAFC;")
        layout.addWidget(title_lbl)
        
        layout.addStretch()
        
        # Close Button (X)
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #94A3B8;
                font-size: 14px;
                font-weight: bold;
                width: 24px;
                height: 24px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: #F8FAFC;
            }
        """)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.clicked.connect(self.sidebar.hide)
        layout.addWidget(close_btn)


class AISidebar(QDockWidget):
    """
    Dockable sidebar widget for Searcher AI Assistant.
    """
    
    def __init__(self, ai_service, parent=None):
        super().__init__("Searcher AI", parent)
        self.ai_service = ai_service
        self.parent_window = parent
        
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        
        # Set custom header bar
        self.title_bar = SearcherAITitleBar(self)
        self.setTitleBarWidget(self.title_bar)
        
        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        self.setStyleSheet("""
            QDockWidget {
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QWidget#SidebarContainer {
                background-color: #0F172A;
                border-left: 1px solid rgba(255, 255, 255, 0.08);
            }
            QScrollArea#ChatScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#ChatContentWidget {
                background-color: transparent;
            }
            
            /* Quick Action Card Buttons */
            QPushButton.QuickActionCard {
                background-color: #1E293B;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 14px 16px;
                text-align: left;
                color: #F8FAFC;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton.QuickActionCard:hover {
                background-color: #273549;
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #38BDF8;
            }
            QPushButton.QuickActionCard:pressed {
                background-color: #162032;
            }
            
            /* Chat Bubbles */
            QFrame.UserBubble {
                background-color: #0EA5E9;
                border-radius: 12px;
                padding: 10px 14px;
            }
            QLabel.UserBubbleText {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 500;
            }
            
            QFrame.AIBubble {
                background-color: #1E293B;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 12px 14px;
            }
            QLabel.AIBubbleText {
                color: #F8FAFC;
                font-size: 13px;
                line-height: 1.5;
            }
            
            /* Bottom Input Bar */
            QFrame#InputFrame {
                background-color: #1E293B;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 20px;
                padding: 3px 6px 3px 14px;
            }
            QFrame#InputFrame:focus-within {
                border: 1px solid #38BDF8;
            }
            QLineEdit#ChatInput {
                background-color: transparent;
                border: none;
                color: #F8FAFC;
                font-size: 13px;
            }
            QPushButton#SendBtn {
                background-color: #38BDF8;
                border: none;
                border-radius: 16px;
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
                color: #0F172A;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#SendBtn:hover {
                background-color: #0EA5E9;
                color: #FFFFFF;
            }
        """)

    def setup_ui(self):
        container = QWidget()
        container.setObjectName("SidebarContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Scrollable Chat Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("ChatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ChatContentWidget")
        self.chat_layout = QVBoxLayout(self.scroll_content)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(12)
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        # Render Initial Welcome Screen
        self.render_welcome_screen()

        # Bottom Input Bar (Pill style matching screenshot)
        input_frame = QFrame()
        input_frame.setObjectName("InputFrame")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("ChatInput")
        self.input_field.setPlaceholderText("Ask anything...")
        self.input_field.returnPressed.connect(self.on_ask)
        input_layout.addWidget(self.input_field)

        self.btn_send = QPushButton("➔")
        self.btn_send.setObjectName("SendBtn")
        self.btn_send.setToolTip("Send to Searcher AI")
        self.btn_send.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_send.clicked.connect(self.on_ask)
        input_layout.addWidget(self.btn_send)

        main_layout.addWidget(input_frame)

        self.setWidget(container)

    def render_welcome_screen(self):
        """Renders greeting + quick action cards matching screenshot."""
        self.clear_chat_layout()

        # Greeting Area
        greeting_box = QWidget()
        g_layout = QVBoxLayout(greeting_box)
        g_layout.setContentsMargins(0, 8, 0, 8)
        g_layout.setSpacing(4)

        hello_lbl = QLabel("Hello! 👋")
        hello_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #F8FAFC;")
        
        sub_lbl = QLabel("How can I help you today?")
        sub_lbl.setStyleSheet("font-size: 14px; color: #94A3B8;")

        g_layout.addWidget(hello_lbl)
        g_layout.addWidget(sub_lbl)
        self.chat_layout.addWidget(greeting_box)

        # Quick Action Cards (4 buttons matching screenshot)
        cards = [
            ("📄   Summarize this page", "summarize"),
            ("❓   Ask a question", "ask_mode"),
            ("✍️   Generate notes", "notes"),
            ("💬   Explain this content", "explain"),
        ]

        for text, action_type in cards:
            btn = QPushButton(text)
            btn.setProperty("class", "QuickActionCard")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, a=action_type, t=text: self.on_quick_action(a, t))
            self.chat_layout.addWidget(btn)

        self.chat_layout.addStretch()

    def clear_chat_layout(self):
        """Clears all widgets from the chat scroll layout."""
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def get_page_content(self, callback):
        """Retrieves page text from active tab."""
        if hasattr(self.parent_window, "get_current_page_text"):
            self.parent_window.get_current_page_text(callback)
        else:
            callback("")

    def on_quick_action(self, action_type: str, card_title: str):
        """Triggered when user clicks a Quick Action Card."""
        if action_type == "ask_mode":
            self.input_field.setFocus()
            self.input_field.setPlaceholderText("Type your question about this page...")
            return

        # Add user prompt bubble
        self.add_user_message(card_title.strip())

        # Add thinking indicator
        thinking_widget = self.add_thinking_message()

        # Fetch page text & run AI response
        def _process(page_text):
            thinking_widget.deleteLater()
            if action_type == "summarize":
                response = self.ai_service.summarize(page_text)
            elif action_type == "notes":
                response = self.ai_service.generate_notes(page_text)
            elif action_type == "explain":
                response = self.ai_service.explain_content(page_text)
            else:
                response = self.ai_service.summarize(page_text)
            self.add_ai_message(response)

        self.get_page_content(_process)

    def on_ask(self):
        """Triggered when user submits a query via the input box."""
        question = self.input_field.text().strip()
        if not question:
            return

        self.input_field.clear()
        
        # Display user message bubble
        self.add_user_message(question)

        # Display thinking indicator
        thinking_widget = self.add_thinking_message()

        def _process(page_text):
            thinking_widget.deleteLater()
            response = self.ai_service.answer_question(page_text, question)
            self.add_ai_message(response)

        self.get_page_content(_process)

    def add_user_message(self, text: str):
        """Appends a User Chat Bubble."""
        bubble = QFrame()
        bubble.setProperty("class", "UserBubble")
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(12, 10, 12, 10)
        
        lbl = QLabel(text)
        lbl.setProperty("class", "UserBubbleText")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        # Remove stretch at bottom if present
        self._remove_bottom_stretch()
        self.chat_layout.addWidget(bubble)
        self.chat_layout.addStretch()
        self.scroll_to_bottom()

    def add_ai_message(self, markdown_text: str):
        """Appends a Searcher AI Response Bubble."""
        bubble = QFrame()
        bubble.setProperty("class", "AIBubble")
        layout = QVBoxLayout(bubble)
        layout.setContentsMargins(14, 12, 14, 12)
        
        lbl = QLabel()
        lbl.setProperty("class", "AIBubbleText")
        lbl.setTextFormat(Qt.TextFormat.MarkdownText)
        lbl.setText(markdown_text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        layout.addWidget(lbl)

        self._remove_bottom_stretch()
        self.chat_layout.addWidget(bubble)
        self.chat_layout.addStretch()
        self.scroll_to_bottom()

    def add_thinking_message(self) -> QWidget:
        """Appends a temporary thinking indicator."""
        bubble = QFrame()
        bubble.setProperty("class", "AIBubble")
        layout = QHBoxLayout(bubble)
        layout.setContentsMargins(12, 10, 12, 10)
        
        lbl = QLabel("⏳ Searcher AI is analyzing page content...")
        lbl.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: 500;")
        layout.addWidget(lbl)

        self._remove_bottom_stretch()
        self.chat_layout.addWidget(bubble)
        self.chat_layout.addStretch()
        self.scroll_to_bottom()
        return bubble

    def _remove_bottom_stretch(self):
        """Removes bottom stretch item to append new messages cleanly."""
        if self.chat_layout.count() > 0:
            last_item = self.chat_layout.itemAt(self.chat_layout.count() - 1)
            if last_item.spacerItem():
                self.chat_layout.takeAt(self.chat_layout.count() - 1)

    def scroll_to_bottom(self):
        """Ensures chat automatically scrolls to bottom when new items are added."""
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
