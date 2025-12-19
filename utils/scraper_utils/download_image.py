# download_image.py
import os
import re
import requests
import time


def download_project_image(url_slideshow, folder_path, image_number, log_signal=None, retries=4, delay=2, prefix=""):
    """下载图片，带重试机制"""
    for attempt in range(retries):
        try:
            response = requests.get(url_slideshow, stream=True)
            response.raise_for_status()  # 如果响应码不是200，会引发异常
            # 构建文件名，添加前缀
            file_name = os.path.join(folder_path, f"{prefix}image_{image_number}.jpg")
            # 保存图片到本地
            with open(file_name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            # 获取文件名（不包含路径）
            short_file_name = os.path.basename(file_name)
            # 通过信号发送下载成功的日志
            if log_signal:
                log_signal.emit(f"<font color='#2BC840'>图片下载成功:{short_file_name}")
            else:
                print(f"图片下载成功:{short_file_name}")
            return  # 下载成功后退出
        except requests.exceptions.RequestException as e:
            # 通过信号发送下载失败的日志
            if log_signal:
                log_signal.emit(f"下载图片失败: {e}，尝试 {attempt + 1}/{retries}")
            else:
                print(f"下载图片失败: {e}，尝试 {attempt + 1}/{retries}")
            time.sleep(delay)  # 等待后重试

    if log_signal:
        log_signal.emit(f"下载图片失败: {url_slideshow}，已重试 {retries} 次")
    else:
        print(f"下载图片失败: {url_slideshow}，已重试 {retries} 次")


def download_vcg_image(url_slideshow, folder_path, page_number, image_number, log_signal, retries=4, delay=2):
    """下载 VCG 图片，带重试机制"""
    for attempt in range(retries):
        try:
            response = requests.get(url_slideshow, stream=True)
            response.raise_for_status()  # 如果响应码不是200，会引发异常
            # 构建文件名，加入页码信息
            file_name = os.path.join(folder_path, f'image_page{page_number}_number{image_number}.jpg')
            # 保存图片到本地
            with open(file_name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            # 获取文件名（不包含路径）
            short_file_name = os.path.basename(file_name)
            # 通过信号发送下载成功的日志
            log_signal.emit(f"<font color='#2BC840'>图片下载成功: {short_file_name}")
            return  # 下载成功后退出
        except requests.exceptions.RequestException as e:
            # 通过信号发送下载失败的日志
            log_signal.emit(f"下载图片失败: {e}，尝试 {attempt + 1}/{retries}")
            time.sleep(delay)  # 等待后重试

    log_signal.emit(f"下载图片失败: {url_slideshow}，已重试 {retries} 次")


def download_znzmo_image(url_slideshow, folder_path, page_number, image_number, log_signal, title, retries=4, delay=2):
    """下载 ZNZMO 图片，带重试机制"""
    for attempt in range(retries):
        try:
            response = requests.get(url_slideshow, stream=True)
            response.raise_for_status()  # 如果响应码不是200，会引发异常

            # 获取当前时间戳，作为文件名的一部分
            timestamp = int(time.time())

            # 构建文件名，加入标题、页面、序号和时间戳信息
            sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", title)  # 去除标题中可能不允许的字符
            file_name = os.path.join(folder_path, f'{sanitized_title}_page{page_number}_number{image_number}_{timestamp}.jpg')

            # 保存图片到本地
            with open(file_name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            # 获取文件名（不包含路径）
            short_file_name = os.path.basename(file_name)
            # 通过信号发送下载成功的日志
            log_signal.emit(f"<font color='#2BC840'>ZNZMO 图片下载成功: {short_file_name}</font>")
            return  # 下载成功后退出
        except requests.exceptions.RequestException as e:
            # 通过信号发送下载失败的日志
            log_signal.emit(f"下载 ZNZMO 图片失败: {e}，尝试 {attempt + 1}/{retries}")
            time.sleep(delay)  # 等待后重试

    log_signal.emit(f"下载 ZNZMO 图片失败: {url_slideshow}，已重试 {retries} 次")
