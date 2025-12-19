import json
import os
import re
import time
import warnings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.login_utils.browser_setup import create_driver
from utils.file_utils.file_path_and_creat_folder import create_output_folder
from utils.scraper_utils.download_image import download_project_image


class ArScraper:
    """
    ArchDaily 爬虫函数，爬取指定关键词和页数的内容。

    参数：
    key_word: str - 搜索关键词
    page_count: int - 爬取的页数
    log_signal: pyqtSignal (可选) - 用于向 GUI 日志窗口输出信息
    thread_instance: ScraperThread (可选) - 用于检查爬虫状态
    """


    def __init__(self, key_word, page_count, log_signal=None, thread_instance=None):
        self.key_word = key_word.replace(' ', '')  # 去除关键词中的空格
        self.page_count = page_count
        self.log_signal = log_signal
        self.thread_instance = thread_instance
        self.driver = create_driver(log_signal=self.log_signal)

    def scrape(self, custom_base_dir=None):
        """开始爬取指定页数的内容"""
        warnings.filterwarnings("ignore", message=".*SSL.*")
        base_url = f"https://www.archdaily.cn/search/cn/all?q={self.key_word}&page={{}}"

        try:
            # 获取用户输入的文件夹路径
            output_folder = create_output_folder(base_url, custom_base_dir=custom_base_dir)
            self.log_message('正在加载ArchDaily页面...')
            all_links = self._get_all_links(base_url)
            # open_folder(output_folder)  # 打开文件夹
            self._process_links(all_links, output_folder)
            self.log_message("所有页面爬取完成")
        finally:
            self.driver.quit()

    def _get_all_links(self, base_url):
        """获取所有页面的链接"""
        all_links = []  # 用于存储所有页的链接
        for current_page in range(1, self.page_count + 1):
            if self.thread_instance and not self.thread_instance.is_running:
                self.log_message("爬虫任务已终止")
                break

            # 构建当前页面的 URL
            url = base_url.format(current_page)
            self.driver.get(url)
            self.log_message(f"加载第 {current_page} 页内容，URL: {url}")

            # 使用显示等待，确保页面加载完成
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//a[@class="gridview__content"]'))
                )
            except TimeoutException:
                self.log_message("加载页面超时，请检查网络或页面结构。")
                break

            # 获取当前页的所有项目链接
            final_page_links = self.driver.find_elements(By.XPATH, '//a[@class="gridview__content"]')
            page_links = [link.get_attribute('href') for link in final_page_links]

            # 汇总本页获取到的所有链接
            all_links.extend(page_links)
            self.log_message(f"第 {current_page} 页获取到 {len(page_links)} 个链接")

        return all_links

    def _process_links(self, all_links, output_folder):
        """处理每个链接，获取项目信息和图片"""
        for link in all_links:
            self.log_message(f"正在处理链接: {link}")
            if self.thread_instance and not self.thread_instance.is_running:
                self.log_message("爬虫任务已终止")
                break

            self._process_single_link(link, output_folder)

    def _process_single_link(self, link, output_folder):
        """处理单个项目链接"""
        try:
            self.driver.get(link)

            # 设置等待时间，例如10秒
            next_page_article = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//article//p")))
            article_text = [element.text for element in next_page_article]
            combined_texts = '\n'.join(article_text)
            cleaned_combined_texts = re.sub(r'\s+', ' ', combined_texts)
            self.log_message(f"已获取正文：\n{cleaned_combined_texts[:20]}...")

            # 获取项目名字
            project_name = self._get_project_name()

            # 创建项目文件夹
            folder_path = self._create_project_folder(output_folder, project_name)

            # 获取项目信息并保存
            project_info_str = self._get_project_info(link, cleaned_combined_texts)

            self._save_project_info(folder_path, project_info_str)

            # 下载图片
            self._download_images(link, folder_path)

        except Exception as e:
            self.log_message(f"处理链接 {link} 时发生错误: {e}")

    def _get_project_name(self):
        """获取项目名称"""
        xpath_expression = (
            '//h1[@class="afd-title-big '
            'afd-title-big--full '
            'afd-title-big--bmargin-big '
            'afd-relativeposition "]'
        )
        project_name_elements = self.driver.find_elements(By.XPATH, xpath_expression)
        if project_name_elements:
            name_text = project_name_elements[0].text
            return name_text.split('/')[0].strip() if '/' in name_text else name_text.strip()
        return "未知项目"

    def _create_project_folder(self, output_folder, project_name):
        """创建项目文件夹"""
        folder_path = os.path.join(output_folder, project_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            # self.log_message(f"Folder {project_name} Created!")
        return folder_path

    def _get_project_info(self, link, cleaned_combined_texts):
        """获取项目信息"""
        # 获取项目名称
        project_name = self._get_project_name()

        project_info_elements = self.driver.find_elements(By.XPATH, '//div[@class="afd-specs"]')
        project_info = [area.text for area in project_info_elements if area.text]
        project_info_str = '\n'.join(project_info)
        project_info_str = re.sub(r'•', '', project_info_str)
        project_info_str = re.sub(r'\n\s*\n', '\n', project_info_str)
        project_info_str = re.sub(r'\n\s+', '\n', project_info_str)
        project_info_str = project_info_str.replace('面积: \n', '面积: ')
        project_info_str = project_info_str.replace('项目年份: \n', '项目年份: ')

        # 构建完整的项目概述信息
        full_project_info = (
            f"项目名称: {project_name}\n\n"
            f"{project_info_str}\n\n"
            f"项目链接: {link}\n"
            f"正文内容:\n{cleaned_combined_texts}"
        )

        return full_project_info

    def _save_project_info(self, folder_path, project_info_str):
        """将项目信息保存到文本文件中"""
        info_file_path = os.path.join(folder_path, '项目信息概要.text')
        with open(info_file_path, 'w', encoding='utf-8') as file:
            file.write(project_info_str)
        # self.log_message(f"项目信息已保存: {info_file_path}")

    def _download_images(self, link, folder_path):
        """下载图片"""
        try:
            # 用于获取图片链接的代码，添加显示等待
            image_elements_href = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[@class="js-image-size__link "]'))
            )
            image_href_web = image_elements_href.get_attribute('href')

            # 用第三个浏览器实例打开大图网页
            self.driver.get(image_href_web)
            time.sleep(3)

            # 等待大图页面加载特定元素，例如图片元素
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="afd-gal-items js-gal-slide-animate"]'))
            )

            # 提取 data-images 属性的值
            data_images = element.get_attribute('data-images')

            # 解析 JSON 数据
            data_images_list = json.loads(data_images)

            # 遍历列表并提取 "url_slideshow" 的值并下载
            for i, item in enumerate(data_images_list):
                url_slideshow = item.get("url_slideshow")
                if url_slideshow:
                    download_project_image(url_slideshow, folder_path, i + 1, self.log_signal)  # 使用已实现的下载方法

        except Exception as e:
            self.log_message(f"下载图片时发生错误: {e}")

    def log_message(self, message):
        """日志输出函数，如果 log_signal 存在，则发送信号；否则直接打印"""
        if self.log_signal:
            self.log_signal.emit(message)
        else:
            print(message)
