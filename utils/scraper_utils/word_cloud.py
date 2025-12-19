import json
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import matplotlib.font_manager as fm
import re


class WordCloudGenerator:
    def __init__(self, stopwords_path, font_path='SimHei.ttf', web_name=None, links_count=None):
        """
        初始化词云生成器
        :param stopwords_path: 停用词文件路径
        :param font_path: 中文字体路径，默认 SimHei.ttf
        """
        import os
        if not os.path.exists(stopwords_path):
            raise FileNotFoundError(f"停用词文件未找到，请检查路径: {stopwords_path}")
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"字体文件未找到，请检查路径: {font_path}")

        self.font_path = font_path
        self.stopwords = self.load_stopwords(stopwords_path)
        self.web_name = web_name
        self.links_count = links_count

    @staticmethod
    def load_stopwords(file_path):
        """
        加载停用词表
        :param file_path: 停用词文件路径
        :return: 停用词集合
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file)

    @staticmethod
    def load_comments(file_path):
        """
        加载评论数据，提取所有 comment_text 字段内容，并返回关键词
        :param file_path: JSON 文件路径
        :return: (评论文本列表, 搜索关键词)
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        keyword = data.get("keyword", "未知关键词")  # 提取搜索关键词
        comments = []
        for post in data.get("comments", []):
            for comment in post.get("comments", []):
                if 'comment_text' in comment:
                    comments.append(comment['comment_text'])
        return comments, keyword  # 确保返回的是元组

    def preprocess_text(self, comments):
        """
        文本预处理：分词和去除停用词
        :param comments: 评论文本列表
        :return: 处理后的词列表
        """
        all_comments = ' '.join(comments)
        words = jieba.lcut(all_comments)
        filtered_words = [word for word in words if word not in self.stopwords and len(word) > 1]
        print(f"提取到的中文分词（去重后）：{set(filtered_words)}")  # 调试信息
        return filtered_words

    @staticmethod
    def extract_english_words(comments):
        """
        提取英文单词
        :param comments: 评论文本列表
        :return: 英文单词列表
        """
        all_comments = ' '.join(comments)
        # 使用正则表达式提取所有由英文字母组成的单词
        english_words = re.findall(r'[a-zA-Z]+', all_comments)
        print(f"提取到的英文单词（去重后）：{set(english_words)}")  # 调试信息
        return list(set(english_words))  # 返回去重后的英文单词列表

    @staticmethod
    def count_word_frequencies(words):
        """
        统计词频
        :param words: 词列表
        :return: 词频统计字典
        """
        return Counter(words)

    def generate_wordcloud(self, word_counts, output_path, keyword, comment_count):
        """
        生成词云并添加高频词和关键词备注
        :param word_counts: 词频统计字典
        :param output_path: 词云图输出路径
        :param keyword: 搜索关键词
        :param comment_count: 评论数量
        """
        # 初始化词云，使用提供的字体路径
        wc = WordCloud(
            font_path=self.font_path,
            width=800,
            height=400,
            background_color='white'
        )
        wc.generate_from_frequencies(word_counts)

        # 获取前几个高频词
        top_words = word_counts.most_common(10)  # 获取前 10 个高频词
        remarks_top_words = " | ".join([f"{word}: {freq}" for word, freq in top_words])

        # 加载字体
        font_prop = fm.FontProperties(fname=self.font_path)

        # 设置画布
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')  # 关闭坐标轴

        # 添加备注 - 搜索关键词和评论数量
        remarks_keyword = f"搜索关键词: {keyword} | 搜索平台: {self.web_name} | 评论数量: {comment_count} | 爬取帖子数量: {self.links_count}"
        plt.figtext(0.5, 0.04, remarks_keyword, ha="center", fontsize=12, wrap=True, fontproperties=font_prop)

        # 添加高频词备注在最底部
        plt.figtext(0.5, 0.01, remarks_top_words, ha="center", fontsize=10, wrap=True, fontproperties=font_prop)

        # 显示图像并保存
        plt.tight_layout(rect=[0, 0.08, 1, 1])  # 调整布局，留出空间给备注
        plt.savefig(output_path)
        print(f"词云保存到: {output_path}")

        # plt.show()

    def process_comments(self, json_path, output_image_path):
        """
        从评论文件生成词云
        :param json_path: 评论 JSON 文件路径
        :param output_image_path: 词云输出路径
        """
        print("加载评论数据...")
        comments, keyword = self.load_comments(json_path)  # 获取评论和关键词
        comment_count = len(comments)  # 计算评论数量
        print(f"关键词: {keyword}")
        print(f"总共加载到 {comment_count} 条评论。")

        print("开始提取中文分词...")
        chinese_words = self.preprocess_text(comments)
        print(f"中文分词总数：{len(chinese_words)}")

        print("开始提取英文单词...")
        english_words = self.extract_english_words(comments)
        print(f"英文单词总数：{len(english_words)}")

        print("统计词频...")
        word_counts = self.count_word_frequencies(chinese_words + english_words)
        print("高频词统计（前 20）：")
        for word, freq in word_counts.most_common(20):
            print(f"{word}: {freq}")

        print("开始生成词云...")
        self.generate_wordcloud(
            word_counts=word_counts,
            output_path=output_image_path,
            keyword=keyword,  # 使用提取的关键词
            comment_count=comment_count
        )


# 使用示例
# wc_generator = WordCloudGenerator(
#     web_name="小红书",
#     links_count=20,
#     stopwords_path=r'/Users/apple/pyqt6爬虫网站本地测试/pythonProject/data/baidu_stopwords.txt',
#     font_path=r'/Users/apple/pyqt6爬虫网站本地测试/pythonProject/data/font.TTF'
# )
# wc_generator.process_comments(
#     json_path=r'/Users/apple/Downloads/爬取内容/爬取内容xiaohongshu_com_20250130_225457_e7d8ad7e/deepseek.json',
#     output_image_path=r'/Users/apple/Downloads/爬取内容/爬取内容xiaohongshu_com_20250130_225457_e7d8ad7e/输出的词云路径.png'
# )