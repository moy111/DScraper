# 还没解决cookie登陆的问题

import time
import warnings
from selenium.webdriver.common.by import By
from utils.file_utils.file_path_and_creat_folder import create_output_folder
from utils.login_utils.browser_setup import create_driver
from utils.scraper_utils.download_image import download_vcg_image
from utils.login_utils.cookies_manager import get_or_load_cookies


class PinScraper:
    def __init__(self, key_word, log_signal=None):
        """
        Pinterest 爬虫类，用于爬取指定关键词的图片内容。

        参数：
        key_word: str - 搜索关键词
        log_signal: pyqtSignal (可选) - 用于向 GUI 日志窗口输出信息
        """
        self.key_word = key_word
        self.log_signal = log_signal
        self.driver = create_driver(log_signal=self.log_signal)  # 创建浏览器实例
        self.all_image_urls = set()

    def log_message(self, message):
        """日志输出函数，如果 log_signal 存在，则发送信号；否则直接打印"""
        if self.log_signal:
            self.log_signal.emit(message)
        else:
            print(message)

    def load_cookies(self, url):
        """加载并应用 Pinterest 网站的 Cookies"""
        self.driver.get(url)
        get_or_load_cookies(self.driver, url)
        self.driver.refresh()
        self.log_message("加载Cookies完成，免登录成功")

    def scrape(self, custom_base_dir=None):
        """开始爬取内容，收集图片链接并下载图片"""
        warnings.filterwarnings("ignore", message=".*SSL.*")
        key_word_clear = self.key_word.replace(' ', '')  # 去除关键词中的空格
        base_url = f"https://www.pinterest.com/search/pins/?q={key_word_clear}&rs=typed"
        self.load_cookies(base_url)
        self.log_message('请稍等，正在加载网址...')

        # 设置文件夹路径
        folder_path = create_output_folder(base_url, custom_base_dir=custom_base_dir)
        self.log_message(f"文件夹创建成功：{folder_path}")

        # 开始滚动和图片链接收集
        self._collect_image_links()

        # 下载图片
        self._download_images(folder_path)

    def _collect_image_links(self):
        """滚动页面并收集所有图片链接"""
        scroll_step = 1000  # 每次滚动的像素步长
        max_scroll_time = 100  # 最大滚动时间（秒）
        start_time = time.time()
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            img_elements = self.driver.find_elements(By.XPATH, '//img[@alt]')
            for link in img_elements:
                srcset = link.get_attribute('srcset')
                src = link.get_attribute('src')
                if srcset:
                    for entry in srcset.split(','):
                        url, descriptor = entry.strip().split(' ')
                        if descriptor == '4x':  # 仅添加高分辨率图片
                            self.all_image_urls.add(url)
                elif src:
                    self.all_image_urls.add(src)

            self.log_message(f"当前收集到的图片链接数: {len(self.all_image_urls)}")

            # 向下滚动页面并等待加载
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # 检查是否滚动到底部
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or time.time() - start_time > max_scroll_time:
                break
            last_height = new_height

    def _download_images(self, folder_path):
        """下载所有收集到的图片"""
        for url in self.all_image_urls:
            download_vcg_image(url, folder_path, log_signal=self.log_signal)

    def close(self):
        """关闭浏览器驱动"""
        if self.driver:
            self.driver.quit()
