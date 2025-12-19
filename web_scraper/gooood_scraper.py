import os
import re
import warnings
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.login_utils.browser_setup import create_driver
from utils.scraper_utils.download_image import download_project_image
from utils.file_utils.file_path_and_creat_folder import create_output_folder

class Goooodscraper:

    def __init__(self, key_word, page_count, log_signal=None, thread_instance=None):
        self.key_word = key_word.replace(' ', '')  # 去除关键词中的空格
        self.page_count = page_count
        self.log_signal = log_signal
        self.thread_instance = thread_instance
        self.driver = create_driver(log_signal=self.log_signal)


    def log_message(self, message):
        """日志输出函数，如果 log_signal 存在，则发送信号；否则直接打印"""
        if self.log_signal:
            self.log_signal.emit(message)
        else:
            print(message)

    def scrape(self, custom_base_dir=None):
        """开始爬取指定页数的内容"""
        warnings.filterwarnings("ignore", message=".*SSL.*")
        base_url = f"https://www.gooood.cn/search/{self.key_word}/page/{{}}"

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

                # 获取所有文章链接
                post_links = [post.get_attribute('href') for post in
                              self.driver.find_elements(By.XPATH, '//div[@class="post-thumbnail"]//a')]

                # 遍历链接并访问
                for post_url in post_links:
                    self._scrape_post(post_url, output_folder)

            self.log_message("所有页数已完成爬取")

        finally:
            self.driver.quit()

    def _scroll_to_bottom(self):
        """滚动到页面底部并等待加载更多内容"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    def _scrape_post(self, post_url, output_folder):
        """爬取每个文章的详细内容"""
        self.log_message(f"正在处理{post_url}")
        self.driver.get(post_url + "?lang=cn")
        project_name = self._get_text(By.XPATH, '//h1[@class="entry-title"]').split('/')[0].strip()
        folder_path = os.path.join(output_folder, project_name)
        os.makedirs(folder_path, exist_ok=True)

        design_company = self._get_elements_text('//div[@class="entry-spec"]/div[1]//a')
        site = self._get_elements_text('//div[@class="entry-spec"]/div[2]//a')
        project_class = self._get_elements_text('//div[@class="entry-spec"]/div[3]//a')
        materials = self._get_elements_text('//div[@class="entry-spec"]/div[4]//a')
        labels = self._get_elements_text('//div[@class="entry-spec"]/div[5]//a')
        classification = self._get_elements_text('//div[@class="entry-spec"]/div[6]//a')

        project_info = (
            f"设计公司：\t{design_company}\n"
            f"位置：\t\t{site}\n"
            f"类型：\t\t{project_class}\n"
            f"材料：\t\t{materials}\n"
            f"标签：\t\t{labels}\n"
            f"分类：\t\t{classification}\n"
            f"项目链接：{post_url}\n"
        )
        with open(os.path.join(folder_path, '项目信息概要.text'), 'w', encoding='utf-8') as f:
            f.write(project_info)

        image_elements = self.driver.find_elements(By.XPATH, '//a[@class="colorbox_gallery"]/img')
        for i, image in enumerate(image_elements):
            image_src = re.sub(r'-\d+x\d+', '', image.get_attribute('src'))
            download_project_image(image_src, folder_path, i, self.log_signal)  # 注意 image_number 参数为 i

        self.log_message(f"{project_name} 信息和图片已保存")

    def _get_text(self, by, path):
        """获取元素文本，如果元素不存在则返回空字符串"""
        try:
            return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((by, path))).text
        except:
            return ""

    def _get_elements_text(self, xpath):
        """获取符合条件的所有元素的文本列表"""
        return [elem.text for elem in self.driver.find_elements(By.XPATH, xpath)]
