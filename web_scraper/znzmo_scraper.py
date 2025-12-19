import re
import time
import warnings
from utils.file_utils.file_path_and_creat_folder import create_output_folder
from utils.login_utils.browser_setup import create_driver
from utils.scraper_utils.download_image import download_znzmo_image
from utils.login_utils.cookies_manager import get_or_load_cookies
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt6.QtCore import QObject

class ZnzmoScraper(QObject):
    def __init__(self, key_word, page_count, log_signal=None):
        """
        视觉中国VCG 爬虫类，爬取指定关键词和页数的内容。

        参数：
        key_word: str - 搜索关键词
        page_count: int - 爬取的页数
        log_signal: pyqtSignal (可选) - 用于向 GUI 日志窗口输出信息
        """
        super().__init__()  # 调用父类 QObject 的构造函数
        self.key_word = key_word
        self.page_count = page_count
        self.log_signal = log_signal
        self.driver = create_driver(log_signal=self.log_signal, headless=False)  # 创建浏览器实例
        self.thread_instance = None  # 初始化 thread_instance 属性

        # 尝试获取或加载 cookies
        login_url = "https://www.znzmo.com"  # 替换为实际的登录 URL
        get_or_load_cookies(self.driver, login_url, "znzmo", self.log_signal, login_click_xpath="//*[@id='loginsuccessnews']")

        # 测试访问一个需要登录的页面
        self.driver.get("https://xiaoguotu.znzmo.com/xgt/1112994507.html?hsQuery=河岸")


    def log_message(self, message):
        """日志输出函数，如果 log_signal 存在，则发送信号；否则直接打印"""
        if self.log_signal:
            self.log_signal.emit(message)
        else:
            print(message)


    def scrape(self, custom_base_dir=None):
        """开始爬取指定页数的内容"""
        warnings.filterwarnings("ignore", message=".*SSL.*")

        key_word_clear = self.key_word.replace(' ', '')  # 去除关键词中的空格
        base_url = f"https://xiaoguotu.znzmo.com/xgt/p_{{}}.html?keyword={key_word_clear}&st=21"

        self.log_message('请稍等，正在加载网址')

        try:
            # 获取用户输入的文件夹路径
            output_folder = create_output_folder(base_url, custom_base_dir=custom_base_dir)
            for page in range(1, self.page_count + 1):
                if self.thread_instance and not self.thread_instance.is_running:
                    self.log_message("爬虫任务已终止")
                    break

                self.driver.get(base_url.format(page))
                self.log_message(f"加载第 {page} 页...")
                self._scroll_to_bottom()

                # 使用显示等待确保页面完全加载
                try:
                    post_elements = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, ".components-xiaoguotuComponent-Card-index__listImg__iNBNq"))
                    )
                    self.log_message(f"找到的项目链接数量: {len(post_elements)}")
                except TimeoutException:
                    self.log_message("未找到任何项目链接，可能是页面加载过慢")
                    continue

                # open_folder(output_folder)

                # 提取所有 URL 并存储在一个列表中
                post_urls = [post.get_attribute('href') for post in post_elements if post.get_attribute('href')]

                # 打印所有提取的 URL
                # self.log_message(f"提取到的 URL 列表: {post_urls}")

                # 遍历链接并访问
                for post_url in post_urls:
                    try:
                        if post_url:  # 确保 URL 不为空
                            self._scrape_post(post_url, output_folder, page)

                    except Exception as e:
                        self.log_message(f"处理 URL {post_url} 时出错: {str(e)}")  # 记录错误信息

                self.log_message("<b>所有 URL 提取完成")
        finally:
            self.driver.quit()

    def _scroll_to_bottom(self):
        """滚动到页面底部并等待加载更多内容"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def _scrape_post(self, post_url, output_folder, page):
        try:
            self.log_message(f"正在处理 {post_url}")
            self.driver.get(post_url)

            # 使用显示等待来确保效果图链接加载完毕
            try:
                image_links = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".pages-xiaoguotuDetail-index__image__bdP2o"))
                )
            except TimeoutException:
                self.log_message("未找到任何效果图链接")
                return

                # 使用显示等待查找标题名称
            try:
                title_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".pages-xiaoguotuDetail-index__title__MNhvk"))
                )
                title_name = title_element.text  # 获取标题文本
                self.log_message(f"<b>标题: {title_name}")
            except TimeoutException:
                self.log_message("未找到标题名称")
                return

            # 处理链接，去掉问号后的字符和"water"前缀
            processed_links = []
            for img in image_links:
                try:
                    original_url = img.get_attribute('src')
                    url_without_query = original_url.split('?')[0]
                    processed_url = url_without_query.replace('water', '', 1)
                    processed_links.append(processed_url)
                except StaleElementReferenceException:
                    self.log_message("遇到 stale element reference 错误，跳过当前图片")

            # self.log_message(f"图片链接: {processed_links}")

            # 获取效果图名称
            image_name_element = self.driver.find_element(By.CSS_SELECTOR, ".pages-xiaoguotuDetail-index__title__MNhvk")
            image_name = re.sub(r'[<>:"/\\|?*]', '_', image_name_element.text.strip())

            # 打印所有图片链接并下载
            for i, image_url in enumerate(processed_links):
                # 下载图片
                try:
                    download_znzmo_image(image_url, output_folder, page, i + 1, self.log_signal, title_name)
                except Exception as e:
                    self.log_signal.emit(f"图片下载失败: {e}")

            self.log_message(f"{image_name} 图片已保存")
        except StaleElementReferenceException:
            self.log_message(f"处理 {post_url} 时遇到 stale element reference 错误，跳过该页面")
        except Exception as e:
            self.log_message(f"处理 {post_url} 时出错: {str(e)}")

