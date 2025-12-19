import os
import zipfile
import tarfile
import logging
import shutil
import platform

class Extractor:
    @staticmethod
    def extract(file_path, extract_to=None):
        """
        根据文件类型自动解压缩 ZIP 或 TAR (tar.gz, tar.bz2)
        :param file_path: 要解压的压缩文件路径
        :param extract_to: 目标解压目录，默认与文件同级
        :return: 解压成功返回 True，否则返回 False
        """
        if not os.path.exists(file_path):
            logging.error(f"文件不存在: {file_path}")
            return False

        if extract_to is None:
            extract_to = os.path.splitext(file_path)[0]  # 默认解压到同名目录

        os.makedirs(extract_to, exist_ok=True)  # 确保目标路径存在

        try:
            if file_path.endswith(".zip"):
                return Extractor.extract_zip(file_path, extract_to)
            elif file_path.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar")):
                return Extractor.extract_tar(file_path, extract_to)
            else:
                logging.error(f"不支持的压缩格式: {file_path}")
                return False
        except Exception as e:
            logging.error(f"解压失败: {str(e)}")
            return False

    @staticmethod
    def extract_zip(file_path, extract_to):
        """解压 ZIP 文件"""
        try:
            logging.debug(f"解压 ZIP 文件: {file_path} 到 {extract_to}")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            logging.debug("ZIP 解压完成")
            return True
        except Exception as e:
            logging.error(f"ZIP 解压失败: {str(e)}")
            return False

    @staticmethod
    def extract_tar(file_path, extract_to):
        """解压 TAR (tar.gz, tar.bz2, tar) 文件"""
        try:
            logging.debug(f"解压 TAR 文件: {file_path} 到 {extract_to}")
            with tarfile.open(file_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
            logging.debug("TAR 解压完成")
            return True
        except Exception as e:
            logging.error(f"TAR 解压失败: {str(e)}")
            return False

    @staticmethod
    def cleanup(file_path):
        """删除原始压缩包"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.debug(f"已删除压缩文件: {file_path}")
                return True
        except Exception as e:
            logging.error(f"删除压缩包失败: {str(e)}")
        return False

    @staticmethod
    def get_default_extract_path(file_path):
        """获取默认解压路径（去掉所有压缩格式扩展名）"""
        while file_path.endswith((".zip", ".tar", ".tar.gz", ".tar.bz2", ".tar.xz")):
            file_path = os.path.splitext(file_path)[0]
        return file_path
