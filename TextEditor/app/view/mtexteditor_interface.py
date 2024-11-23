import json
import os
from openai import OpenAI
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QFileDialog, QHBoxLayout, QColorDialog, QCompleter
from PyQt5.QtCore import Qt
from qfluentwidgets import CommandBar, Action, FluentIcon, TabBar, TransparentToolButton, EditableComboBox, \
    PrimaryDropDownPushButton, RoundMenu, MessageBox, SearchLineEdit, ComboBox
from PyQt5.QtGui import QTextCursor, QFont, QColor, QFontDatabase


class MultiTextEditorInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()
        # DeepSeek API 客户端
        self.api_client = OpenAI(api_key="sk-请在这里输入您的Open-AI兼容API密钥", base_url="https://api.deepseek.com")
        # 使用相对路径存储 JSON
        self.state_save_directory = os.path.join(os.path.dirname(__file__), 'json')
        if not os.path.exists(self.state_save_directory):
            os.makedirs(self.state_save_directory)

    def initUI(self):
        # 垂直主布局
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        # 命令栏
        self.commandBar = CommandBar()
        self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.openAction = Action(FluentIcon.FOLDER, '打开文件', triggered=self.openFile)
        self.saveAction = Action(FluentIcon.SAVE, '保存文件', triggered=self.saveFile)
        self.newTabAction = Action(FluentIcon.ADD, '新建标签页', triggered=self.addNewTab)

        self.commandBar.addAction(self.openAction)
        self.commandBar.addSeparator()
        self.commandBar.addAction(self.saveAction)
        self.commandBar.addSeparator()
        self.commandBar.addAction(self.newTabAction)

        # AI 助手按钮
        self.aiAssistantButton = PrimaryDropDownPushButton(FluentIcon.ROBOT, 'AI Assistant')
        self.aiAssistantMenu = RoundMenu(parent=self.aiAssistantButton)
        self.aiAssistantMenu.addAction(Action(FluentIcon.SEND, '续写', triggered=lambda: self.useAIAssistant('extend')))
        self.aiAssistantMenu.addAction(
            Action(FluentIcon.PENCIL_INK, '总结', triggered=lambda: self.useAIAssistant('summarize')))
        self.aiAssistantMenu.addAction(
            Action(FluentIcon.ASTERISK, '头脑风暴', triggered=lambda: self.useAIAssistant('brainstorm')))
        self.aiAssistantMenu.addAction(
            Action(FluentIcon.ACCEPT_MEDIUM, '文法检查', triggered=lambda: self.useAIAssistant('grammar_check')))
        self.aiAssistantButton.setMenu(self.aiAssistantMenu)

        self.commandBar.addSeparator()
        self.commandBar.addWidget(self.aiAssistantButton)
        self.layout.addWidget(self.commandBar)

        self.toolBar = QHBoxLayout()

        # 工具按钮
        self.copyButton = TransparentToolButton(FluentIcon.COPY, self)
        self.copyButton.clicked.connect(self.copyText)
        self.pasteButton = TransparentToolButton(FluentIcon.PASTE, self)
        self.pasteButton.clicked.connect(self.pasteText)
        self.cutButton = TransparentToolButton(FluentIcon.CUT, self)
        self.cutButton.clicked.connect(self.cutText)
        self.undoButton = TransparentToolButton(FluentIcon.CANCEL, self)  # 修改为撤销图标
        self.undoButton.clicked.connect(self.undoText)
        self.deleteButton = TransparentToolButton()  # 修改为删除图标
        self.deleteButton.clicked.connect(self.deleteText)
        self.zoomInButton = TransparentToolButton(FluentIcon.ZOOM_IN, self)
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomOutButton = TransparentToolButton(FluentIcon.ZOOM_OUT, self)
        self.zoomOutButton.clicked.connect(self.zoomOut)
        self.cancelButton = TransparentToolButton(FluentIcon.DELETE, self)  # 修改为取消图标
        self.cancelButton.clicked.connect(self.cancelAction)
        self.alignLeftButton = TransparentToolButton(FluentIcon.LEFT_ARROW, self)
        self.alignLeftButton.clicked.connect(self.alignLeft)
        self.alignCenterButton = TransparentToolButton(FluentIcon.MENU, self)
        self.alignCenterButton.clicked.connect(self.alignCenter)
        self.alignRightButton = TransparentToolButton(FluentIcon.RIGHT_ARROW, self)
        self.alignRightButton.clicked.connect(self.alignRight)
        self.fontColorButton = TransparentToolButton(FluentIcon.FONT_INCREASE, self)
        self.fontColorButton.clicked.connect(self.changeFontColor)

        # 工具栏
        self.toolBar.addWidget(self.copyButton)
        self.toolBar.addWidget(self.pasteButton)
        self.toolBar.addWidget(self.cutButton)
        self.toolBar.addWidget(self.undoButton)
        self.toolBar.addWidget(self.cancelButton)
        self.toolBar.addWidget(self.deleteButton)
        self.toolBar.addWidget(self.zoomInButton)
        self.toolBar.addWidget(self.zoomOutButton)
        self.toolBar.addWidget(self.alignLeftButton)
        self.toolBar.addWidget(self.alignCenterButton)
        self.toolBar.addWidget(self.alignRightButton)
        self.toolBar.addWidget(self.fontColorButton)

        self.fontComboBox = ComboBox()
        self.loadSystemFonts()
        self.fontComboBox.setPlaceholderText("选择字体")
        self.fontComboBox.currentIndexChanged.connect(self.changeFont)
        self.toolBar.addWidget(self.fontComboBox)

        self.fontSizeComboBox = EditableComboBox()
        font_sizes = ['8', '10', '12', '14', '18', '24', '32', '40', '48', '56', '72']
        self.fontSizeComboBox.addItems(font_sizes)
        self.fontSizeComboBox.setPlaceholderText("选择或输入字号大小")
        self.fontSizeComboBox.setCurrentIndex(-1)
        self.fontSizeComboBox.currentTextChanged.connect(self.changeFontSize)
        self.toolBar.addWidget(self.fontSizeComboBox)

        self.searchLineEdit = SearchLineEdit(self)
        self.searchLineEdit.setPlaceholderText("搜索文本")
        self.searchLineEdit.searchSignal.connect(self.searchText)
        self.toolBar.addWidget(self.searchLineEdit)

        self.layout.addLayout(self.toolBar)

        # 标签栏
        self.tabBar = TabBar(self)
        self.tabBar.setMovable(True)
        self.tabBar.setTabMaximumWidth(220)
        self.tabBar.tabCloseRequested.connect(self.removeTab)
        self.tabBar.currentChanged.connect(self.updateEditorVisibility)
        self.layout.addWidget(self.tabBar)

        self.editors = []  # 用于存储 QTextEdit 实例的列表

        # 初始化一个标签页
        self.addNewTab()
        self.setObjectName("multi-text-editor-interface")

    def addNewTab(self):
        # 新 QTextEdit
        newEditor = QTextEdit(self)
        newEditor.setObjectName(f"editor-{len(self.editors)}")
        newEditor.setAcceptRichText(True)
        newEditor.zoomIn(15)

        # 按顺序标签名称
        existing_tab_names = [self.tabBar.tabText(i) for i in range(self.tabBar.count())]
        tabIndex = len(self.editors) + 1
        tabName = f"文档 {tabIndex}"
        while tabName in existing_tab_names:
            tabIndex += 1
            tabName = f"文档 {tabIndex}"

        self.tabBar.addTab(tabName, tabName)
        self.tabBar.setCurrentIndex(len(self.editors))

        self.layout.addWidget(newEditor)
        self.editors.append(newEditor)
        self.updateEditorVisibility()

    def loadSystemFonts(self):
        fontDatabase = QFontDatabase()
        fontFamilies = fontDatabase.families()
        self.fontComboBox.addItems(fontFamilies)

    def openFile(self):
        # 打开文件对话框
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "打开文件", "", "Text Files (*.txt);;All Files (*)",
                                                  options=options)
        if filePath:
            self.addNewTab()
            currentEditor = self.editors[self.tabBar.currentIndex()]

            # 读文件
            with open(filePath, 'r', encoding='utf-8') as file:
                content = file.read()
                currentEditor.setHtml(content)

            # 更新标签名称（bug）
            fileName = os.path.basename(filePath)
            self.tabBar.setTabText(self.tabBar.currentIndex(), fileName)

            # 如果存在相应json，加载状态
            stateFilePath = os.path.join(self.state_save_directory, f"{fileName}.json")
            if os.path.exists(stateFilePath):
                with open(stateFilePath, 'r', encoding='utf-8') as stateFile:
                    state = json.load(stateFile)
                    self.applyEditorState(currentEditor, state)

    def saveFile(self):
        # 保存文件对话框
        if self.tabBar.currentIndex() >= 0:
            currentEditor = self.editors[self.tabBar.currentIndex()]
            options = QFileDialog.Options()
            filePath, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "Text Files (*.txt);;All Files (*)",
                                                      options=options)
            if filePath:
                with open(filePath, 'w', encoding='utf-8') as file:
                    content = currentEditor.toHtml()
                    file.write(content)

                # 更新标签名称（bug）
                fileName = os.path.basename(filePath)
                self.tabBar.setTabText(self.tabBar.currentIndex(), fileName)

                # 保存状态到JSON
                state = self.getEditorState(currentEditor)
                stateFilePath = os.path.join(self.state_save_directory, f"{fileName}.json")
                with open(stateFilePath, 'w', encoding='utf-8') as stateFile:
                    json.dump(state, stateFile, ensure_ascii=False, indent=4)

    def getEditorState(self, editor):
        # 获取编辑器状态
        alignment = editor.alignment()
        if alignment == Qt.AlignLeft:
            alignment_str = 'AlignLeft'
        elif alignment == Qt.AlignCenter:
            alignment_str = 'AlignCenter'
        elif alignment == Qt.AlignRight:
            alignment_str = 'AlignRight'
        else:
            alignment_str = 'AlignJustify'

        return {
            'font': editor.currentFont().family(),
            'fontSize': editor.fontPointSize(),
            'fontColor': editor.textColor().name(),
            'alignment': alignment_str
        }

    def applyEditorState(self, editor, state):
        # 应用编辑器状态
        if 'font' in state:
            editor.setCurrentFont(QFont(state['font']))
        if 'fontSize' in state:
            editor.setFontPointSize(state['fontSize'])
        if 'fontColor' in state:
            editor.setTextColor(QColor(state['fontColor']))
        if 'alignment' in state:
            if state['alignment'] == 'AlignLeft':
                editor.setAlignment(Qt.AlignLeft)
            elif state['alignment'] == 'AlignCenter':
                editor.setAlignment(Qt.AlignCenter)
            elif state['alignment'] == 'AlignRight':
                editor.setAlignment(Qt.AlignRight)
            else:
                editor.setAlignment(Qt.AlignJustify)

    def useAIAssistant(self, task_type):
        # 读上下文
        if self.tabBar.currentIndex() < 0:
            return
        currentEditor = self.editors[self.tabBar.currentIndex()]
        content = currentEditor.toPlainText()[-300:]

        system_message = "你不要说任何废话，你是个API，直接给出正文结果回应。严格显示你的回复长度150字以内。"
        if task_type == 'extend':
            system_message = "当前你要做的是根据给定文本进行续写。警告，别包含任何原文。你只能输出续写部分，user输入内容一个字都不要写出来。" + system_message
        elif task_type == 'summarize':
            system_message = "当前你要做的是对给定文本进行总结，给出简洁的总结。" + system_message
        elif task_type == 'brainstorm':
            system_message = "当前你要做的是根据给定文本进行头脑风暴，分条描述主意。" + system_message
        elif task_type == 'grammar_check':
            system_message = "当前你要做的是对给定文本进行文法检查并给出修正建议。" + system_message

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": content}
        ]

        # 调用 AI API
        response = self.api_client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )

        # 添加 AI 的回复
        ai_response = response.choices[0].message.content
        currentEditor.append(ai_response)

    def removeTab(self, index):
        if len(self.editors) > 1:
            title = "保存更改"
            content = "您想在离开前保存对当前标签页的更改吗？"
            dialog = MessageBox(title, content, self)
            dialog.setClosableOnMaskClicked(True)

            if dialog.exec():
                self.saveFile()
                self._closeTab(index)
            else:
                self._closeTab(index)
        else:
            print("不能移除最后一个标签页！")

    def _closeTab(self, index):
        self.tabBar.removeTab(index)
        editor = self.editors.pop(index)
        self.layout.removeWidget(editor)
        editor.deleteLater()
        self.updateEditorVisibility()

    def copyText(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.copy()

    def pasteText(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.paste()

    def cutText(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.cut()

    def cancelAction(self):
        # 清空当前文本编辑器内容
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.setPlainText("")

    def deleteText(self):
        # 删除选定的文本
        currentEditor = self.editors[self.tabBar.currentIndex()]
        cursor = currentEditor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()

    def zoomIn(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.zoomIn()

    def zoomOut(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.zoomOut()

    def undoText(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.undo()

    def alignLeft(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.setAlignment(Qt.AlignLeft)

    def alignCenter(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.setAlignment(Qt.AlignCenter)

    def alignRight(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        currentEditor.setAlignment(Qt.AlignRight)

    def changeFontColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            currentEditor = self.editors[self.tabBar.currentIndex()]
            currentEditor.setTextColor(color)

    def changeFont(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        font_name = self.fontComboBox.currentText()
        font = QFont(font_name)
        currentEditor.setCurrentFont(font)

    def changeFontSize(self):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        size_text = self.fontSizeComboBox.currentText()
        if size_text.isdigit():
            size = int(size_text)
            currentEditor.setFontPointSize(size)

    def searchText(self, text):
        currentEditor = self.editors[self.tabBar.currentIndex()]
        document = currentEditor.document()

        cursor = QTextCursor(document)
        pattern = text
        occurrences = []  #匹配

        while not cursor.isNull() and not cursor.atEnd():
            cursor = document.find(pattern, cursor)
            if not cursor.isNull():
                occurrences.append(QTextCursor(cursor))

        # 用setcursor高亮
        if occurrences:
            self.currentSearchIndex = 0
            self.searchOccurrences = occurrences
            currentEditor.setTextCursor(occurrences[0])
            self.updateSearchStatus()

    def updateSearchStatus(self):
        if hasattr(self, 'searchOccurrences') and self.searchOccurrences:
            total = len(self.searchOccurrences)
            current = self.currentSearchIndex + 1
            self.searchLineEdit.setToolTip(f"<{current}/{total}>")

    def updateEditorVisibility(self):
        currentIndex = self.tabBar.currentIndex()
        for i, editor in enumerate(self.editors):
            editor.setVisible(i == currentIndex)
