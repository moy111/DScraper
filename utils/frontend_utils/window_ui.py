# window_ui.py
import qtawesome as qta
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QHBoxLayout, QTextEdit, QCompleter, QMessageBox, QApplication
from utils.file_utils.load_datas import resource_path, load_json_file
from utils.frontend_utils.style import StyleSheetHelper
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPalette


# QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
# QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)


def create_common_ui(parent, window_title, visit_button_text, visit_button_func, exclude_elements=None):
    """
    创建通用的 UI 布局。

    参数：
    parent: QWidget - 父窗口
    window_title: str - 窗口标题
    visit_button_text: str - 访问按钮的文字
    visit_button_func: function - 访问按钮的功能
    """
    # 获取系统是否为深色模式
    is_dark_mode = QApplication.palette().color(QPalette.Window).value() < 128
    print("Is dark mode（common_ui）:", is_dark_mode)  # 打印出当前模式


    exclude_elements = exclude_elements or []
    parent.setWindowTitle(window_title)
    layout = QVBoxLayout()

    # 创建横向布局，包含关键词输入框、访问按钮、页数选择框和城市选择框
    main_layout = QHBoxLayout()

    # 创建关键词输入框
    if "keyword_input" not in exclude_elements:
        keyword_label = QLabel('关键词:')
        keyword_label.setObjectName("keyword_label")  # 设置唯一的对象名称
        keyword_input = QLineEdit()
        keyword_input.setPlaceholderText(f'在 {window_title} 中搜索...')
        main_layout.addWidget(keyword_label)
        main_layout.addWidget(keyword_input)
    else:
        keyword_input = None


    # 创建城市名称输入框
    if "city_input" not in exclude_elements:
        # 动态加载城市链接
        city_names = []
        try:
            city_links = load_json_file(resource_path("data/dianping_city_link.json"))
            city_names = list(city_links.keys())
        except FileNotFoundError:
            QMessageBox.warning(
                parent, "警告",
                f"请检查文件路径是否正确！"
            )
        except ValueError as e:
            QMessageBox.warning(
                parent, "警告",
                f"加载城市链接失败: {str(e)}"
            )
        finally:
            if not city_names:
                print(f"[DEBUG] 无法加载城市链接，城市列表为空，程序仍将继续运行。")

        city_label = QLabel('城市:')
        city_label.setObjectName("city_label")
        city_input = QLineEdit()
        city_input.setPlaceholderText("输入城市名称...")

        # 使用 QCompleter 实现动态匹配
        city_completer = QCompleter(city_names)
        city_completer.setCaseSensitivity(Qt.CaseInsensitive)  # 匹配不区分大小写
        city_input.setCompleter(city_completer)

        main_layout.addWidget(city_label)
        main_layout.addWidget(city_input)
    else:
        city_input = None


    # 访问按钮
    if "visit_button" not in exclude_elements:
        visit_button = QPushButton(visit_button_text)
        visit_button.clicked.connect(visit_button_func)
        visit_button.setIcon(qta.icon("mdi.web"))
        main_layout.addWidget(visit_button)
    else:
        visit_button = None

    # 页数选择框
    if "page_input" not in exclude_elements:
        page_label = QLabel('爬取页数:')
        page_input = QSpinBox()
        page_input.setRange(1, 100)
        page_input.setValue(1)
        main_layout.addWidget(page_label)
        main_layout.addWidget(page_input)
    else:
        page_label, page_input = None, None

    # 显示 max_links 输入框
    if "max_links_input" not in exclude_elements:
        max_links_label = QLabel('爬取帖子数:')
        max_links_input = QSpinBox()
        max_links_input.setRange(1, 1000)
        max_links_input.setValue(20)
        main_layout.addWidget(max_links_label)
        main_layout.addWidget(max_links_input)
    else:
        max_links_label, max_links_input = None, None

    # 将横向布局添加到主布局
    layout.addLayout(main_layout)

    # 创建一个水平布局，用于放置启动和终止按钮
    button_row_layout = QHBoxLayout()
    # 启动按钮
    start_button = QPushButton('开始爬取项目图片以及信息概要')
    start_button.setDefault(True)
    start_button.setAutoDefault(True)

    # 添加图标
    start_button.setIcon(qta.icon("mdi.arrow-right"))  # Material Design Icon
    start_button.setIconSize(QSize(32, 32))  # 调整为合适的大小
    start_button.setStyleSheet(
        StyleSheetHelper.get_button_style(StyleSheetHelper.get_colorful_border_style(), is_dark_mode))  # 传递正确的参数
    start_button.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手型
    start_button.setFixedHeight(50)  # 设置启动按钮高度
    start_button.setMinimumWidth(200)  # 设置启动按钮最小宽度

    # 终止按钮
    stop_button = QPushButton('终止爬虫')
    stop_button.setIcon(qta.icon("mdi.stop-circle-outline"))  # 添加终止图标
    stop_button.setIconSize(QSize(32, 32))  # 设置图标大小
    stop_button.setStyleSheet(
        StyleSheetHelper.get_button_style(StyleSheetHelper.get_normal_border_style(), is_dark_mode))  # 传递正确的参数
    stop_button.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手型
    stop_button.setFixedHeight(50)  # 统一按钮高度
    stop_button.setMinimumWidth(120)  # 设置终止按钮最小宽度

    # 将按钮添加到水平布局
    button_row_layout.addWidget(start_button)
    button_row_layout.addWidget(stop_button)

    # 为启动按钮设置更大的拉伸比例
    button_row_layout.setStretch(0, 3)  # 启动按钮占更多空间
    button_row_layout.setStretch(1, 1)  # 终止按钮占较少空间

    # 将按钮布局添加到主布局
    layout.addLayout(button_row_layout)

    # 日志显示框
    log_output = QTextEdit()
    log_output.setPlaceholderText(f"这里将显示「{window_title}」的爬取日志，输入关键词启动爬虫来激发你的创意")
    log_output.setReadOnly(True)

    layout.addWidget(log_output)

    # 状态显示
    status_label = QLabel("状态: 未运行")
    status_label.setStyleSheet("color: gray;")
    layout.addWidget(status_label)

    # 设置布局
    parent.setLayout(layout)

    return {
        "keyword_input": keyword_input,
        "page_input": page_input,
        "page_label": page_label,
        "start_button": start_button,
        "stop_button": stop_button,
        "log_output": log_output,  # 确保这一行存在
        "status_label": status_label,
        "log_placeholder": log_output.placeholderText(), # 返回日志的 placeholder 文本
        "max_links_input": max_links_input, # 添加最大链接数量
        "city_input": city_input # 返回新增的城市输入框
    }
