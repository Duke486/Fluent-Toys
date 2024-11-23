# coding: utf-8

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QGridLayout, QSizePolicy, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import setFont, PushButton, PrimaryPushButton, TransparentPushButton, LineEdit
from qfluentwidgets import FluentIcon as FIF
from openai import OpenAI
import math

from app.common.style_sheet import StyleSheet


class AiInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()
        self.client = OpenAI(api_key="sk-请在这里输入您的Open-AI兼容API密钥", base_url="https://api.deepseek.com")

    def initUI(self):
        mainLayout = QHBoxLayout(self)

        # 左侧计算器
        calculatorLayout = QVBoxLayout()
        calculatorLayout.setAlignment(Qt.AlignTop)

        self.calculatorLabel = QLabel(self.tr("经济计算"), self)
        setFont(self.calculatorLabel, 24)
        calculatorLayout.addWidget(self.calculatorLabel)

        # 大框
        self.inputLine = LineEdit(self)
        self.inputLine.setAlignment(Qt.AlignRight)
        self.inputLine.setPlaceholderText("请输入表达式")
        self.inputLine.setFixedHeight(self.inputLine.sizeHint().height() * 4)
        setFont(self.inputLine, 28)
        calculatorLayout.addWidget(self.inputLine)

        buttonLayout = QGridLayout()
        number_buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 0), ('.', 3, 1)
        ]
        for text, row, col in number_buttons:
            button = PushButton(text, self)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            buttonLayout.addWidget(button, row, col)
            button.clicked.connect(lambda checked, t=text: self.onButtonClick(t))

        text_buttons = [
            ('利息是', 4, 0), ('税前收入', 4, 1), ('税率是', 4, 2),
            ('存定期', 5, 0), ('年', 5, 1), ('百分点', 5, 2)
        ]
        for text, row, col in text_buttons:
            button = PushButton(text, self)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            buttonLayout.addWidget(button, row, col)
            button.clicked.connect(lambda checked, t=text: self.onButtonClick(t))

        primary_buttons = [
            ('算本利', 0, 3), ('算利息', 1, 3), ('算税额', 2, 3), ('=', 3, 3), ('清空', 6, 0), ('退格', 6, 1)
        ]
        for text, row, col in primary_buttons:
            if text == '=':
                button = PrimaryPushButton(text, self)
            elif text == '清空':
                button = TransparentPushButton(FIF.DELETE, text, self)
            elif text == '退格':
                button = TransparentPushButton(FIF.LEFT_ARROW, text, self)
            else:
                button = PrimaryPushButton(text, self)

            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            buttonLayout.addWidget(button, row, col)
            button.clicked.connect(lambda checked, t=text: self.onButtonClick(t))

        calculatorLayout.addLayout(buttonLayout)

        mainLayout.addLayout(calculatorLayout, 4)

        # 右侧历史
        historyLayout = QVBoxLayout()
        historyLayout.setAlignment(Qt.AlignTop)

        self.historyLabel = QLabel(self.tr("历史记录"), self)
        setFont(self.historyLabel, 24)
        historyLayout.addWidget(self.historyLabel)

        self.historyList = QListWidget(self)
        historyLayout.addWidget(self.historyList)

        mainLayout.addLayout(historyLayout, 3)

        self.setObjectName("economic-calculator-interface")

        self.setMicaStyle()

    def setMicaStyle(self):
        self.resize(1000, 800)
        self.setObjectName('economicCalculatorInterface')
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
                # 发送请求到 API
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是个计算表达式处理专家，你需要把人类写的，在三重中括号内的一个经济计算表达式变成python格式的表达式。你的输出结果只包含一个由三重中括号括起来的python表达式，只能有+-*/,你自己去排好计算顺序。如果你觉得用户输入的表达式根本无法理解，就算是你也不好去修正，那就返回三个中括号引起来的wrong。如果你觉得用户输入的数字太大，例如2的99次方，不适合python来完成，则响应三重中括号围起来的cant。"},
                        {"role": "user", "content": currentText}
                    ],
                    stream=False
                )
                response_text = response.choices[0].message.content.strip()

                if response_text == '[[[wrong]]]' or response_text == '[[[cant]]]':
                    self.inputLine.setText('表达式无法理解或无法计算')
                else:
                    # 执行表达式
                    try:
                        # 导入数学库并计算
                        expression = response_text.strip('[[[]]]')
                        result = eval(expression, {"__builtins__": None}, math.__dict__)
                        self.inputLine.setText(str(result))

                        historyItem = QListWidgetItem(f"{expression} = {result}")
                        self.historyList.addItem(historyItem)
                    except Exception as e:
                        self.inputLine.setText('Python计算错误')
            except Exception as e:
                self.inputLine.setText('API响应超时')
        else:
            self.inputLine.setText(currentText + buttonText)
