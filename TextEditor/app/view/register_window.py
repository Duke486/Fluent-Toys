# coding:utf-8
import sys
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel
from qfluentwidgets import PrimaryPushButton, LineEdit, setThemeColor
from ..common import resource


class RegisterWindow(QWidget):
    """ Register window """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('register-window')
        setThemeColor('#28afe9')
        self.initUI()

    def initUI(self):
        # Set up the main horizontal layout
        self.hBoxLayout = QHBoxLayout(self)
        self.setLayout(self.hBoxLayout)

        # Background image
        self.backgroundPixmap = QPixmap(':/app/images/background.png')

        # Left spacer (3/4 of the width)
        self.hBoxLayout.addStretch(3)

        # Right side layout (1/4 of the width)
        self.rightLayout = QVBoxLayout()
        self.hBoxLayout.addLayout(self.rightLayout, 1)

        # Set layout margins and spacing
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.rightLayout.setContentsMargins(20, 0, 20, 0)
        self.rightLayout.setSpacing(0)
        self.hBoxLayout.setSpacing(0)

        # Vertical centering
        self.rightLayout.addStretch(1)

        # Icon label
        self.iconLabel = QLabel(self)
        self.iconLabel.setPixmap(QIcon(':/app/images/logo.png').pixmap(100, 100))
        self.iconLabel.setAlignment(Qt.AlignCenter)
        self.rightLayout.addWidget(self.iconLabel)
        self.rightLayout.addSpacing(20)

        # Line edit for file name
        self.fileNameLineEdit = LineEdit(self)
        self.fileNameLineEdit.setPlaceholderText('要创建的文件名')
        self.fileNameLineEdit.setClearButtonEnabled(True)
        self.fileNameLineEdit.setFixedWidth(200)
        self.rightLayout.addWidget(self.fileNameLineEdit, alignment=Qt.AlignCenter)
        self.rightLayout.addSpacing(20)

        # Create and Open buttons
        self.createButton = PrimaryPushButton(self.tr('创建'), self)
        self.openButton = PrimaryPushButton(self.tr('打开'), self)
        self.createButton.setFixedWidth(200)
        self.openButton.setFixedWidth(200)
        self.rightLayout.addWidget(self.createButton, alignment=Qt.AlignCenter)
        self.rightLayout.addSpacing(20)
        self.rightLayout.addWidget(self.openButton, alignment=Qt.AlignCenter)

        # Vertical centering
        self.rightLayout.addStretch(1)

        # Set the window style
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_pixmap = self.backgroundPixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding,
                                                     Qt.SmoothTransformation)

        # Calculate position to center the image
        x = (self.width() - scaled_pixmap.width()) // 2
        y = (self.height() - scaled_pixmap.height()) // 2

        painter.drawPixmap(x, y, scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Adjust the right layout to always occupy 1/4 of the window width
        total_width = self.width()
        right_width = total_width // 4
        self.hBoxLayout.setStretch(0, 3)  # Left spacer
        self.hBoxLayout.setStretch(1, 1)  # Right layout
