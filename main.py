import time

start_time = time.time()
print(f"Python process started: {start_time}")

def log_time(module_name):
    print(f"{module_name} imported at {time.time() - start_time:.3f} seconds")

import qtawesome as qta
log_time("qtawesome")

import logging
log_time("logging")

import sys
log_time("sys")

import traceback
log_time("traceback")

import os
log_time("os")

import keyring
log_time("keyring")

from utils.file_utils.file_path_and_creat_folder import open_folder, get_base_directory
log_time("file_utils")

from utils.licenses_utils.licenses import DisclaimerDialog
log_time("licenses_utils")

from utils.frontend_utils.style import StyleSheetHelper
log_time("frontend_utils")

from PyQt6.QtWidgets import QLineEdit, QHBoxLayout, QFileDialog, QTabWidget, QMessageBox, QApplication, QDialog, QLabel, QVBoxLayout, QPushButton, QWidget, QMenuBar, QMainWindow
log_time("PyQt6.QtWidgets")

from PyQt6.QtGui import QAction
log_time("PyQt6.QtGui QAction")

from PyQt6.QtGui import QIcon, QPalette
log_time("PyQt6.QtGui QIcon, QPalette")

from PyQt6.QtCore import QSize
log_time("PyQt6.QtCore QSize")

from ui.archdaily_window import ArchdailyScraperApp as AS
log_time("ui.archdaily_window")

from ui.vcg_window import VcgScraperApp as VS
log_time("ui.vcg_window")

from ui.gooood_window import GoooodScraperApp as GS
log_time("ui.gooood_window")

from ui.znzmo_window import ZnzmoScraperApp as ZS
log_time("ui.znzmo_window")

from ui.huaban_window import HuabanScraperApp as HS
log_time("ui.huaban_window")

from ui.dianping_window import DianpingScraperApp as DS
log_time("ui.dianping_window")

from ui.xhs_window import XhsScraperApp as XS
log_time("ui.xhs_window")

print(f"所有包导入完成: {time.time() - start_time:.3f} seconds")


current_version = '1.1.0'
app_name = "Crawloo爬虫工具箱"

# 1. 确保日志目录在用户主目录下
log_dir = os.path.join(os.path.expanduser("~"), "crawloo_logs")
try:
    os.makedirs(log_dir, exist_ok=True)
except Exception as e:
    print(f"无法创建日志目录 {log_dir}: {e}")

# 2. 定义日志文件路径
log_file = os.path.join(log_dir, "app.log")

# 3. 自定义强制 flush 的 FileHandler
class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()  # 强制写入，防止日志丢失

# 4. 获取全局 logger
logger = logging.getLogger("crawloo")
logger.setLevel(logging.DEBUG)

# 5. 清理已存在的 handler，防止重复日志
if logger.hasHandlers():
    logger.handlers.clear()

# 6. 定义日志格式
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# 7. 文件日志处理器
try:
    file_handler = FlushFileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as e:
    print(f"无法创建日志文件 {log_file}: {e}")

# 8. 控制台日志处理器
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 9. 兼容 PyInstaller，防止 stdout 丢失
if getattr(sys, 'frozen', False):
    try:
        sys.stdout = open(os.path.join(log_dir, "stdout.log"), "w", encoding="utf-8")
        sys.stderr = sys.stdout
    except Exception as e:
        logger.error(f"无法重定向 stdout/stderr: {e}")

logger.debug("日志系统初始化完成")
print(f"日志系统初始化完成: {time.time()}")

AppName = "com.Crawloo"

# 获取系统是否为深色模式
is_dark_mode = QApplication.palette().color(QPalette.Window).value() < 128
print("Is dark mode:", is_dark_mode)  # 打印出当前模式


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initui()

    def initui(self):
        title_name = f"{app_name}-{current_version}控制台"
        self.setWindowTitle(title_name)
        self.setWindowIcon(QIcon(r'/Users/apple/Downloads/xxx/2344673.icns'))
        self.resize(650, 550)

        # 创建中心窗口
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 创建垂直布局
        layout = QVBoxLayout()

        # # 添加菜单栏
        # self.create_menu()

        # 创建 Tab Widget 来容纳爬虫窗口
        self.tab_widget = QTabWidget()

        # 添加路径选择框
        self.create_path_ui(layout)

        # 初始化爬虫窗口并传递 UI 元素字典
        self.archdaily_tab = AS(self)  # 传递 UI 元素
        self.archdaily_tab.status_signal.connect(self.update_archdaily_status)

        self.vcg_tab = VS(self)  # 传递 UI 元素
        self.vcg_tab.status_signal.connect(self.update_vcg_status)

        self.gooood_tab = GS(self)  # 传递 UI 元素
        self.gooood_tab.status_signal.connect(self.update_gooood_status)

        self.znzmo_tab = ZS(self)  # 传递 UI 元素
        self.znzmo_tab.status_signal.connect(self.update_znzmo_status)

        self.huaban_tab = HS(self)  # 传递 UI 元素
        self.huaban_tab.status_signal.connect(self.update_huaban_status)

        self.dianping_tab = DS(self)  # 传递 UI 元素
        self.dianping_tab.status_signal.connect(self.update_dianping_status)

        self.xhs_tab = XS(self)  # 传递 UI 元素
        self.xhs_tab.status_signal.connect(self.update_xhs_status)

        tab_data = [
            (self.archdaily_tab, "ArchDaily", "mdi.circle-double"),
            (self.vcg_tab, "视觉中国", "mdi.camera"),
            (self.gooood_tab, "Gooood", "mdi.brush"),
            (self.znzmo_tab, "知末效果图", "mdi.image"),
            (self.huaban_tab, "花瓣网", "mdi.link"),
            (self.dianping_tab, "大众点评", "mdi.store"),
            (self.xhs_tab, "小红书", "mdi.book")
        ]

        for i, (tab, name, icon) in enumerate(tab_data):
            self.tab_widget.addTab(tab, name)
            self.tab_widget.setTabIcon(i, qta.icon(icon))


        # 将 Tab Widget 添加到布局
        layout.addWidget(self.tab_widget)

        # 将布局设置到中心窗口
        central_widget.setLayout(layout)

        # 添加状态标签并设置样式
        self.archdaily_status = QLabel("未运行")
        self.vcg_status = QLabel("未运行")
        self.gooood_status = QLabel("未运行")
        self.znzmo_status = QLabel("未运行")
        self.huaban_status = QLabel("未运行")
        self.dianping_status = QLabel("未运行")
        self.xhs_status = QLabel("未运行")

        self.archdaily_status.setStyleSheet(StyleSheetHelper.get_label_style(is_dark_mode))
        self.vcg_status.setStyleSheet(StyleSheetHelper.get_label_style(is_dark_mode))
        self.gooood_status.setStyleSheet(StyleSheetHelper.get_label_style(is_dark_mode))
        self.znzmo_status.setStyleSheet(StyleSheetHelper.get_label_style(is_dark_mode))
        self.huaban_status.setStyleSheet(StyleSheetHelper.get_label_style(is_dark_mode))
        self.dianping_status.setStyleSheet(StyleSheetHelper.get_label_style(is_dark_mode))
        self.xhs_status.setStyleSheet(StyleSheetHelper.get_label_style(is_dark_mode))

        # 创建第一行标签的水平布局
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(QLabel("ArchDaily:"))
        row1_layout.addWidget(self.archdaily_status)
        row1_layout.addWidget(QLabel("视觉中国:"))
        row1_layout.addWidget(self.vcg_status)
        row1_layout.addWidget(QLabel("Gooood:"))
        row1_layout.addWidget(self.gooood_status)
        row1_layout.addWidget(QLabel("知末效果图:"))
        row1_layout.addWidget(self.znzmo_status)
        row1_layout.addWidget(QLabel("花瓣网备份:"))
        row1_layout.addWidget(self.huaban_status)
        row1_layout.addWidget(QLabel("大众点评:"))
        row1_layout.addWidget(self.dianping_status)
        row1_layout.addWidget(QLabel("小红书:"))
        row1_layout.addWidget(self.xhs_status)

        # 将水平布局添加到主垂直布局中
        layout.addLayout(row1_layout)

    def create_path_ui(self, layout):
        """
        创建并添加路径选择框到布局
        """
        path_layout = QHBoxLayout()
        path_label = QLabel("保存路径:")

        # 设置 path_input 为类属性，以便各个爬虫窗口访问
        self.path_input = QLineEdit()
        default_path = get_base_directory()
        self.path_input.setText(default_path)
        self.path_input.setReadOnly(True)

        # 创建选择文件夹按钮并设置图标
        path_button = QPushButton("选择路径")
        path_button.setIcon(qta.icon("mdi.folder-edit-outline"))
        path_button.setIconSize(QSize(20, 20))

        # 创建打开文件夹按钮并设置图标
        open_folder_button = QPushButton("打开路径")
        open_folder_button.setIcon(qta.icon("mdi.folder-outline"))
        open_folder_button.setIconSize(QSize(20, 20))

        path_button.setStyleSheet(StyleSheetHelper.get_path_button_style(is_dark_mode))
        open_folder_button.setStyleSheet(StyleSheetHelper.get_path_button_style(is_dark_mode))

        # 定义选择文件夹功能
        def select_folder():
            folder_path = QFileDialog.getExistingDirectory(self, "选择保存文件夹")
            if folder_path:
                self.path_input.setText(folder_path)  # 更新 path_input 文本

        path_button.clicked.connect(select_folder)
        open_folder_button.clicked.connect(lambda: open_folder(self.path_input.text()))

        # 添加路径选择控件到布局
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_button)
        path_layout.addWidget(open_folder_button)

        layout.addLayout(path_layout)

    def get_main_ui_elements(self):
        """
        返回包含 UI 元素的字典
        """
        # 返回路径输入框和其他元素
        return {
            "path_input": self.path_input,  # 返回保存路径输入框
        }

    def update_archdaily_status(self, status):
        self.archdaily_status.setText(status)

    def update_vcg_status(self, status):
        self.vcg_status.setText(status)

    def update_gooood_status(self, status):
        self.gooood_status.setText(status)

    def update_znzmo_status(self, status):
        self.znzmo_status.setText(status)

    def update_huaban_status(self, status):
        self.huaban_status.setText(status)

    def update_dianping_status(self, status):
        self.dianping_status.setText(status)

    def update_xhs_status(self, status):
        self.xhs_status.setText(status)

# 主程序
def main():
    # 设置高DPI缩放
    # QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # 显示免责声明对话框
    disclaimer_dialog = DisclaimerDialog()
    result = disclaimer_dialog.exec_()

    if result == QDialog.Accepted:
        logging.info("用户同意免责声明，继续执行主程序。")

        main_window = MainApp()
        main_window.show()
    else:
        logging.info("用户未同意免责声明，程序退出。")
        sys.exit(0)

    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # 捕获异常并记录日志
        error_log = os.path.expanduser("~/crawloo_error.log")
        with open(error_log, "w") as f:
            traceback.print_exc(file=f)
        print(f"An error occurred. Check the log file at: {error_log}")
        sys.exit(1)
