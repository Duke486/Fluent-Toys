# coding: utf-8
from PyQt5.QtCore import QUrl, QSize, Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QStackedWidget, QWidget

from qfluentwidgets import NavigationItemPosition, FluentWindow, SplashScreen, FluentIcon
from qfluentwidgets import FluentIcon as FIF

from .setting_interface import SettingInterface
from .about_interface import AboutInterface
from .mtexteditor_interface import MultiTextEditorInterface
from .ai import AiAssistantInterface
from .register_window import RegisterWindow
from ..common.config import cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common import resource


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # Create interfaces
        self.settingInterface = SettingInterface(self)
        self.aboutInterface = AboutInterface(self)
        self.textEditorInterface = MultiTextEditorInterface(self)
        self.aiAssistantInterface = AiAssistantInterface(self)
        self.registerWindow = RegisterWindow(self)

        # Add navigation
        self.initNavigation()

        self.connectSignalToSlot()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        # Connect RegisterWindow buttons to their respective actions
        self.registerWindow.createButton.clicked.connect(self.createNewFile)
        self.registerWindow.openButton.clicked.connect(self.openExistingFile)

    def initNavigation(self):
        # Add sub interfaces to the navigation
        self.addSubInterface(self.registerWindow, FIF.HOME, 'Start', NavigationItemPosition.TOP)
        self.addSubInterface(self.textEditorInterface, FIF.EDIT, 'Editor', NavigationItemPosition.TOP)
        self.addSubInterface(self.aiAssistantInterface, FIF.ROBOT, 'AI Assistant', NavigationItemPosition.TOP)
        self.addSubInterface(self.aboutInterface, FIF.INFO, 'About', NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settingInterface, FluentIcon.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        self.splashScreen.finish()

    def initWindow(self):
        self.resize(1200, 850)
        self.setMinimumWidth(660)
        self.navigationInterface.setExpandWidth(250)
        self.navigationInterface.setMinimumExpandWidth(700)
        self.navigationInterface.expand(useAni=False)
        self.setWindowIcon(QIcon(':/app/images/logo.png'))
        self.setWindowTitle('Shizuku Editor')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # Create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(176, 176))
        self.splashScreen.raise_()

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def createNewFile(self):
        file_name = self.registerWindow.fileNameLineEdit.text().strip()
        if file_name:
            self.textEditorInterface.addNewTabWithName(file_name)
            self.navigationInterface.setCurrentIndex(1)  # Switch to the editor page

    def openExistingFile(self):
        self.textEditorInterface.openFile()
        self.navigationInterface.setCurrentIndex(1)  # Switch to the editor page

