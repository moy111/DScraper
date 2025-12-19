import re
import time
import os
import json
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from utils.login_utils.browser_setup import create_driver
from utils.login_utils.cookies_manager import get_or_load_cookies
from utils.scraper_utils.download_image import download_project_image
from utils.file_utils.file_path_and_creat_folder import create_output_folder
from utils.scraper_utils.word_cloud import WordCloudGenerator
from utils.file_utils.load_datas import resource_path

class XhsScraper():
    def __init__(self, key_word, log_signal=None, max_links=None):
        """
        小红书 爬虫类，爬取指定关键词和页数的内容。

        参数：
        key_word: str - 搜索关键词
        log_signal: pyqtSignal (可选) - 用于向 GUI 日志窗口输出信息
        """
        self.key_word = key_word
        self.log_signal = log_signal
        self.max_links = max_links
        self.driver = create_driver(log_signal=self.log_signal, headless=False)  # 创建浏览器实例
        self.thread_instance = None  # 初始化 thread_instance 属性
        self.all_comments = []  # 用于存储所有帖子的评论

        # 尝试获取或加载 cookies
        login_url = "https://www.xiaohongshu.com"  # 替换为实际的登录 URL
        get_or_load_cookies(self.driver, login_url, "xhs", self.log_signal, login_click_xpath="//*[@id='login-btn']")

        # input("test")


    def log_message(self, message):
        """日志输出函数，如果 log_signal 存在，则发送信号；否则直接打印"""
        if self.log_signal:
            self.log_signal.emit(message)
        else:
            print(message)

    def scrape(self, custom_base_dir=None):
        """开始爬取指定关键词内容"""
        key_word_clear = self.key_word.replace(' ', '')  # 去除空格
        base_url = f"https://www.xiaohongshu.com/search_result/?keyword={key_word_clear}&source=web_search_result_notes"
        self.log_message('请稍等，正在加载网址')
        post_urls = set()  # 用集合去重

        try:
            # 获取用户输入的文件夹路径
            output_folder = create_output_folder(base_url, custom_base_dir=custom_base_dir)

            # 打开初始页面
            self.driver.get(base_url)
            WebDriverWait(self.driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            self.log_message("页面加载完成，开始滚动提取链接...")

            # 等待初始页面的链接加载完成
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//a[contains(@class, 'cover') and contains(@class, 'mask')]"))
                )
                self.log_message("初始页面的链接元素加载完成，开始提取链接...")
            except TimeoutException:
                self.log_message("等待初始页面的链接元素加载超时，可能部分链接无法提取。")

            # 提取初始页面的链接
            initial_links = {
                re.sub(r'_fw.*$', '', post.get_attribute("href"))
                for post in
                self.driver.find_elements(By.XPATH, "//a[contains(@class, 'cover') and contains(@class, 'mask')]")
                if post.get_attribute("href")
            }
            post_urls.update(initial_links)
            self.log_message(f"初始页面链接数量: {len(initial_links)}，总链接数量: {len(post_urls)}")

            # 滚动逻辑
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            no_change_count = 0
            wait_time = 1.5
            scroll_step = 300
            no_change_limit = 50

            while len(post_urls) < self.max_links:
                # 滚动页面
                self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                self.log_message(f"滚动页面，滚动 {scroll_step} 像素...")
                time.sleep(wait_time)

                # 提取新链接
                current_links = {
                    re.sub(r'_fw.*$', '', post.get_attribute("href"))
                    for post in
                    self.driver.find_elements(By.XPATH, "//a[contains(@class, 'cover') and contains(@class, 'mask')]")
                    if post.get_attribute("href")
                }
                new_links = current_links - post_urls
                post_urls.update(new_links)

                self.log_message(f"新增链接数量: {len(new_links)}，总链接数量: {len(post_urls)}")

                # 检查页面高度变化
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height and not new_links:
                    no_change_count += 1
                    self.log_message(f"页面未变化且无新链接，第 {no_change_count} 次检测到此情况。")
                    if no_change_count >= no_change_limit:
                        self.log_message("页面连续多次无法滚动且无新链接，停止滚动。")
                        break
                else:
                    last_height = new_height
                    no_change_count = 0

            self.log_message(f"滚动结束，总提取到的链接数量: {len(post_urls)}")
            post_urls = list(post_urls)[:self.max_links]  # 如果超出限制，裁剪到上限

            # 遍历提取的链接并访问
            for link_index, post_url in enumerate(post_urls, start=1):
                try:
                    if post_url:  # 确保 URL 不为空
                        self.log_message(f"开始处理链接 {link_index}/{len(post_urls)}: {post_url}")
                        self._scrape_post(post_url, output_folder, link_index, len(post_urls))
                except Exception as e:
                    self.log_message(f"处理 URL {post_url} 时出错: {str(e)}")

            # 统一生成 JSON 文件路径
            json_path = os.path.join(output_folder, f"{self.key_word}.json")

            # 保存所有评论到文件
            self.save_all_comments_to_file(json_path)

            # 调用生成词云的方法
            try:
                output_image_path = os.path.join(output_folder, f"{self.key_word}_wordcloud.png")
                self.generate_word_cloud(json_path, output_image_path)
                self.log_message(f"词云图已生成并保存到: {output_image_path}")
            except Exception as e:
                self.log_message(f"生成词云时出错: {str(e)}")

        finally:
            self.driver.quit()

    def _scrape_post(self, post_url, output_folder, link_index, link_total):
        try:
            self.log_message(f"正在处理帖子: {post_url} ({link_index}/{link_total})")
            self.driver.get(post_url)

            # 滚动并提取图片链接
            all_image_links = self.extract_links()

            # 提取帖子标题
            post_title = None
            try:
                self.log_message("开始提取帖子标题...")
                title_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='detail-title']"))
                )
                raw_title = title_element.text.strip()
                post_title = re.sub(r'[\\/:*?"<>|]', '_', raw_title)  # 替换非法字符
                self.log_message(f"提取到的标题: {post_title}")

                # 下载图片
                for i, image_url in enumerate(all_image_links):
                    try:
                        download_project_image(image_url, output_folder, i + 1, self.log_signal,
                                               prefix=f"{post_title}_")
                    except Exception as e:
                        self.log_message(f"图片下载失败: {e}")
            except TimeoutException:
                self.log_message("未找到标题元素，跳过帖子。")
            except Exception as e:
                self.log_message(f"提取标题时发生错误: {e}")

            # 提取评论
            try:
                comments = self.extract_comments(link_index, link_total)
                if post_title:
                    self.all_comments.append({
                        "title": post_title,
                        "url": post_url,
                        "comments": comments
                    })
            except Exception as e:
                self.log_message(f"提取评论时发生错误: {e}")
        except Exception as e:
            self.log_message(f"处理帖子 {post_url} 时出错: {e}")

    def extract_comments(self, link_index, link_total):
        comments = []
        try:
            self.log_message(f"开始提取评论 (链接进度: {link_index}/{link_total})...")

            # 定位到评论区的 note-scroller 容器
            try:
                note_scroller = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "note-scroller"))
                )
                self.log_message("成功找到评论区 note-scroller。")
            except TimeoutException:
                self.log_message("未找到 note-scroller，可能该帖子无评论。")
                return comments

            # 滚动 note-scroller 容器加载更多评论
            self.scroll_note_scroller(note_scroller)
            self.log_message("正在提取评论")

            # 获取评论
            comment_elements = note_scroller.find_elements(By.XPATH, ".//div[contains(@class, 'comment-item')]")
            total_comments = len(comment_elements)
            self.log_message(f"检测到 {total_comments} 条评论元素。")

            for comment_index, comment_element in enumerate(comment_elements, start=1):
                try:
                    # 显示进度信息
                    self.log_message(
                        f"提取评论进度: {comment_index}/{total_comments} (链接进度: {link_index}/{link_total})")

                    username = comment_element.find_element(By.XPATH, ".//a[@class='name']").text.strip()
                    comment_text = comment_element.find_element(By.XPATH, ".//span[@class='note-text']").text.strip()
                    try:
                        comment_image = comment_element.find_element(By.XPATH,
                                                                     ".//div[@class='img-box']/img").get_attribute(
                            "src")
                    except NoSuchElementException:
                        comment_image = None
                    try:
                        likes = comment_element.find_element(By.XPATH,
                                                             ".//div[contains(@class, 'like-wrapper')]//span[@class='count']").text.strip()
                    except NoSuchElementException:
                        likes = "0"
                    date = comment_element.find_element(By.XPATH, ".//div[@class='date']/span").text.strip()

                    comments.append({
                        "username": username,
                        "comment_text": comment_text,
                        "comment_image": comment_image,
                        "likes": likes,
                        "date": date
                    })
                except Exception as e:
                    self.log_message(f"提取单条评论失败: {e}")

            self.log_message(f"提取到 {len(comments)} 条评论。")
        except Exception as e:
            self.log_message(f"提取评论时发生错误: {e}")
        return comments

    def scroll_note_scroller(self, container):
        """
        滚动评论区的 note-scroller 容器以加载更多评论。
        """
        try:
            previous_scroll_top = self.driver.execute_script("return arguments[0].scrollTop;", container)
            scroll_attempts = 0
            max_attempts = 3

            while scroll_attempts < max_attempts:
                # 随机滚动的距离（50~300像素之间）
                scroll_distance = random.randint(700, 1000)
                self.driver.execute_script(f"arguments[0].scrollTop += {scroll_distance};", container)

                # 随机暂停时间（0.5 ~ 2.0 秒之间）
                pause_time = random.uniform(0.5, 1)
                time.sleep(pause_time)

                # 检查滚动位置是否变化
                current_scroll_top = self.driver.execute_script("return arguments[0].scrollTop;", container)
                if current_scroll_top > previous_scroll_top:
                    self.log_message(f"滚动成功，当前位置: {current_scroll_top}")
                    previous_scroll_top = current_scroll_top
                    scroll_attempts = 0  # 重置尝试次数
                else:
                    self.log_message(f"第 {scroll_attempts + 1} 次滚动无效。")
                    scroll_attempts += 1

                # 随机插入更长时间的暂停（每滚动几次后）
                if random.random() < 0.3:  # 30% 的概率进行长暂停
                    long_pause_time = random.uniform(3, 5)
                    self.log_message(f"暂停 {long_pause_time:.2f} 秒，模拟人类行为。")
                    time.sleep(long_pause_time)

                # 检查是否滚动到底部
                max_scroll = self.driver.execute_script("return arguments[0].scrollHeight - arguments[0].clientHeight;",
                                                        container)
                if current_scroll_top >= max_scroll:
                    self.log_message("已滚动到底部，停止滚动。")
                    break

            self.log_message("滚动操作完成。")
        except Exception as e:
            self.log_message(f"滚动 note-scroller 时出错: {e}")


    def extract_links(self, max_attempts=200, wait_time=2, scroll_step=600, no_change_limit=10):
        """
        逐步滚动页面，每次滚动后提取图片链接，直到页面连续无法滚动且没有新链接。

        :param max_attempts: 最大滚动次数，防止死循环
        :param wait_time: 每次滚动后等待的时间，用于加载内容
        :param scroll_step: 每次滚动的距离（像素值）
        :param no_change_limit: 连续无法滚动且无新链接的最大次数
        :return: 所有提取到的图片链接集合
        """
        all_image_links = set()
        # last_height = self.driver.execute_script("return document.body.scrollHeight")
        # no_change_count = 0  # 连续无法滚动且无新链接的计数器
        # attempts = 0
        try:
            image_elements = self.driver.find_elements(By.XPATH, "//img[contains(@class, 'note-slider-img')]")
            image_links = {
                re.sub(r'_fw.*$', '', img.get_attribute("src"))
                for img in image_elements if img.get_attribute("src")
            }
            all_image_links.update(image_links)
            self.log_message(f"当前提取到的图片链接数量: {len(image_links)}")
            # return image_links
        except Exception as e:
            self.log_message(f"提取图片链接时发生错误: {e}")
        self.log_message(f"滚动结束，总共提取到的图片链接数量: {len(all_image_links)}")
        return all_image_links


    def save_all_comments_to_file(self, json_path):
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump({
                    "keyword": self.key_word,
                    "comments": self.all_comments
                }, f, ensure_ascii=False, indent=4)
            self.log_message(f"所有评论已保存到文件: {json_path}")
        except Exception as e:
            self.log_message(f"保存所有评论到文件时发生错误: {e}")


    def generate_word_cloud(self, json_path, output_image_path):
        """生成词云并保存为图片"""
        try:
            self.log_message(f"正在生成词云: {json_path} -> {output_image_path}")

            # 动态加载资源路径
            stopwords_path = resource_path('data/baidu_stopwords.txt')
            font_path = resource_path('data/font.TTF')

            # 创建词云生成器
            wc_generator = WordCloudGenerator(
                stopwords_path=stopwords_path,
                font_path=font_path,
                web_name='小红书',
                links_count=self.max_links
            )

            # 生成词云
            wc_generator.process_comments(json_path=json_path, output_image_path=output_image_path)
            self.log_message(f"词云已成功保存到: {output_image_path}")
        except Exception as e:
            self.log_message(f"生成词云时发生错误: {e}")


# def resource_path(relative_path):
#     """
#     获取资源文件的路径，适配打包和非打包模式。
#     :param relative_path: 相对路径
#     :return: 绝对路径
#     """
#     if hasattr(sys, '_MEIPASS'):  # 如果是打包后的环境
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)
