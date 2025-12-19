import time
import pickle
import os
import platform
from urllib.parse import urlparse
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 定义每个网站的登录检查规则
# """记录已经登陆的特征"""
LOGIN_CHECK_RULES = {
    "znzmo": {"by": By.CLASS_NAME, "value": "components-Header-index__iconSort__gtvzg"},
    "huaban": {"by": By.XPATH, "value": "//*[@id='__next']/main/div[1]/div/div/div[5]/a"},
    "dianping": {"by": By.XPATH, "value": "//*[@id='__next']/div/div[1]/div[2]/div[3]/div"},
    "xhs": {"by": By.XPATH, "value": "//*[@id='global']/div[2]/div[1]/ul/li[4]/div/a/span[1]/div"},
    "tianyancha": {"by": By.XPATH, "value": "//*[@id='page-header']/div/div[2]/div/div[6]/div/a"},
    "necipc": {"by": By.XPATH, "value": "/html/body/div[5]/div[2]/div[4]/div[2]/div"}
    # 添加更多规则...
}

def log_message(log_signal, message):
    """日志输出函数，如果 log_signal 存在，则发送信号；否则直接打印"""
    if log_signal:
        log_signal.emit(message)
    else:
        print(message)

def get_or_load_cookies(driver: WebDriver, login_url: str, site_key: str, log_signal=None, login_click_xpath=None, message_signal=None) -> str:
    """
    获取或加载网站的 cookies 并保存到文件。如果已经存在匹配的 cookies 文件夹则直接加载，否则获取新的 cookies。

    :param driver: 已创建的浏览器驱动
    :param login_url: 要登录的网址
    :param log_signal: 日志信号，用于向 GUI 输出日志
    :param login_click_xpath: 模拟点击的 XPath（如果有的话）
    :return: 返回 cookie 文件的路径
    """
    # 检测操作系统类型
    if platform.system() == "Darwin":  # macOS
        base_cookie_dir = os.path.expanduser("~/Library/Application Support/DScraper/cookies")
    elif platform.system() == "Windows":  # Windows
        base_cookie_dir = os.path.expandvars(r"%APPDATA%\DScraper\cookies")
    else:  # Linux 或其他系统
        base_cookie_dir = os.path.expanduser("~/.DScraper/cookies")

    domain = urlparse(login_url).netloc
    cookies_dir = os.path.join(base_cookie_dir, domain)
    log_message(log_signal, f"Cookies 将保存到目录: {cookies_dir}")

    # 打开登录页面
    driver.get(login_url)
    time.sleep(2)  # 确保页面加载完成

    if os.path.exists(cookies_dir):
        existing_cookies = [f for f in os.listdir(cookies_dir) if f.startswith(f'cookies_{domain}')]

        if existing_cookies:
            latest_cookie_file = os.path.join(cookies_dir, sorted(existing_cookies)[-1])
            log_message(log_signal, f"发现已有的 Cookie 文件: {latest_cookie_file}")

            try:
                driver.get(f"https://{domain}")
                time.sleep(2)  # 确保页面加载

                with open(latest_cookie_file, 'rb') as file:
                    cookies = pickle.load(file)
                    for cookie in cookies:
                        try:
                            driver.add_cookie(cookie)
                        except Exception as e:
                            log_message(log_signal, f"无法加载 cookie: {cookie}, 错误: {e}")

                # 在所有 cookie 加载完后刷新页面
                log_message(log_signal, f"Cookies 已加载到浏览器: {latest_cookie_file}")
                driver.refresh()  # 刷新页面以应用 cookies
                time.sleep(2)  # 等待刷新完成

                # 检查用户是否已登录
                if is_logged_in(driver, site_key):
                    log_message(log_signal, "登录成功！")
                    return latest_cookie_file
                else:
                    log_message(log_signal, "登录失败，请检查 cookies 是否有效。")
                    log_message(log_signal, "将重新获取新的 cookie...")

            except Exception as e:
                log_message(log_signal, f"加载 Cookie 文件失败: {e}")
                log_message(log_signal, "将重新获取新的 cookie...")

    log_message(log_signal, "未找到匹配的 cookies 文件夹或加载失败，正在通过浏览器获取新的 cookie...")

    try:
        if login_click_xpath:
            # 如果提供了 XPath，先模拟点击以进入登录页面
            simulate_click(driver, login_click_xpath, log_signal)

        # 等待用户手动登录
        log_message(log_signal, "等待用户手动登录")
        while True:
            time.sleep(2)  # 每2秒检查一次
            if is_logged_in(driver, site_key):  # 检查用户是否已登录
                log_message(log_signal, "用户已登录，继续执行...")
                break  # 登录成功，退出循环

        # 获取当前时间戳，用于生成 cookie 文件名
        timestamp = time.strftime('%Y%m%d_%H%M%S')

        # 创建 cookies 文件夹（如果不存在的话）
        if not os.path.exists(cookies_dir):
            os.makedirs(cookies_dir)

        # 定义 cookie 文件的路径
        cookie_file_path = os.path.join(cookies_dir, f'cookies_{domain}_{timestamp}.pkl')

        # 保存 cookies 到文件
        with open(cookie_file_path, 'wb') as file:
            pickle.dump(driver.get_cookies(), file)

        log_message(log_signal, f"Cookies 已保存到: {cookie_file_path}")

    except Exception as e:
        log_message(log_signal, f"获取 Cookies 时出错: {e}")
    # finally:
    #     driver.quit()  # 确保在完成操作后关闭浏览器
    return cookie_file_path


def simulate_click(driver: WebDriver, xpath: str, log_signal=None) -> None:
    """
    模拟点击指定 XPath 的元素。

    :param driver: 已创建的浏览器驱动
    :param xpath: 要点击的元素的 XPath
    :param log_signal: 日志信号，用于向 GUI 输出日志
    """
    try:
        # 使用显示等待确保元素可被点击
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
        log_message(log_signal, f"已点击元素: {xpath}")
        # 标亮需要手动登录的消息
        log_message(log_signal, "<font color='#FEBC2E'>****** 请手动在浏览器里登录以获取cookie～ ******</font>")

    except TimeoutException:
        log_message(log_signal, f"等待元素超时，XPath: {xpath}")
    except NoSuchElementException:
        log_message(log_signal, f"未找到元素，XPath: {xpath}")
    except Exception as e:
        log_message(log_signal, f"点击元素时出错: {e}")


def is_logged_in(driver: WebDriver, site_key: str) -> bool:
    """
    检查用户是否已登录。
    通过查找登录成功后的特定元素来判断，例如用户头像或欢迎信息。
    """
    if site_key not in LOGIN_CHECK_RULES:
        raise ValueError(f"No login check rule defined for site '{site_key}'")

    rule = LOGIN_CHECK_RULES[site_key]
    try:
        # 动态查找登录成功标志元素
        driver.find_element(rule["by"], rule["value"])
        return True  # 找到元素，表示已登录
    except NoSuchElementException:
        return False  # 没有找到元素，表示未登录
