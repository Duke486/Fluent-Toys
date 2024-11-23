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
from .calculator import CalculatorInterface
from .ai import AiInterface
from .conversion import UnitConversionWidget
from .base import BaseConversionWidget

from ..common.config import cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common import resource


class MainWindow(MSFluentWindow):
    # 继承了MSFluentWindow类

    def __init__(self):
        super().__init__()
        self.initWindow()
        setThemeColor("#1e88e5")

        # 创建需要的子界面
        self.aboutInterface = AboutInterface(self)
        self.calculatorInterface = CalculatorInterface(self)
        self.aiInterface = AiInterface(self)
        self.conversionInterface = UnitConversionWidget(self)
        self.baseConversionInterface = BaseConversionWidget(self)
        self.connectSignalToSlot()

        self.initNavigation()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        self.addSubInterface(self.calculatorInterface, FluentIcon.DEVELOPER_TOOLS, self.tr('标准'),
                             position=NavigationItemPosition.TOP)
        self.addSubInterface(self.conversionInterface, FluentIcon.SPEED_HIGH, self.tr('换算'),
                             position=NavigationItemPosition.TOP)
        self.addSubInterface(self.baseConversionInterface, FluentIcon.CODE, self.tr('进制转换'),position=NavigationItemPosition.TOP)
        self.addSubInterface(self.aiInterface, FluentIcon.IOT, self.tr('AI经济'),
                             position=NavigationItemPosition.TOP)

        self.addSubInterface(
            self.aboutInterface, FluentIcon.COMPLETED, self.tr('关于'), position=NavigationItemPosition.BOTTOM
        )

        self.splashScreen.finish()

    def initWindow(self):
        self.resize(650, 470)
        self.setMinimumWidth(630)
        self.setWindowIcon(QIcon(':/app/images/logo.ico'))
        self.setWindowTitle('计算器')

        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # 加载闪屏
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
