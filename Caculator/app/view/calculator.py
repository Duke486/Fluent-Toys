# coding: utf-8

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QGridLayout, QSizePolicy, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import setFont, PushButton, PrimaryPushButton, TransparentPushButton, LineEdit, FluentIcon
from qfluentwidgets import FluentIcon as FIF

from app.common.style_sheet import StyleSheet


class CalculatorInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        mainLayout = QHBoxLayout(self)

        # 计算器那边
        calculatorLayout = QVBoxLayout()
        calculatorLayout.setAlignment(Qt.AlignTop)

        self.calculatorLabel = QLabel(self.tr("标准计算器"), self)
        setFont(self.calculatorLabel, 24)
        self.calculatorLabel.move(36, 50)
        calculatorLayout.addWidget(self.calculatorLabel)

        # 大框框
        self.inputLine = LineEdit(self)
        self.inputLine.setAlignment(Qt.AlignRight)
        self.inputLine.setPlaceholderText("0")
        self.inputLine.setFixedHeight(self.inputLine.sizeHint().height() * 4)
        setFont(self.inputLine, 36)
        calculatorLayout.addWidget(self.inputLine)

        # 按钮阵列
        buttonLayout = QGridLayout()
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('÷', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('×', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3),
            ('0', 3, 0), ('.', 3, 1), ('+', 3, 2), ('=', 3, 3, 2, 1),
            ('清空', 4, 0), ('退格', 4, 1),('重记', 4, 2)
        ]

        for text, row, col, *span in buttons:
            if text == '清空':
                button = TransparentPushButton(FIF.DELETE, text, self)
            elif text == '退格':
                button = TransparentPushButton(FIF.LEFT_ARROW, text, self)
            elif text == '=':
                button = PrimaryPushButton(text, self)
            elif text == '重记':
                button = TransparentPushButton(FluentIcon.HISTORY,text, self)
            else:
                button = PushButton(text, self)

            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            buttonLayout.addWidget(button, row, col, *(span if span else [1, 1]))
            button.clicked.connect(lambda checked, t=text: self.onButtonClick(t))

        calculatorLayout.addLayout(buttonLayout)

        mainLayout.addLayout(calculatorLayout, 4)

        # 右边历史记录
        historyLayout = QVBoxLayout()
        historyLayout.setAlignment(Qt.AlignTop)

        self.historyLabel = QLabel(self.tr("历史记录"), self)
        setFont(self.historyLabel, 24)
        self.historyLabel.move(36, 50)
        historyLayout.addWidget(self.historyLabel)

        self.historyList = QListWidget(self)
        stands = []

        for stand in stands:
            item = QListWidgetItem(stand)
            self.historyList.addItem(item)

        historyLayout.addWidget(self.historyList)
        mainLayout.addLayout(historyLayout, 3)

        self.setObjectName("calculator-interface")

        self.setMicaStyle()

    def setMicaStyle(self):
        self.resize(1000, 800)
        self.setObjectName('calculatorInterface')
        StyleSheet.SETTING_INTERFACE.apply(self)
        self.setStyleSheet("QWidget{background:transparent}")

    def onButtonClick(self, buttonText):
        currentText = self.inputLine.text()
        if buttonText == '清空':
            self.inputLine.setText('')
        elif buttonText == '退格':
            self.inputLine.setText(currentText[:-1])
        elif buttonText == '=':
            try:
                # 替换÷和×
                expression = currentText.replace('÷', '/').replace('×', '*')
                result = eval(expression)
                self.inputLine.setText(str(result))

                historyItem = QListWidgetItem(f"{currentText} = {result}")
                self.historyList.addItem(historyItem)
            except ZeroDivisionError:
                self.inputLine.setText('除数为零')
            except Exception:
                self.inputLine.setText('输入不合法')
        elif buttonText == '重记':
            self.historyList.clear()
        else:
            self.inputLine.setText(currentText + buttonText)
