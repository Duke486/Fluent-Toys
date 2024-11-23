from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit
from qfluentwidgets import ComboBox, LineEdit, setFont
from PyQt5.QtCore import Qt
import base64


class BaseConversionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self, calculatorLayout=None):
        main_layout = QVBoxLayout()  # 垂直布局
        main_layout.setAlignment(Qt.AlignCenter)
        self.setObjectName("baseConversionWidget")

        caption_label = QLabel("进制转换器")
        setFont(caption_label, 24)
        caption_label.move(36, 50)
        # caption_label.setAlignment(Qt.AlignCenter)
        # caption_label.setProperty("pixelFontSize", 33)
        main_layout.addWidget(caption_label)

        input_layout = QVBoxLayout()
        input_layout.setAlignment(Qt.AlignCenter)

        self.input_line_edit = LineEdit()
        self.input_line_edit.setPlaceholderText("0")
        self.input_line_edit.setFixedWidth(300)
        self.input_line_edit.textChanged.connect(self.perform_conversion)
        input_layout.addWidget(self.input_line_edit)

        self.base_combo_box = ComboBox()
        self.base_combo_box.addItems(["二进制", "八进制", "十进制", "十六进制"])
        self.base_combo_box.setFixedWidth(300)
        self.base_combo_box.currentIndexChanged.connect(self.perform_conversion)
        input_layout.addWidget(self.base_combo_box)

        main_layout.addLayout(input_layout)

        # 垂直布局输出区域
        output_layout = QVBoxLayout()
        output_layout.setAlignment(Qt.AlignCenter)

        self.output_fields = {}
        bases = ["二进制", "八进制", "十进制", "十六进制", "Base64"]
        for base in bases:
            label = QLabel(base)
            label.setFont(QFont("微软雅黑", 13))
            label.setAlignment(Qt.AlignCenter)
            output_layout.addWidget(label)

            line_edit = LineEdit()
            line_edit.setFont(QFont("微软雅黑", 13))
            line_edit.setReadOnly(True)
            line_edit.setFixedWidth(300)
            output_layout.addWidget(line_edit)

            self.output_fields[base] = line_edit

        main_layout.addLayout(output_layout)

        self.setLayout(main_layout)
        self.base_combo_box.setCurrentIndex(2)  # 默认当成十进制

    def perform_conversion(self):
        input_text = self.input_line_edit.text()
        base_from = self.base_combo_box.currentText()
        try:
            # 输入的进制是什么
            if base_from == "二进制":
                number = int(input_text, 2)
            elif base_from == "八进制":
                number = int(input_text, 8)
            elif base_from == "十进制":
                number = int(input_text, 10)
            elif base_from == "十六进制":
                if input_text.startswith("0x"):
                    input_text = input_text[2:]
                number = int(input_text, 16)
            else:
                self.clear_outputs()
                return

            # 显示用的文本框
            self.output_fields["二进制"].setText(bin(number)[2:])
            self.output_fields["八进制"].setText(oct(number)[2:])
            self.output_fields["十进制"].setText(str(number))
            self.output_fields["十六进制"].setText(hex(number)[2:].upper())
            self.output_fields["Base64"].setText(
                base64.b64encode(number.to_bytes((number.bit_length() + 7) // 8, 'big')).decode(
                    'utf-8') if number > 0 else "")
        except ValueError:
            # Handle invalid input
            self.clear_outputs()

    def clear_outputs(self):
        for field in self.output_fields.values():
            field.setText("")


# Example usage
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = BaseConversionWidget()
    window.show()
    sys.exit(app.exec_())
