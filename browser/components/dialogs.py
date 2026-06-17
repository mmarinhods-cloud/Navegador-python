from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, 
                             QPushButton, QLabel, QDialog, QGraphicsDropShadowEffect)

class MacInputDialog(QDialog):
    def __init__(self, title, instruction, default_text, theme="light", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(420, 200)
        
        self.container = QWidget(self)
        self.container.setObjectName("DialogContainer")
        self.container.setFixedSize(400, 180)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 65))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)
        
        self.label_title = QLabel(title)
        self.label_title.setObjectName("MacTitle")
        
        self.label_instruction = QLabel(instruction)
        self.label_instruction.setObjectName("MacInstruction")
        
        self.input_field = QLineEdit(default_text)
        self.input_field.setObjectName("MacInput")
        self.input_field.setFocus()
        self.input_field.selectAll()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setObjectName("MacCancel")
        self.btn_cancel.setFixedSize(90, 32)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Salvar")
        self.btn_save.setObjectName("MacSave")
        self.btn_save.setFixedSize(90, 32)
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addWidget(self.label_title)
        layout.addWidget(self.label_instruction)
        layout.addWidget(self.input_field)
        layout.addLayout(btn_layout)
        
        self.apply_dialog_theme(theme)

    def apply_dialog_theme(self, theme):
        if theme == "light":
            self.container.setStyleSheet("""
                QWidget#DialogContainer {
                    background-color: #f6f6f6;
                    border: 1px solid #dcdcdc;
                    border-radius: 12px;
                }
                QLabel#MacTitle {
                    color: #111111;
                    font-family: '.AppleSystemUIFont', 'SF Pro', 'Helvetica Neue';
                    font-size: 15px;
                    font-weight: bold;
                    background: transparent;
                }
                QLabel#MacInstruction {
                    color: #555555;
                    font-family: '.AppleSystemUIFont', 'SF Pro';
                    font-size: 12px;
                    background: transparent;
                }
                QLineEdit#MacInput {
                    padding: 6px 10px;
                    min-height: 24px;
                    border-radius: 6px;
                    border: 1px solid #c3c3c3;
                    background-color: #ffffff;
                    color: #000000;
                    font-size: 13px;
                }
                QLineEdit#MacInput:focus {
                    border: 2px solid #007aff;
                }
                QPushButton#MacCancel {
                    background-color: #e3e3e3;
                    color: #333333;
                    border-radius: 6px;
                    font-family: '.AppleSystemUIFont', 'SF Pro';
                    font-size: 13px;
                }
                QPushButton#MacCancel:hover {
                    background-color: #d8d8d8;
                }
                QPushButton#MacSave {
                    background-color: #007aff;
                    color: white;
                    border-radius: 6px;
                    font-family: '.AppleSystemUIFont', 'SF Pro';
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton#MacSave:hover {
                    background-color: #0063cc;
                }
            """)
        else:
            self.container.setStyleSheet("""
                QWidget#DialogContainer {
                    background-color: #2c2c2c;
                    border: 1px solid #404040;
                    border-radius: 12px;
                }
                QLabel#MacTitle {
                    color: #ffffff;
                    font-family: '.AppleSystemUIFont', 'SF Pro', 'Helvetica Neue';
                    font-size: 15px;
                    font-weight: bold;
                    background: transparent;
                }
                QLabel#MacInstruction {
                    color: #aaaaaa;
                    font-family: '.AppleSystemUIFont', 'SF Pro';
                    font-size: 12px;
                    background: transparent;
                }
                QLineEdit#MacInput {
                    padding: 6px 10px;
                    min-height: 24px;
                    border-radius: 6px;
                    border: 1px solid #454545;
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-size: 13px;
                }
                QLineEdit#MacInput:focus {
                    border: 2px solid #0a84ff;
                }
                QPushButton#MacCancel {
                    background-color: #404040;
                    color: #e0e0e0;
                    border-radius: 6px;
                    font-family: '.AppleSystemUIFont', 'SF Pro';
                    font-size: 13px;
                }
                QPushButton#MacCancel:hover {
                    background-color: #4d4d4d;
                }
                QPushButton#MacSave {
                    background-color: #0a84ff;
                    color: white;
                    border-radius: 6px;
                    font-family: '.AppleSystemUIFont', 'SF Pro';
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton#MacSave:hover {
                    background-color: #006bf2;
                }
            """)

    def textValue(self):
        return self.input_field.text()
