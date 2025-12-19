import os
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.login_utils.browser_setup import create_driver
from utils.login_utils.cookies_manager import get_or_load_cookies
from utils.scraper_utils.download_image import download_project_image
from utils.file_utils.file_path_and_creat_folder import create_output_folder


class Huabanscraper:

    def __init__(self, key_word, log_signal=None, thread_instance=None):
        self.key_word = key_word.strip()  # 去除前后空格
        self.log_signal = log_signal
        self.thread_instance = thread_instance

        # 验证用户输入是否为有效链接
        if not self.is_valid_huaban_user_url(self.key_word):
            self.log_message("<font color='#FEBC2E'>链接似乎无效哦，请检查主页链接有没有粘贴错～\n链接应该长这个样子：https://huaban.com/user/xxxx")
            raise ValueError("无效链接")

        # 创建浏览器实例
        self.driver = create_driver(log_signal=self.log_signal, headless=False)

        # 尝试获取或加载 cookies
        login_url = "https://huaban.com"  # 替换为实际的登录 URL
        get_or_load_cookies(self.driver, login_url, "huaban", self.log_signal, login_click_xpath="//*[@id='__next']/main/div[1]/div/div/div[4]")

        # 加载用户画板页面
        self.driver.get(self.key_word)


    def is_valid_huaban_user_url(self, url):
        """
        验证是否为花瓣网用户主页的有效链接
        """
        pattern = re.compile(
            r'^https://huaban\.com/user/[a-zA-Z0-9]+/?$'
        )
        return bool(pattern.match(url))

    def log_message(self, message):
        """日志输出函数，如果 log_signal 存在，则发送信号；否则直接打印"""
        if self.log_signal:
            self.log_signal.emit(message)
        else:
            print(message)

    def scrape(self, custom_base_dir=None):
        """
        备份画板，通过逐步滚动提取画板链接并处理。

        :param custom_base_dir: 自定义的输出文件夹路径
        """
        base_url = "https://huaban.com"
        self.log_message('请稍等，正在加载网址')
        post_urls = set()  # 用集合去重
        try:
            # 获取用户输入的文件夹路径
            output_folder = create_output_folder(base_url, custom_base_dir=custom_base_dir)

            # 确保页面完全加载
            WebDriverWait(self.driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # **首次提取初始链接**
            self.log_message("页面初次加载完成，提取初始内容...")
            time.sleep(2)  # 初始加载等待时间
            all_links = {
                re.sub(r'_fw.*$', '', post.get_attribute("href"))
                for post in self.driver.find_elements(By.XPATH, "//div[@class='oyIO61fv']/a")
                if post.get_attribute("href")
            }
            self.log_message(f"初始提取的链接数量: {len(all_links)}")
            post_urls.update(all_links)

            # 滚动逻辑
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            no_change_count = 0  # 页面高度不变且无新链接的计数器
            attempts = 0
            max_attempts = 100
            wait_time = 1.5
            scroll_step = 500  # 每次滚动的距离
            no_change_limit = 5  # 连续无法滚动且无新链接的最大次数

            while attempts < max_attempts:
                # **逐步滚动**
                self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                self.log_message(f"第 {attempts + 1} 次滚动，滚动 {scroll_step} 像素...")
                time.sleep(wait_time)  # 等待加载

                # **滚动后提取当前页面的链接**
                self.log_message("提取滚动后加载的内容...")
                current_links = {
                    re.sub(r'_fw.*$', '', post.get_attribute("href"))
                    for post in self.driver.find_elements(By.XPATH, "//div[@class='oyIO61fv']/a")
                    if post.get_attribute("href")
                }
                new_links = current_links - post_urls
                self.log_message(f"新增链接数量: {len(new_links)}")
                post_urls.update(new_links)

                # **检查页面高度变化**
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height and not new_links:
                    # 仅在页面高度无变化且无新链接时递增计数器
                    no_change_count += 1
                    self.log_message(f"页面高度未变化且无新链接，第 {no_change_count} 次检测到此情况。")
                    if no_change_count >= no_change_limit:
                        self.log_message("页面连续多次无法滚动且无新链接，停止滚动。")
                        break
                else:
                    # 重置计数器
                    last_height = new_height
                    no_change_count = 0

                attempts += 1

            if attempts == max_attempts:
                self.log_message("达到最大滚动次数，可能仍有未加载的内容。")

            self.log_message(f"滚动结束，总提取到的画板链接数量: {len(post_urls)}")

            # 遍历提取的链接并访问
            for post_url in post_urls:
                try:
                    if post_url:  # 确保 URL 不为空
                        self._scrape_post(post_url, output_folder)
                except Exception as e:
                    self.log_message(f"处理 URL {post_url} 时出错: {str(e)}")
        finally:
            self.driver.quit()

    def _scrape_post(self, post_url, output_folder):
        try:
            self.log_message(f"正在处理画板: {post_url}")
            self.driver.get(post_url)

            # 滚动并提取图片链接
            all_image_links = self._scroll_and_extract_links()

            # 提取画板标题
            try:
                self.log_message("开始提取画板标题...")
                board_title_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[@class='nvk0Il6c']"))
                )
                board_title = board_title_element.text.strip()
                self.log_message(f"提取到的标题: {board_title}")

                # 替换非法字符，确保作为文件夹名合法
                safe_board_title = re.sub(r'[\\/:*?"<>|]', '_', board_title)
                board_output_folder = os.path.join(output_folder, safe_board_title)
                os.makedirs(board_output_folder, exist_ok=True)
                self.log_message(f"画板子文件夹创建成功: {board_output_folder}")

                # 下载图片
                for i, image_url in enumerate(all_image_links):
                    try:
                        download_project_image(image_url, board_output_folder, i + 1, self.log_signal)
                    except Exception as e:
                        self.log_message(f"图片下载失败: {e}")
            except TimeoutException:
                self.log_message("未找到标题元素，跳过画板。")
            except Exception as e:
                self.log_message(f"提取标题时发生错误: {e}")
        except Exception as e:
            self.log_message(f"处理画板 {post_url} 时出错: {e}")

    def _scroll_and_extract_links(self, max_attempts=200, wait_time=0.5, scroll_step=300, no_change_limit=10):
        """
        逐步滚动页面，每次滚动后提取图片链接，直到页面连续无法滚动且没有新链接。

        :param max_attempts: 最大滚动次数，防止死循环
        :param wait_time: 每次滚动后等待的时间，用于加载内容
        :param scroll_step: 每次滚动的距离（像素值）
        :param no_change_limit: 连续无法滚动且无新链接的最大次数
        :return: 所有提取到的图片链接集合
        """
        all_image_links = set()
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        no_change_count = 0  # 连续无法滚动且无新链接的计数器
        attempts = 0

        # **初次抓取图片链接**
        self.log_message("初次抓取图片链接...")
        current_links = self._extract_image_links()
        all_image_links.update(current_links)
        self.log_message(f"初次提取到的图片链接数量: {len(current_links)}")

        while attempts < max_attempts:
            # **滚动页面一点点**
            self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            self.log_message(f"第 {attempts + 1} 次滚动，滚动 {scroll_step} 像素...")
            time.sleep(wait_time)

            # **抓取滚动后的图片链接**
            self.log_message("抓取滚动后的图片链接...")
            current_links = self._extract_image_links()
            new_links = current_links.difference(all_image_links)
            all_image_links.update(current_links)

            self.log_message(f"新增图片链接数量: {len(new_links)}")

            # **检查页面高度变化**
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and not new_links:
                # 只有页面高度不变且没有新链接时，才增加计数器
                no_change_count += 1
                self.log_message(f"页面无法滚动且无新链接，第 {no_change_count} 次检测到此情况。")
                if no_change_count >= no_change_limit:
                    self.log_message("页面无法滚动且无新链接多次，停止滚动。")
                    break
            else:
                # 只要页面高度变化或抓取到新链接，就重置计数器
                last_height = new_height
                no_change_count = 0

            attempts += 1

        if attempts == max_attempts:
            self.log_message("达到最大滚动次数，可能仍有未加载的内容。")

        self.log_message(f"滚动结束，总共提取到的图片链接数量: {len(all_image_links)}")
        return all_image_links


    def _extract_image_links(self):
        """
        提取当前页面上的所有图片链接。

        :return: 图片链接集合
        """
        try:
            image_elements = self.driver.find_elements(By.XPATH, "//a[@class='__7D5D_BHJ']/img")
            image_links = {
                re.sub(r'_fw.*$', '', img.get_attribute("src"))
                for img in image_elements if img.get_attribute("src")
            }
            self.log_message(f"当前提取到的图片链接数量: {len(image_links)}")
            return image_links
        except Exception as e:
            self.log_message(f"提取图片链接时发生错误: {e}")
            return set()


    # def close(self):
    #     if self.driver:
    #         self.driver.quit()
# # 测试执行
# huaban = Huabanscraper()
# try:
#     huaban.scrape()
# finally:
#     huaban.close()