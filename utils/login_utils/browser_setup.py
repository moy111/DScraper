import os
import platform
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager



def create_driver(log_signal=None,  headless=True):
    # 设置国内镜像 URL
    MIRROR_URL = "https://registry.npmmirror.com/mirrors/chromedriver"

    """
    创建浏览器驱动函数，根据操作系统选择合适的浏览器：
    - Mac 系统优先使用 Chrome，失败则使用 Safari。
    - Windows 系统优先使用 Chrome，失败则使用 Edge。
    log_signal: pyqtSignal (可选) - 用于向 GUI 日志窗口输出信息。
    """
    # 设置日志
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # 设置日志级别为DEBUG
    handler = logging.StreamHandler()  # 可以使用其他handler，比如FileHandler
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


    def log_message(message):
        """日志输出函数，如果 log_signal 存在，则发送信号；否则直接打印"""
        if log_signal:
            log_signal.emit(message)
        logger.info(message)

    system = platform.system()  # 获取当前操作系统
    # log_message(f"检测到的操作系统: {system}")


    def is_chrome_installed():
        """检查 Chrome 是否安装在 Windows 系统中。"""
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        return os.path.exists(chrome_path) or os.path.exists(
            chrome_path.replace("Program Files", "Program Files (x86)"))


    def install_driver_with_progress(install_func):
        """监控真实下载进度"""
        log_message('正在努力匹配浏览器驱动......（如果没有梯子第一次匹配可能需要2-3分钟）')
        try:
            driver_path = install_func()
            log_message("驱动下载完成！")
            return driver_path
        except Exception as e:
            log_message(f"驱动下载失败，错误: {e}")
            raise


    # 针对 MacOS 系统
    if system == 'Darwin':
        # log_message("检测是否安装了 Chrome 浏览器...")

        # 检查是否安装了 Chrome 浏览器
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            log_message("尝试启动 Chrome 浏览器...")

            try:
                chrome_options = ChromeOptions()

                # # 设置独立的用户数据目录，避免多个实例冲突
                # user_data_dir = f"/tmp/chrome_user_data_{instance_id}"
                # chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
                #
                # # 设置不同的调试端口，避免端口冲突
                # debug_port = 9222 + instance_id
                # chrome_options.add_argument(f"--remote-debugging-port={debug_port}")

                if headless:
                    chrome_options.add_argument("--headless=old")  # 使用旧的headless模式
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-software-rasterizer")
                chrome_options.add_argument("--log-level=3")
                chrome_options.add_argument("--disable-application-cache")  # 禁用应用缓存
                chrome_options.add_argument("--incognito")  # 启用隐身模式（无缓存，无历史）
                chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-features=UserAgentClientHint")
                chrome_options.add_experimental_option("useAutomationExtension", False)
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_argument(
                    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36"
                )

                # 使用国内镜像源安装 ChromeDriver 并监控下载进度
                chrome_service = Service(
                    install_driver_with_progress(
                        lambda: ChromeDriverManager(url=MIRROR_URL).install()
                    )
                )
                driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
                log_message("使用 Chrome 浏览器成功！")
                return driver

            except Exception as chrome_exception:
                log_message(f"Chrome 启动失败，错误信息: {chrome_exception}")

        # 如果 Chrome 没有安装或启动失败，尝试使用 Safari 浏览器
        log_message("尝试使用 Safari 浏览器...")

        try:
            driver = webdriver.Safari()
            log_message("使用 Safari 浏览器成功！")
            return driver

        except Exception as safari_exception:
            log_message(f"Safari 启动失败，错误信息: {safari_exception}")
            log_message("请确保在 Safari 设置中启用 'Allow Remote Automation' 选项。")
            log_message(
                "解决步骤:\n1. 打开 Safari 浏览器。\n2. 在菜单栏中选择 Safari -> Preferences（或按 Command + ,）。\n3. 选择 Advanced 标签。\n4. 勾选 Show Develop menu in menu bar 选项。\n5. 在菜单栏中，点击 Develop 菜单。\n6. 确保勾选了 Allow Remote Automation 选项。")

            raise RuntimeError("Chrome 和 Safari 浏览器均无法启动，请检查浏览器是否安装和配置正确。")

    # 针对 Windows 系统
    elif system == 'Windows':
        # 优先尝试启动 Edge 浏览器
        log_message("尝试启动 Edge 浏览器...")

        try:
            edge_options = EdgeOptions()
            if headless:
                edge_options.add_argument("--headless=old")
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--window-size=1920,1080")
            edge_options.add_argument("--ignore-certificate-errors")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--disable-software-rasterizer")
            edge_options.add_argument("--log-level=3")
            edge_options.add_argument("--disable-application-cache")  # 禁用应用缓存
            edge_options.add_argument("--incognito")  # 启用隐身模式（无缓存，无历史）
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_argument("--disable-features=UserAgentClientHint")
            edge_options.add_experimental_option("useAutomationExtension", False)
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36"
            )

            # 使用 EdgeChromiumDriverManager 自动安装 EdgeDriver
            edge_driver_path = install_driver_with_progress(
                lambda: EdgeChromiumDriverManager().install()
            )
            log_message(f"edge驱动路径： {edge_driver_path}")
            edge_service = EdgeService(edge_driver_path)
            driver = webdriver.Edge(service=edge_service, options=edge_options)
            log_message("使用 Edge 浏览器成功！")
            return driver

        except Exception as edge_exception:
            log_message(f"Edge 启动失败，错误信息: {edge_exception}")

            # Edge 启动失败，尝试启动 Chrome 浏览器
            log_message("未成功启动 Edge，尝试启动 Chrome 浏览器...")

            # if is_chrome_installed():
            try:
                chrome_options = ChromeOptions()
                if headless:
                    chrome_options.add_argument("--headless=old")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-software-rasterizer")
                chrome_options.add_argument("--log-level=3")
                chrome_options.add_argument("--disable-application-cache")  # 禁用应用缓存
                chrome_options.add_argument("--incognito")  # 启用隐身模式（无缓存，无历史）
                chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_argument("--disable-features=UserAgentClientHint")
                chrome_options.add_experimental_option("useAutomationExtension", False)
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_argument(
                    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.2 Safari/537.36"
                )
                # 使用国内镜像源安装 ChromeDriver 并监控下载进度
                chrome_driver_path = install_driver_with_progress(
                    lambda: ChromeDriverManager(url=MIRROR_URL).install()
                )
                log_message(f"chrome驱动路径： {chrome_driver_path}")

                chrome_service = Service(chrome_driver_path)

                driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
                log_message("使用 Chrome 浏览器成功！")
                return driver

            except Exception as chrome_exception:
                log_message(f"Chrome 启动失败，错误信息: {chrome_exception}")
                raise RuntimeError("Chrome 和 Edge 浏览器均无法启动，"
                                   "\n先不慌，请点击以下链接下载最新版本的浏览器再试试："
                                   "\nedge浏览器官方下载: https://www.microsoft.com/zh-cn/edge/download?form=MA13FJ"
                                   "\ngoogle浏览器官方下载: https://www.google.cn/intl/zh-CN/chrome/")

    else:
        log_message("不支持的操作系统！")
        raise RuntimeError("该脚本仅支持 Windows 和 MacOS 系统。")
