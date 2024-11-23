# coding: utf-8
from time import sleep
from tkinter import Widget

from PyQt5.QtCore import QUrl, QSize, QEventLoop, QTimer
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication, QWidget

from qfluentwidgets import NavigationItemPosition, MSFluentWindow, SplashScreen, FluentIcon, setThemeColor
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import AcrylicWindow

from .about_interface import AboutInterface


from .puzzle import PuzzleInterface
from .puzzle_easy import PuzzleEasyInterface
from .puzzle_hard import PuzzleHardInterface
from ..common.config import cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common import resource


class MainWindow(MSFluentWindow):
    # MSFluentWindow

    def __init__(self):
        super().__init__()
        self.initWindow()
        setThemeColor("#1e88e5")
        # 创建子界面
        self.aboutInterface = AboutInterface(self)
        self.puzzleInterface = PuzzleInterface(self)
        self.puzzleEasyInterface = PuzzleEasyInterface(self)
        self.puzzleHardInterface = PuzzleHardInterface(self)
        self.connectSignalToSlot()

        self.initNavigation()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        self.addSubInterface(self.puzzleEasyInterface, FluentIcon.APPLICATION, self.tr('简单'),
                             position=NavigationItemPosition.TOP)
        self.addSubInterface(self.puzzleInterface, FluentIcon.LAYOUT, self.tr('普通'),
                             position=NavigationItemPosition.TOP)
        self.addSubInterface(self.puzzleHardInterface, FluentIcon.CALORIES, self.tr('困难'),
                             position=NavigationItemPosition.TOP)

        self.addSubInterface(
            self.aboutInterface, FluentIcon.COMPLETED, self.tr('关于'), position=NavigationItemPosition.BOTTOM
        )

        self.splashScreen.finish()

    def initWindow(self):
        self.resize(730, 570)
        self.setMinimumWidth(730)
        self.setMinimumHeight(570)
        self.setMaximumSize(730, 570)
        self.setWindowIcon(QIcon(':/app/images/logo.ico'))
        self.setWindowTitle('Puzzle Game')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        self.splashScreen = SplashScreen(QIcon(':/app/images/logo.png'), self)
        self.splashScreen.setIconSize(QSize(150, 150))
        self.splashScreen.raise_()

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())
