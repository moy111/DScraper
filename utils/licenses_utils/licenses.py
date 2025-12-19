from PyQt6.QtWidgets import QLineEdit, QMessageBox, QDialog, QLabel, QVBoxLayout, QPushButton, QScrollArea, QWidget
import logging
from utils.file_utils.load_datas import resource_path, load_txt_file
import os
import uuid
import requests
import subprocess


def check_license(serial_number, hardware_info):
    """
    校验序列号和设备硬件信息是否已授权。
    :param serial_number: 激活码
    :param hardware_info: 设备硬件信息字典，包含 mac_address, disk_serial, motherboard_serial, cpu_serial
    :return: (is_valid: bool, message: str, expiry_date: Optional[str])
    """
    url = "http://38.147.185.50:5000/validate"
    # 只发送不为空的硬件信息
    data = {k: v for k, v in hardware_info.items() if v}
    data["serial_number"] = serial_number

    logging.info(f"正在向 {url} 发送请求，数据: {data}")

    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()  # 检查 HTTP 请求是否成功

        # 解析服务器响应
        try:
            result = response.json()
        except ValueError as e:
            logging.error(f"服务器返回了无效的 JSON: {response.text}")
            return False, "服务器响应格式错误，请稍后再试", None

        # 打印服务器响应以便调试
        logging.info(f"服务器响应: {result}")

        # 判断是否验证成功
        if result.get("success", False):  # 使用服务器返回的字段 "success"
            expiry_date = result.get("expiry_date", None)  # 获取到期日期
            logging.info(f"许可证验证成功，有效期至: {expiry_date}")
            return True, result.get("message", "许可证验证成功"), expiry_date
        else:
            error_message = result.get("message", "许可证验证失败")
            logging.error(f"验证失败: {error_message}")
            return False, error_message, None

    except requests.exceptions.Timeout:
        logging.error("请求超时")
        return False, "请求超时，请稍后再试", None
    except requests.exceptions.RequestException as e:
        logging.error(f"请求发生异常: {e}")
        return False, f"网络错误：{e}", None


# 激活功能对话框
class ActivationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("激活软件")
        self.setFixedSize(150, 250)

        # 输入框
        self.serial_number_input = QLineEdit(self)
        self.serial_number_input.setPlaceholderText("请输入序列号")

        # 按钮
        self.activate_button = QPushButton("激活", self)
        self.activate_button.clicked.connect(self.activate)

        # 布局
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("请输入序列号激活软件："))
        self.layout.addWidget(self.serial_number_input)
        self.layout.addWidget(self.activate_button)

        # 状态和到期时间标签
        self.status_label = QLabel("", self)
        self.expiry_date_label = QLabel("", self)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.expiry_date_label)

        self.setLayout(self.layout)
        self.result = None

    def activate(self):
        serial_number = self.serial_number_input.text().strip()
        logging.info(f"用户输入的序列号: {serial_number}")

        # 获取硬件信息
        hardware_info = get_hardware_info()
        if not hardware_info:
            QMessageBox.critical(self, "激活失败", "无法获取设备硬件信息，请检查设备配置。")
            logging.error("无法获取设备硬件信息")
            return

        # 调用验证函数
        is_valid, message, expiry_date = check_license(serial_number, hardware_info)

        if is_valid:
            # 在 QMessageBox 中显示激活成功信息和到期日期
            QMessageBox.information(
                self,
                "激活成功",
                f"软件激活成功！\n\n到期日期：{expiry_date}",
            )
            self.result = serial_number  # 保存激活的序列号
            logging.info(f"软件激活成功，保存序列号: {serial_number}")

            # 禁用输入框和按钮
            self.serial_number_input.setDisabled(True)
            self.activate_button.setDisabled(True)
            self.accept()  # 关闭对话框并返回成功
        else:
            # 在 QMessageBox 中显示失败信息
            QMessageBox.critical(
                self,
                "激活失败",
                f"原因：{message}",
            )
            logging.error(f"激活失败，原因: {message}")


# 获取设备的 MAC 地址（假设使用 get_mac_address 函数）
def get_hardware_info():
    hardware_info = {}

    # 获取 MAC 地址
    try:
        # 使用 uuid 获取 MAC 地址
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xFF)
                                for ele in range(0, 8 * 6, 8)][::-1])
        if mac_address and mac_address != "00:00:00:00:00:00":
            hardware_info["mac_address"] = mac_address
            logging.info(f"MAC 地址: {mac_address}")
    except Exception as e:
        logging.error(f"获取 MAC 地址失败: {e}")

    # 获取硬盘序列号
    try:
        if os.name == "nt":  # Windows
            # 使用 PowerShell 获取硬盘序列号
            cmd = 'powershell "Get-PhysicalDisk | Select-Object -Property SerialNumber"'
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            if result:
                hardware_info["disk_serial"] = result.splitlines()[-1].strip()
                logging.info(f"硬盘序列号: {hardware_info['disk_serial']}")
        elif os.name == "posix":  # macOS or Linux
            if "Darwin" in os.uname().sysname:  # macOS
                cmd = "diskutil info / | grep 'Volume UUID'"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                if result:
                    hardware_info["disk_serial"] = result.split(":")[-1].strip()
                    logging.info(f"硬盘序列号 (macOS): {hardware_info['disk_serial']}")
            else:  # Linux
                # 更强的兼容性，通过 lsblk 或其他命令获取硬盘序列号
                cmd = "lsblk -o NAME,SERIAL"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                if result:
                    lines = result.splitlines()
                    for line in lines:
                        if "disk" in line:  # 找到硬盘相关信息
                            hardware_info["disk_serial"] = line.split()[-1]
                            logging.info(f"硬盘序列号 (Linux): {hardware_info['disk_serial']}")
        else:
            logging.warning("无法识别的操作系统类型")
    except Exception as e:
        logging.error(f"获取硬盘序列号失败: {e}")

    # 获取主板序列号
    try:
        if os.name == "nt":  # Windows
            cmd = "wmic baseboard get serialnumber"
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            if result:
                hardware_info["motherboard_serial"] = result.splitlines()[1].strip()  # 获取正确的主板序列号
                # 标准化处理
                hardware_info["motherboard_serial"] = hardware_info["motherboard_serial"].strip('"').strip("'")
                logging.info(f"主板序列号: {hardware_info['motherboard_serial']}")
        elif os.name == "posix":  # macOS or Linux
            if "Darwin" in os.uname().sysname:  # macOS
                cmd = "ioreg -l | grep IOPlatformSerialNumber"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                if result:
                    hardware_info["motherboard_serial"] = result.splitlines()[0].split()[-1]
                    # 标准化处理
                    hardware_info["motherboard_serial"] = hardware_info["motherboard_serial"].strip('"').strip("'")
                    logging.info(f"主板序列号 (macOS): {hardware_info['motherboard_serial']}")
            else:  # Linux
                cmd = "sudo dmidecode -t 2 | grep 'Serial Number'"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                if result:
                    hardware_info["motherboard_serial"] = result.split(":")[-1].strip()
                    # 标准化处理
                    hardware_info["motherboard_serial"] = hardware_info["motherboard_serial"].strip('"').strip("'")
                    logging.info(f"主板序列号 (Linux): {hardware_info['motherboard_serial']}")
        else:
            logging.warning("无法识别的操作系统类型")
    except Exception as e:
        logging.error(f"获取主板序列号失败: {e}")

    # 获取 CPU 序列号
    try:
        if os.name == "nt":  # Windows
            cmd = "wmic cpu get processorid"
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            if result:
                hardware_info["cpu_serial"] = result.splitlines()[1].strip()
                logging.info(f"CPU 序列号: {hardware_info['cpu_serial']}")
        elif os.name == "posix":  # macOS or Linux
            if "Darwin" in os.uname().sysname:  # macOS
                cmd = "sysctl -n machdep.cpu.brand_string"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                if result:
                    hardware_info["cpu_serial"] = result
                    logging.info(f"CPU 序列号 (macOS): {hardware_info['cpu_serial']}")
            else:  # Linux
                cmd = "cat /proc/cpuinfo | grep 'serial'"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                if result:
                    hardware_info["cpu_serial"] = result.split(":")[-1].strip()
                    logging.info(f"CPU 序列号 (Linux): {hardware_info['cpu_serial']}")
        else:
            logging.warning("无法识别的操作系统类型")
    except Exception as e:
        logging.error(f"获取 CPU 序列号失败: {e}")

    return hardware_info


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


