import os
import time
import warnings
from selenium.webdriver.common.by import By
from utils.file_utils.file_path_and_creat_folder import create_output_folder
from utils.login_utils.browser_setup import create_driver
from utils.scraper_utils.download_image import download_vcg_image


class VCGScraper:
    def __init__(self, key_word, page_count, log_signal=None):
        """
        视觉中国VCG 爬虫类，爬取指定关键词和页数的内容。

        参数：
        key_word: str - 搜索关键词
        page_count: int - 爬取的页数
        log_signal: pyqtSignal (可选) - 用于向 GUI 日志窗口输出信息
        """
        self.key_word = key_word
        self.page_count = page_count
        self.log_signal = log_signal
        self.driver = create_driver(log_signal=self.log_signal)  # 创建浏览器实例

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
        base_url = f"https://www.vcg.com/creative-image/{key_word_clear}/?page={{}}"

        self.log_message('请稍等，正在加载网址')

        try:
            # 获取用户输入的文件夹路径
            output_folder = create_output_folder(base_url, custom_base_dir=custom_base_dir)

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                self.log_message("文件夹创建成功")

            # open_folder(output_folder)

            # 遍历每一页
            for page in range(1, self.page_count + 1):
                self.log_message(f"正在处理第 {page} 页")
                # 构建当前页的 URL
                current_page_url = base_url.format(page)
                self.driver.get(current_page_url)
                time.sleep(2)  # 等待页面加载

                # 存储当前页面所有图片链接
                all_image_urls = set()

                # 模拟滚动加载所有内容
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                while True:
                    # 用find_elements的By查询图片链接，并打印出来调试
                    image_url_elements = self.driver.find_elements(By.XPATH, '//img[@class="lazyload_hk ll_loaded"]')
                    for image in image_url_elements:
                        img_url = image.get_attribute("data-src")
                        if img_url:
                            # 修正 URL
                            if img_url.startswith("//"):
                                img_url = "https:" + img_url
                            all_image_urls.add(img_url)

                    # 向下滚动到页面底部
                    new_height = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # 等待一段时间以确保新内容加载完成
                    time.sleep(3)
                    # 判断是否滚动到底部
                    if new_height == last_height:
                        break
                    last_height = new_height

                # 打印所有图片链接并下载
                for index, url1 in enumerate(all_image_urls, start=1):
                    # self.log_message(url1)
                    try:
                        # 使用你写的 download_vcg_image 函数下载图片
                        download_vcg_image(url1, output_folder, page, index, self.log_signal)  # 这里添加 page 参数
                    except Exception as e:
                        self.log_signal.emit(f"图片下载失败: {e}")

        finally:
            # 关闭浏览器实例
            self.driver.quit()
