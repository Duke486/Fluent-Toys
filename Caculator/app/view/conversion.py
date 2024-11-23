from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton
from qfluentwidgets import ComboBox, SwitchButton, LineEdit, PrimaryPushButton, setFont
from PyQt5.QtCore import Qt


class UnitConversionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # 垂直
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        self.setObjectName("unitConversionWidget")
        caption_label = QLabel("单位换算")
        setFont(caption_label, 24)
        caption_label.move(36, 50)
        # caption_label.setAlignment(Qt.AlignCenter)
        # caption_label.setProperty("pixelFontSize", 33)
        main_layout.addWidget(caption_label)
        # 选单位
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        self.mode_combo_box = ComboBox()
        self.mode_combo_box.addItems(['温度', '面积', '体积', '长度', '重量', '速度', '压力', '能量'])
        self.mode_combo_box.currentIndexChanged.connect(self.update_unit_selection)
        self.mode_combo_box.setCurrentIndex(0)  # Set default to the first option
        self.mode_combo_box.setFixedWidth(200)  # Increase width of the mode selection combo box
        header_layout.addWidget(self.mode_combo_box)

        self.switch_button = SwitchButton()
        self.switch_button.setOnText("实时显示结果")
        self.switch_button.setOffText("手动点击计算")
        self.switch_button.setChecked(True)
        self.switch_button.checkedChanged.connect(self.toggle_calculation_mode)
        header_layout.addWidget(self.switch_button)

        main_layout.addLayout(header_layout)

        # 垂直（输入区）
        conversion_layout = QVBoxLayout()
        conversion_layout.setAlignment(Qt.AlignCenter)

        # 框框1
        input_layout_1 = QVBoxLayout()
        input_layout_1.setAlignment(Qt.AlignCenter)
        self.input_line_edit_1 = LineEdit()
        self.input_line_edit_1.setPlaceholderText("输入值")
        self.input_line_edit_1.setFixedWidth(200)  # Adjust width of input box
        self.input_line_edit_1.textChanged.connect(self.perform_conversion)
        self.unit_combo_box_1 = ComboBox()
        self.unit_combo_box_1.setFixedWidth(200)  # Match width to input box
        self.unit_combo_box_1.currentIndexChanged.connect(self.perform_conversion)  # Recalculate when unit changes
        input_layout_1.addWidget(self.input_line_edit_1)
        input_layout_1.addWidget(self.unit_combo_box_1)

        conversion_layout.addLayout(input_layout_1)


        equals_label = QLabel("=")
        equals_label.setAlignment(Qt.AlignCenter)
        equals_label.setProperty("pixelFontSize", 29)  # Adjust font size
        conversion_layout.addWidget(equals_label)

        # 框框2
        input_layout_2 = QVBoxLayout()
        input_layout_2.setAlignment(Qt.AlignCenter)
        self.input_line_edit_2 = LineEdit()
        self.input_line_edit_2.setPlaceholderText("转换后的值")
        self.input_line_edit_2.setFixedWidth(200)  # Adjust width of input box
        self.input_line_edit_2.setReadOnly(True)
        self.unit_combo_box_2 = ComboBox()
        self.unit_combo_box_2.setFixedWidth(200)  # Match width to input box
        self.unit_combo_box_2.currentIndexChanged.connect(self.perform_conversion)  # Recalculate when unit changes
        input_layout_2.addWidget(self.input_line_edit_2)
        input_layout_2.addWidget(self.unit_combo_box_2)

        conversion_layout.addLayout(input_layout_2)

        main_layout.addLayout(conversion_layout)

        # 手动计算
        self.calculate_button = PrimaryPushButton("计算")
        self.calculate_button.clicked.connect(self.perform_conversion)
        self.calculate_button.setVisible(False)
        main_layout.addWidget(self.calculate_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.update_unit_selection(0)  # Initialize unit selection

    def update_unit_selection(self, index):
        units = []
        if index == 0:  # Temperature
            units = ["摄氏度", "华氏度", "开尔文"]
        elif index == 1:  # Area
            units = ["平方米", "平方公里", "平方英尺", "英亩"]
        elif index == 2:  # Volume
            units = ["升", "毫升", "立方米", "加仑"]
        elif index == 3:  # Length
            units = ["米", "公里", "英尺", "英里"]
        elif index == 4:  # Weight
            units = ["千克", "克", "磅", "盎司"]
        elif index == 5:  # Speed
            units = ["米每秒", "公里每小时", "英里每小时"]
        elif index == 6:  # Pressure
            units = ["帕斯卡", "巴", "标准大气压"]
        elif index == 7:  # Energy
            units = ["焦耳", "千卡", "电子伏特"]

        self.unit_combo_box_1.clear()
        self.unit_combo_box_2.clear()
        self.unit_combo_box_1.addItems(units)
        self.unit_combo_box_2.addItems(units)

        # 默认选1
        self.input_line_edit_1.setText("1")
        self.perform_conversion()

    def toggle_calculation_mode(self, checked):
        # Toggle between real-time calculation and manual mode
        self.calculate_button.setVisible(not checked)
        if checked:
            self.input_line_edit_1.textChanged.connect(self.perform_conversion)
        else:
            self.input_line_edit_1.textChanged.disconnect(self.perform_conversion)

    def perform_conversion(self):
        try:
            value = float(self.input_line_edit_1.text())
            unit_from = self.unit_combo_box_1.currentText()
            unit_to = self.unit_combo_box_2.currentText()
            result = self.convert_units(value, unit_from, unit_to)
            self.input_line_edit_2.setText(str(result))
        except ValueError:
            self.input_line_edit_2.setText("只允许数字")

    def convert_units(self, value, unit_from, unit_to):
        if unit_from == unit_to:
            return value

        conversion_factors = {
            # Length conversions
            ("米", "公里"): 0.001,
            ("公里", "米"): 1000,
            ("米", "英尺"): 3.28084,
            ("英尺", "米"): 1 / 3.28084,
            ("公里", "英里"): 0.621371,
            ("英里", "公里"): 1.60934,
            # Weight conversions
            ("千克", "磅"): 2.20462,
            ("磅", "千克"): 1 / 2.20462,
            ("克", "盎司"): 0.035274,
            ("盎司", "克"): 1 / 0.035274,
            # Volume conversions
            ("升", "毫升"): 1000,
            ("毫升", "升"): 0.001,
            ("升", "加仑"): 0.264172,
            ("加仑", "升"): 1 / 0.264172,
            ("立方米", "升"): 1000,
            ("升", "立方米"): 0.001,
            # Area conversions
            ("平方米", "平方公里"): 0.000001,
            ("平方公里", "平方米"): 1000000,
            ("平方米", "平方英尺"): 10.7639,
            ("平方英尺", "平方米"): 1 / 10.7639,
            ("平方米", "英亩"): 0.000247105,
            ("英亩", "平方米"): 4046.86,
            # Speed conversions
            ("米每秒", "公里每小时"): 3.6,
            ("公里每小时", "米每秒"): 1 / 3.6,
            ("公里每小时", "英里每小时"): 0.621371,
            ("英里每小时", "公里每小时"): 1.60934,
            # Pressure conversions
            ("帕斯卡", "巴"): 0.00001,
            ("巴", "帕斯卡"): 100000,
            ("帕斯卡", "标准大气压"): 0.00000986923,
            ("标准大气压", "帕斯卡"): 101325,
            # Energy conversions
            ("焦耳", "千卡"): 0.000239006,
            ("千卡", "焦耳"): 4184,
            ("焦耳", "电子伏特"): 6.242e+18,
            ("电子伏特", "焦耳"): 1.60218e-19,
            # Temperature conversions
            ("摄氏度", "华氏度"): lambda c: c * 9 / 5 + 32,
            ("华氏度", "摄氏度"): lambda f: (f - 32) * 5 / 9,
            ("摄氏度", "开尔文"): lambda c: c + 273.15,
            ("开尔文", "摄氏度"): lambda k: k - 273.15,
            ("华氏度", "开尔文"): lambda f: (f - 32) * 5 / 9 + 273.15,
            ("开尔文", "华氏度"): lambda k: (k - 273.15) * 9 / 5 + 32,
        }

        try:
            if (unit_from, unit_to) in conversion_factors:
                factor_or_function = conversion_factors[(unit_from, unit_to)]
                if callable(factor_or_function):
                    return factor_or_function(value)
                else:
                    return value * factor_or_function
            else:
                return "转换失败"
        except KeyError:
            return "转换失败"


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = UnitConversionWidget()
    window.show()
    sys.exit(app.exec_())
