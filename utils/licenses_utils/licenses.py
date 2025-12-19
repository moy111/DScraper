from PyQt6.QtWidgets import QLineEdit, QMessageBox, QDialog, QLabel, QVBoxLayout, QPushButton, QScrollArea, QWidget
import logging
from utils.file_utils.load_datas import resource_path, load_txt_file
import os
import uuid
import requests
import subprocess

class DisclaimerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("免责声明")
        layout = QVBoxLayout()

        # 读取免责声明文件内容
        try:
            disclaimer_text = load_txt_file(resource_path("data/disclaimer_text.txt"))
        except FileNotFoundError:
            disclaimer_text = "免责声明文件未找到。"

        # 创建一个 QScrollArea 并设置内容为 QLabel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # 创建并设置 QLabel 显示免责声明文本
        label = QLabel(disclaimer_text)
        label.setWordWrap(True)
        content_layout.addWidget(label)

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        # 将 QScrollArea 添加到主布局
        layout.addWidget(scroll_area)

        # 同意按钮
        agree_button = QPushButton("我已阅读并同意")
        agree_button.clicked.connect(self.accept)
        layout.addWidget(agree_button)

        # 不同意按钮（退出程序）
        cancel_button = QPushButton("不同意（退出程序）")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.setLayout(layout)


