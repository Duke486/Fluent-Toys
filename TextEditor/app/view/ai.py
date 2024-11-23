from openai import OpenAI
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from qfluentwidgets import (FluentIcon, PrimaryPushButton, PlainTextEdit,
                            TransparentToolButton)
from collections import deque


class AiAssistantInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("aiAssistantInterface")
        self.chat_history = deque(maxlen=6)  # Store last 6 messages (3 rounds)
        self.initUI()
        self.api_client = OpenAI(
            api_key="sk-请在这里输入您的Open-AI兼容API密钥",
            base_url="https://api.deepseek.com"
        )

    def initUI(self):
        # 布局
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        # 左半边AI
        self.leftLayout = QVBoxLayout()
        self.layout.addLayout(self.leftLayout, 2)

        self.titleLabel = QLabel("AI 写作助手-哀酱")
        self.titleLabel.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.leftLayout.addWidget(self.titleLabel)

        # 聊天
        self.chatArea = QWidget()
        self.chatLayout = QVBoxLayout(self.chatArea)
        self.chatLayout.setSpacing(10)
        self.chatLayout.addStretch()

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.chatArea)
        self.leftLayout.addWidget(self.scrollArea)

        # 输入
        self.inputText = PlainTextEdit()
        self.inputText.setPlaceholderText("与我聊天或帮您写作吧！")
        self.inputText.setFont(QFont("Microsoft YaHei", 11))
        self.inputText.setFixedHeight(100)
        self.leftLayout.addWidget(self.inputText)


        self.sendButton = PrimaryPushButton("发送")
        self.sendButton.setIcon(FluentIcon.SEND)
        self.sendButton.setFont(QFont("Microsoft YaHei", 11))
        self.sendButton.clicked.connect(self.handleUserMessage)
        self.leftLayout.addWidget(self.sendButton)

        # 右半边
        self.rightLayout = QVBoxLayout()
        self.layout.addLayout(self.rightLayout, 1)

        self.rightTitleLayout = QHBoxLayout()
        self.rightTitle = QLabel("Editor 画布")
        self.rightTitle.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.rightTitle.setAlignment(Qt.AlignCenter)
        self.copyButton = TransparentToolButton(FluentIcon.COPY)
        self.copyButton.clicked.connect(self.copyEditorContent)
        self.rightTitleLayout.addWidget(self.rightTitle)
        self.rightTitleLayout.addWidget(self.copyButton)
        self.rightLayout.addLayout(self.rightTitleLayout)

        self.editorContent = PlainTextEdit()
        self.editorContent.setReadOnly(True)
        self.editorContent.setFont(QFont("Microsoft YaHei", 12))
        self.rightLayout.addWidget(self.editorContent)

    def createMessageLabel(self, text, is_user=False):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Microsoft YaHei", 11))
        label.setMaximumWidth(400)
        label.setMinimumHeight(30)

        if is_user:
            label.setStyleSheet("""
                background-color: #0078D4;
                color: white;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            """)
        else:
            label.setStyleSheet("""
                background-color: white;
                color: black;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            """)

        container = QWidget()
        layout = QHBoxLayout(container)
        if is_user:
            layout.addStretch()
        layout.addWidget(label)
        if not is_user:
            layout.addStretch()

        self.chatLayout.insertWidget(self.chatLayout.count() - 1, container)
        return label

    def format_chat_history(self):
        history = []
        for i, (role, content) in enumerate(self.chat_history):
            speaker = "User" if role == "user" else "AI"
            history.append(f"{speaker}: {content}")
        return "\n".join(history)

    def handleUserMessage(self):
        user_text = self.inputText.toPlainText().strip()
        if not user_text:
            return

        # 用户消息
        history_text = self.format_chat_history()
        api_message = f"{user_text}\n###\n{history_text}\n###"

        # 显示用户消息
        self.createMessageLabel(user_text, is_user=True)
        self.chat_history.append(("user", user_text))

        # 问API
        ai_response = self.callAI(api_message)
        self.displayAIMessage(ai_response)

        # 格式化，显示AI消息
        clean_response = ai_response
        start = clean_response.find("***")
        if start != -1:
            end = clean_response.find("***", start + 3)
            if end != -1:
                clean_response = clean_response[:start].strip() + clean_response[end + 3:].strip()
        self.chat_history.append(("assistant", clean_response))

        self.inputText.clear()

        # 划到底
        self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().maximum()
        )

    def displayAIMessage(self, response):
        start = response.find("===")
        end = response.find("===", start + 3) if start != -1 else -1

        if start != -1 and end != -1:
            content_to_display = response[start + 3:end].strip()
            response = response[:start].strip() + response[end + 3:].strip()
        else:
            content_to_display = ""

        self.createMessageLabel(response, is_user=False)

        if content_to_display:
            self.editorContent.setPlainText(content_to_display)

    def callAI(self, user_text):
        messages = [{"role": "system",
                     "content": """你是灰原哀，原名宫野志保，被黑衣组织喂下AIPC4869之后变成人工智能助手。其他设定遵照名侦探柯南。
             你很擅长写作，你童趣可爱，但略显高冷。这只是设定，用户问你的时候没必要全盘托出，用自己的话来阐述就好了。
             聊天内容正常回复，只有写作或列举的内容才需要放在三重等于号内。任何聊天或者说明性话语不需要放入。注意，当且仅当用户让你写作内容才需要这样，平时对话不需要用。
             禁用markdown语法，你必须在三重等号之前回应一下用户。例子：\"以下是我写的诗歌，您可以在画布区域查看。===这里是作品===\" \"这是我的伙伴们，我们之间友谊深厚。===这里是列举===\"
             用户的输入中三重井号(###)之间的内容是历史对话记录，请据此保持对话的连贯性，但不要在回复中念出这些记录。"""},
                    {"role": "user", "content": user_text}]




        # Add current user message

        response = self.api_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )

        return response.choices[0].message.content

    def copyEditorContent(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.editorContent.toPlainText())