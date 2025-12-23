# DScraper 爬虫工具箱
https://qjdxx9wxscbnncpx.public.blob.vercel-storage.com/DScraper.png
一个基于 PyQt6 的多网站爬虫工具箱，提供图形界面，支持多种设计和图片网站的自动化数据采集。

## 版本信息

当前版本：v1.1.0

## 功能特性

- **多网站支持**：集成多个设计和图片网站的爬虫模块
  - ArchDaily（建筑设计）
  - 视觉中国（VCG）
  - Gooood（设计网站）
  - 知末效果图（ZNZMO）（当前网页HTML元素有调整，此版本暂时不可用，欢迎优化）
  - 花瓣网（Huaban）（当前网页HTML元素有调整，此版本暂时不可用，欢迎优化）
  - 大众点评（Dianping）（当前网页HTML元素有调整，此版本暂时不可用，欢迎优化）
  - 小红书（Xiaohongshu）（当前网页HTML元素有调整，此版本暂时不可用，欢迎优化）

- **图形界面**：基于 PyQt6 的现代化用户界面
- **状态监控**：实时显示各模块运行状态
- **灵活配置**：支持自定义保存路径
- **日志系统**：完整的日志记录和错误处理
- **数据处理**：集成 jieba 分词和词云生成
- **免责声明**：内置使用协议确认

## 目录结构

```
pythonProject/
├── main.py    # 主程序入口
├── requirements.txt             # Python 依赖列表
├── app.log                      # 应用程序日志
├── README.md                    # 项目说明文档
├── data/                        # 数据文件目录
│   ├── 2344673.icns            # 应用程序图标
│   ├── baidu_stopwords.txt     # 百度停用词表
│   ├── dianping_city_link.json # 大众点评城市链接
│   ├── disclaimer_text.txt     # 免责声明文本
│   └── font.TTF                 # 字体文件
├── ui/                          # 用户界面模块
│   ├── archdaily_window.py      # ArchDaily 爬虫界面
│   ├── dianping_window.py       # 大众点评爬虫界面
│   ├── gooood_window.py         # Gooood 爬虫界面
│   ├── huaban_window.py         # 花瓣网爬虫界面
│   ├── vcg_window.py            # 视觉中国爬虫界面
│   ├── xhs_window.py            # 小红书爬虫界面
│   └── znzmo_window.py          # 知末效果图爬虫界面
├── utils/                       # 工具模块
│   ├── file_utils/              # 文件操作工具
│   │   ├── extract_file.py      # 文件提取
│   │   ├── file_path_and_creat_folder.py  # 路径管理
│   │   └── load_datas.py        # 数据加载
│   ├── frontend_utils/          # 前端工具
│   │   ├── style.py             # 样式定义
│   │   └── window_ui.py         # 窗口UI组件
│   ├── licenses_utils/          # 许可证工具
│   │   └── licenses.py          # 免责声明对话框
│   └── scraper_utils/           # 爬虫工具
│       ├── download_image.py    # 图片下载
│       ├── scraper_utils.py     # 爬虫通用工具
│       └── word_cloud.py        # 词云生成
└── web_scraper/                 # 爬虫核心模块
    ├── archdaily_scraper.py     # ArchDaily 爬虫
    ├── dianping_scraper.py      # 大众点评爬虫
    ├── gooood_scraper.py        # Gooood 爬虫
    ├── huaban_scraper.py        # 花瓣网爬虫
    ├── pinterest_scraper.py     # Pinterest 爬虫（备用）
    ├── vcg_scraper.py           # 视觉中国爬虫
    ├── xhs_scraper.py           # 小红书爬虫
    └── znzmo_scraper.py         # 知末效果图爬虫
```

## 安装步骤

### 环境要求

- Python 3.8+
- macOS / Windows / Linux

### 安装依赖

1. 克隆或下载项目到本地目录

2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. （可选）如果需要打包为可执行文件，安装 PyInstaller：
   ```bash
   pip install pyinstaller
   ```

## 使用说明

1. **启动程序**：
   ```bash
   python main.py
   ```

2. **首次运行**：
   - 程序会显示免责声明对话框，请仔细阅读并同意条款
   - 选择数据保存路径（默认为用户主目录下的 crawloo_data 文件夹）

3. **选择爬虫模块**：
   - 在主界面标签页中选择对应的网站模块
   - 配置爬取参数（如关键词、数量等）
   - 点击开始按钮执行爬取

4. **监控状态**：
   - 主界面底部显示各模块的实时运行状态
   - 日志文件保存在 `~/crawloo_logs/app.log`

5. **查看结果**：
   - 爬取的数据保存在指定的保存路径中
   - 支持图片下载、数据导出等功能

## 主要依赖

- **PyQt6**：图形界面框架
- **Selenium**：网页自动化测试
- **Requests**：HTTP 请求库
- **Jieba**：中文分词
- **WordCloud**：词云生成
- **Pandas**：数据处理
- **Matplotlib**：数据可视化
- **Keyring**：安全凭据存储

完整依赖列表请查看 `requirements.txt` 文件。

## 日志和调试

- 应用程序日志保存在 `~/crawloo_logs/app.log`
- 错误日志保存在 `~/crawloo_error.log`
- 支持控制台和文件双重日志输出

## 注意事项

1. **合规使用**：请确保您的爬取行为符合目标网站的 Terms of Service 和相关法律法规
2. **频率控制**：合理设置请求间隔，避免对目标服务器造成过大压力
3. **数据隐私**：妥善保管爬取到的数据，遵守数据保护相关法规
4. **版本兼容**：建议使用最新稳定版本，如有问题请检查 Python 和依赖版本

## 开发说明

项目采用模块化设计，各部分职责明确：

- `main2_no_vertifacation.py`：主程序和界面框架
- `ui/`：各模块的界面实现
- `web_scraper/`：核心爬虫逻辑
- `utils/`：通用工具函数

如需添加新的爬虫模块，请参考现有模块的实现方式。

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。使用前请仔细阅读免责声明。

## 联系方式

如有问题或建议，请通过项目仓库提交 Issue。
