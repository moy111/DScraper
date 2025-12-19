import re
import uuid
from datetime import datetime
import os
import platform

def get_base_directory(custom_base_dir=None):
    """
    获取基础目录的路径。如果提供了自定义路径，则返回自定义路径，
    否则在系统的“下载”目录下创建一个名为“爬取内容”的子文件夹。

    参数:
    custom_base_dir: str - 可选的自定义基础目录路径

    返回:
    str - 基础目录路径
    """
    if custom_base_dir:
        return custom_base_dir

    # 获取当前系统类型
    system_type = platform.system()

    # 获取用户的主目录
    user_home = os.path.expanduser("~")

    # 根据系统类型获取“下载”目录路径
    if system_type in ['Darwin', 'Linux']:  # macOS 和 Linux
        downloads_dir = os.path.join(user_home, 'Downloads')
    elif system_type == 'Windows':  # Windows
        downloads_dir = os.path.join(user_home, 'Downloads')
    else:
        raise OSError("无法识别的操作系统类型")

    # 在下载目录中创建名为“爬取内容”的子文件夹
    target_dir = os.path.join(downloads_dir, "爬取内容")
    os.makedirs(target_dir, exist_ok=True)  # 确保文件夹存在

    return target_dir


def create_output_folder(base_url, custom_base_dir=None):
    """根据提供的 URL 创建一个带时间戳和域名的唯一文件夹，并返回文件夹路径"""
    # 提取域名特征（如 gooood.cn）
    domain_match = re.search(r"https?://(www\.)?([a-zA-Z0-9.-]+)", base_url)
    domain_name = domain_match.group(2).replace(".", "_") if domain_match else "爬取内容"

    # 获取基础目录
    base_dir = get_base_directory(custom_base_dir)

    # 使用当前时间或者项目名创建文件夹
    folder_name = f"爬取内容{domain_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    folder_path = os.path.join(base_dir, folder_name)

    # 创建文件夹
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


def open_folder(folder_path):
    """打开指定文件夹路径"""
    try:
        system_type = platform.system()
        if system_type == 'Windows':
            os.startfile(folder_path)
        elif system_type == 'Darwin':
            os.system(f'open "{folder_path}"')
        else:
            os.system(f'xdg-open "{folder_path}"')
    except Exception as e:
        print(f"无法打开文件夹: {e}")
