from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QSizePolicy, QFileDialog)
from PyQt5.QtCore import Qt, QSize, QUrl, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPainterPath, QColor
from qfluentwidgets import (PushButton, ComboBox, FluentIcon as FIF,
                            PrimaryPushButton, setFont, FluentIcon,
                            MessageBox, MessageBoxBase, SubtitleLabel)
from app.common.style_sheet import StyleSheet
import random


class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.index = -1
        self.empty = False
        self.setStyleSheet("""
            ClickableLabel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            ClickableLabel:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)

    def mousePressEvent(self, event):
        if not self.empty:
            self.clicked.emit(self.index)


class PuzzleGridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(2)
        self.setLayout(self.layout)


class ImagePreviewBox(MessageBoxBase):
    def __init__(self, image: QPixmap, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('原图预览')

        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        scaled_image = image.scaled(
            400, 400,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.imageLabel.setPixmap(scaled_image)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.imageLabel)

        self.cancelButton.hide()
        self.yesButton.setText("关闭")

        self.widget.setMinimumWidth(450)
        self.widget.setMinimumHeight(500)


class PuzzleHardInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.current_empty = 24
        self.labels = []
        self.current_image = None
        self.piece_pixmaps = []
        self.current_positions = list(range(25))
        self.moving = False
        self.initUI()

    def initUI(self):
        mainLayout = QHBoxLayout(self)

        puzzleLayout = QVBoxLayout()
        puzzleLayout.setAlignment(Qt.AlignTop)

        self.puzzleGridWidget = PuzzleGridWidget(self)
        self.gridLayout = self.puzzleGridWidget.layout

        for i in range(25):
            label = ClickableLabel(self.puzzleGridWidget)
            label.setFixedSize(96, 96)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            label.index = i
            label.clicked.connect(self.labelClicked)
            self.labels.append(label)
            self.gridLayout.addWidget(label, i // 5, i % 5)

        puzzleLayout.addWidget(self.puzzleGridWidget)

        controlLayout = QVBoxLayout()
        controlLayout.setAlignment(Qt.AlignTop)
        controlLayout.setSpacing(20)

        self.levelLabel = QLabel("关卡：未选择", self)
        setFont(self.levelLabel, 16)
        controlLayout.addWidget(self.levelLabel)

        self.levelComboBox = ComboBox(self)
        self.levelComboBox.setPlaceholderText("选择关卡")
        self.levelComboBox.addItems(["点击选择图片", "和泉纱雾", "初音未来", "高木同学", "Zero Two","自定义"])
        self.levelComboBox.currentIndexChanged.connect(self.onLevelChanged)
        controlLayout.addWidget(self.levelComboBox)

        self.fileButton = PushButton(FIF.FOLDER, "选择图片", self)
        self.fileButton.clicked.connect(self.selectImage)
        self.fileButton.hide()
        controlLayout.addWidget(self.fileButton)

        self.shuffleButton = PrimaryPushButton(FIF.SYNC, "打乱", self)
        self.shuffleButton.clicked.connect(self.shufflePuzzle)
        controlLayout.addWidget(self.shuffleButton)

        self.solveButton = PrimaryPushButton(FIF.COMPLETED, "一键通关", self)
        self.solveButton.clicked.connect(self.solvePuzzle)
        controlLayout.addWidget(self.solveButton)

        self.showImageButton = PushButton(FluentIcon.PHOTO, "查看原图", self)
        self.showImageButton.clicked.connect(self.showOriginalImage)
        controlLayout.addWidget(self.showImageButton)

        mainLayout.addLayout(puzzleLayout, 4)
        mainLayout.addLayout(controlLayout, 1)

        self.setObjectName("puzzle-hard-interface")
        self.setMicaStyle()

    def setMicaStyle(self):
        self.resize(800, 600)
        self.setObjectName('puzzleHardInterface')
        StyleSheet.SETTING_INTERFACE.apply(self)
        self.setStyleSheet("QWidget{background:transparent}")

    def onLevelChanged(self, index):
        if index == 5:
            self.fileButton.show()
        else:
            self.fileButton.hide()
            default_images = ["", ":/app/images/sagiri.jpg", ":/app/images/miku.png", ":/app/images/takagi.jpg", ":/app/images/02.png"]
            if index < len(default_images):
                self.loadImage(default_images[index])

    def selectImage(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.bmp)"
        )
        if fileName:
            self.loadImage(fileName)

    def loadImage(self, image_path):
        try:
            self.current_image = QPixmap(image_path)
            size = min(self.current_image.width(), self.current_image.height())
            self.current_image = self.current_image.copy(
                (self.current_image.width() - size) // 2,
                (self.current_image.height() - size) // 2,
                size, size
            )
            self.splitImage()
            self.current_positions = list(range(25))
            self.updateDisplay()
            file_name = image_path.split('/')[-1]
            if len(file_name) > 4:
                file_name = file_name[:4] + '...' if any(
                    '\u4e00' <= char <= '\u9fff' for char in file_name) else file_name[:6] + '...'
            self.levelLabel.setText(f"关卡：{file_name}")
        except Exception as e:
            MessageBox(
                "错误",
                f"加载图片时出错: {str(e)}",
                self
            ).exec()

    def splitImage(self):
        if not self.current_image:
            return

        self.piece_pixmaps = []
        piece_size = self.current_image.width() // 5
        for i in range(25):
            row = i // 5
            col = i % 5
            piece = self.current_image.copy(
                col * piece_size,
                row * piece_size,
                piece_size,
                piece_size
            )
            piece = piece.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.piece_pixmaps.append(piece)

    def updateDisplay(self):
        if not self.piece_pixmaps:
            return

        for i, label in enumerate(self.labels):
            current_piece = self.current_positions[i]
            if current_piece == 24:
                label.clear()
                label.empty = True
            else:
                label.setPixmap(self.piece_pixmaps[current_piece])
                label.empty = False

    def shufflePuzzle(self):
        if not self.piece_pixmaps or self.moving:
            return

        empty_index = self.current_positions.index(24)
        current_empty = empty_index

        for _ in range(200):
            possible_moves = []
            row = current_empty // 5
            col = current_empty % 5

            if row > 0: possible_moves.append(current_empty - 5)
            if row < 4: possible_moves.append(current_empty + 5)
            if col > 0: possible_moves.append(current_empty - 1)
            if col < 4: possible_moves.append(current_empty + 1)

            next_empty = random.choice(possible_moves)
            self.current_positions[current_empty], self.current_positions[next_empty] = \
                self.current_positions[next_empty], self.current_positions[current_empty]
            current_empty = next_empty

        self.updateDisplay()

    def labelClicked(self, clicked_index):
        if not self.piece_pixmaps or self.moving:
            return

        self.moving = True
        try:
            empty_index = self.current_positions.index(24)
            row1, col1 = clicked_index // 5, clicked_index % 5
            row2, col2 = empty_index // 5, empty_index % 5

            if abs(row1 - row2) + abs(col1 - col2) == 1:
                self.current_positions[clicked_index], self.current_positions[empty_index] = \
                    self.current_positions[empty_index], self.current_positions[clicked_index]
                self.updateDisplay()
                self.checkCompletion()
        finally:
            self.moving = False

    def checkCompletion(self):
        if self.current_positions == list(range(25)):
            self.labels[24].setPixmap(self.piece_pixmaps[24])
            self.labels[24].empty = False
            MessageBox(
                "恭喜",
                "恭喜你完成拼图！",
                self
            ).exec()

    def solvePuzzle(self):
        if not self.piece_pixmaps or self.moving:
            return

        self.current_positions = list(range(25))
        self.updateDisplay()
        self.labels[24].setPixmap(self.piece_pixmaps[24])
        self.labels[24].empty = False

    def showOriginalImage(self):
        if not self.current_image:
            return

        preview_dialog = ImagePreviewBox(self.current_image, self)
        preview_dialog.exec()
