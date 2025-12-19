import os
import sys
import json
import time
import logging

def resource_path(relative_path):
    """
    获取资源文件的运行时路径，并记录解析后的路径。
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller 打包环境
        base_path = sys._MEIPASS
        logging.debug(f"Running in a packaged environment. sys._MEIPASS = {sys._MEIPASS}")
    else:
        # 开发环境
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        logging.debug(f"Running in a development environment. Base path = {base_path}")

    full_path = os.path.normpath(os.path.join(base_path, relative_path))
    logging.debug(f"Resolved file path: {full_path}")
    return full_path


def load_json_file(relative_path):
    """
    加载 JSON 文件并返回其内容，同时记录加载时间。
    """
    file_path = resource_path(relative_path)
    logging.debug(f"Attempting to load JSON file: {file_path}")

    start_time = time.time()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        elapsed_time = time.time() - start_time
        logging.info(f"Successfully loaded JSON file: {file_path} (Time taken: {elapsed_time:.4f} seconds)")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {file_path}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error while loading JSON file {file_path}: {str(e)}")
        raise


def load_txt_file(relative_path):
    """
    加载 TXT 文件并返回其内容，同时记录加载时间。
    """
    file_path = resource_path(relative_path)
    logging.debug(f"Attempting to load TXT file: {file_path}")

    start_time = time.time()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        elapsed_time = time.time() - start_time
        logging.info(f"Successfully loaded TXT file: {file_path} (Time taken: {elapsed_time:.4f} seconds)")
        return content
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error while loading TXT file {file_path}: {str(e)}")
        raise