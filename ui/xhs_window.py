# Xhs_scraper.py
import webbrowser
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QThread, pyqtSignal
from utils.frontend_utils.window_ui import create_common_ui
from utils.scraper_utils import scraper_utils
from web_scraper.xhs_scraper import XhsScraper  # 这里导入你的爬虫代码


# 创建爬虫线程
class XhsScraperThreadClass(QThread):
    log_signal = pyqtSignal(str)
    """
    ScraperThreadClass 继承自 QThread，用于处理爬虫的后台线程。
    该类会在独立线程中执行爬虫任务，防止阻塞主界面，任务完成后会发出信号更新日志信息。
    """
    def __init__(self, keyword, max_links, custom_base_dir):
        super().__init__()
        self.keyword = keyword  # 用户输入的爬虫关键词
        self.max_links = max_links  # 用户输入的最大爬取帖子数量
        self.custom_base_dir = custom_base_dir

    def run(self):
        """
        覆写 run 方法，在线程启动时执行爬虫任务。
        在执行过程中，通过 log_signal 发送日志信息；如果发生异常，则捕获并输出错误信息。
        run 方法会在 ScraperThreadClass(keyword, page_count).start() 启动线程时自动调用。
        """
        try:
            # 直接调用爬虫函数，并传入页数参数
            scraper = XhsScraper(self.keyword, self.log_signal, self.max_links)
            scraper.scrape(custom_base_dir=self.custom_base_dir)  # 调用 scrape 方法启动爬虫
        except Exception as e:
            self.log_signal.emit(f"爬虫执行出错: {str(e)}")


class XhsScraperApp(QWidget):
    status_signal = pyqtSignal(str)  # 定义状态信号，用于同步到主窗口状态栏
    """
    该类负责接收用户输入、启动/停止爬虫任务，并在窗口中显示爬虫状态和日志信息。
    初始化时会加载公共 UI 模板中的元素（如按钮和输入框），并将这些 UI 元素绑定到爬虫控制的相应方法上。
    """
    def __init__(self, main_app):
        """
        初始化爬虫窗口，设置 UI 元素、信号连接，并显示初始状态信息。
        """
        super().__init__()
        self.main_ui_elements = main_app.get_main_ui_elements()  # 保存主窗口的引用

        self.scraper_thread = None  # 初始化爬虫线程为 None

        self.ui_elements = create_common_ui(
            self, "小红书", "访问小红书", self.open_webside, exclude_elements=["district_input", "page_input", "city_input"]
        )  # 加载公共 UI 模板

        # 修改启动按钮文本
        if self.ui_elements["start_button"]:
            self.ui_elements["start_button"].setText("开始爬取小红书帖子图片和评论词云")

        # 获取现有的 placeholder 文本
        existing_placeholder = self.ui_elements["log_placeholder"]
        # 在末尾添加一行新的文本
        new_placeholder = existing_placeholder + "\n（当前网页HTML元素有调整，此版本暂时不可用，欢迎优化）"
        # 更新 log_output 的 placeholderText
        self.ui_elements["log_output"].setPlaceholderText(new_placeholder)

        # 连接 UI 按钮与爬虫启动和停止的功能
        self.ui_elements["start_button"].clicked.connect(self.start_scraper)
        self.ui_elements["stop_button"].clicked.connect(self.stop_scraper)

        # 连接关键词输入框的 Enter 键信号到 start_scraper 方法
        if self.ui_elements["keyword_input"]:
            self.ui_elements["keyword_input"].returnPressed.connect(self.start_scraper)


    # ---被动更新---
    def update_status_all(self, status_text):
        """
        同步更新爬虫窗口和主窗口的状态信息。

        :param status_text: str - 状态信息文本
        """
        scraper_utils.update_status_all(self, status_text)


    def on_scraper_finished(self):
        """
        爬虫完成时，更新爬虫窗口和主窗口的状态。
        """
        scraper_utils.on_scraper_finished(self)

    def update_log(self, message):
        """
        在日志输出窗口中追加日志信息。

        :param message: str - 要显示的日志信息
        """
        log_output = self.ui_elements.get("log_output")
        if log_output:  # 确保 log_output 存在
            log_output.append(message)
        else:
            print("Error: log_output is not initialized")  # 或日志记录错误信息
    # ---被动更新---


    # ---启动停止相关---
    def start_scraper(self):
        """
        启动爬虫任务，检查用户输入的关键词和页数，并调用 scraper_utils 的启动方法。
        """
        # 调用 scraper_utils 中的启动方法，传入 ScraperThreadClass
        scraper_utils.start_scraper(self, XhsScraperThreadClass)


    def stop_scraper(self):
        """
        强制终止正在运行的爬虫线程。
        """
        scraper_utils.stop_scraper(self)
    # ---启动停止相关---

    # ---其他---
    def open_webside(self):
        """打开 小红书 搜索页面"""
        webbrowser.open('https://www.xiaohongshu.com')  # 修改为Dianping的网址
