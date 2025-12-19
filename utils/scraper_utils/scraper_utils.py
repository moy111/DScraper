from PyQt6.QtWidgets import QMessageBox
import inspect



def on_scraper_finished(window):
    """爬虫完成时更新状态"""
    window.status_signal.emit("爬虫已完成")  # 更新状态栏
    log_output = window.ui_elements.get("log_output")
    if log_output:
        log_output.append("爬虫执行完毕")  # 日志记录
    else:
        print("Error: log_output is not initialized")  # 错误信息

    status_label = window.ui_elements.get("status_label")
    if status_label:
        status_label.setText("状态: 爬虫已完成")  # 更新爬虫窗口的状态标签
    else:
        print("Error: status_label is not initialized")  # 错误信息



def start_scraper(window, ScraperThreadClass):
    """启动爬虫任务"""
    keyword = window.ui_elements["keyword_input"].text()
    custom_base_dir = window.main_ui_elements["path_input"].text()

    # 动态检查是否需要 city 参数
    init_params = inspect.signature(ScraperThreadClass.__init__).parameters
    city_required = "city" in init_params

    city = None
    if city_required:
        if "city_input" in window.ui_elements:
            city_input = window.ui_elements["city_input"]
            if city_input is not None:  # 确保 city_input 不是 None
                city = city_input.text()  # 使用 text() 获取内容

        if not city:  # 如果 city 为空或没有 city_input
            QMessageBox.warning(window, "提示", "请输入城市名字")
            if "city_input" in window.ui_elements:  # 如果 city_input 存在
                window.ui_elements["city_input"].setFocus()
            return

    # 动态检查是否存在 page_input
    page_count = None
    if "page_input" in window.ui_elements and window.ui_elements["page_input"]:
        page_count = window.ui_elements["page_input"].value()

    # 动态检查是否存在 max_links_input
    max_links = None
    if "max_links_input" in window.ui_elements and window.ui_elements["max_links_input"]:
        max_links = window.ui_elements["max_links_input"].value()

    if not keyword:
        QMessageBox.warning(window, "提示", "请输入关键词")
        window.ui_elements["keyword_input"].setFocus()
        return

    if window.scraper_thread and window.scraper_thread.isRunning():
        window.update_status_all("爬虫正在运行，请先终止当前爬虫。")
        return

    # 构建爬虫线程参数
    try:
        # 获取 ScraperThreadClass 的参数列表
        scraper_params = {
            "keyword": keyword,
            "custom_base_dir": custom_base_dir,
        }

        # 动态添加可选参数
        if "page_count" in init_params and page_count is not None:
            scraper_params["page_count"] = page_count
        if "max_links" in init_params and max_links is not None:
            scraper_params["max_links"] = max_links
        if city_required and city:
            scraper_params["city"] = city

        # 初始化爬虫线程
        print(f"Starting scraper with parameters: {scraper_params}")
        window.scraper_thread = ScraperThreadClass(**scraper_params)

        # 连接信号槽
        window.scraper_thread.log_signal.connect(window.update_log)
        window.scraper_thread.finished.connect(window.on_scraper_finished)

        window.scraper_thread.start()
        window.update_status_all("爬虫运行中...")
        return True

    except Exception as e:
        window.update_status_all("爬虫启动失败。")
        QMessageBox.critical(window, "错误", f"爬虫启动失败: {str(e)}")
        window.scraper_thread = None
        return False

def stop_scraper(window):
    """强制终止爬虫线程"""
    if window.scraper_thread:
        window.scraper_thread.terminate()
        window.scraper_thread.wait()
        log_output = window.ui_elements.get("log_output")
        if log_output:
            log_output.append("爬虫已终止")
        else:
            print("Error: log_output is not initialized")  # 错误信息

        window.update_status_all("爬虫已终止")


def update_log(window, message):
    """在日志输出窗口中追加日志信息。"""
    log_output = window.ui_elements.get("log_output")
    if log_output:
        log_output.append(message)
    else:
        print("Error: log_output is not initialized")  # 错误信息


def update_status_all(window, status_text):
    """同步更新爬虫窗口和主窗口的状态"""
    window.status_signal.emit(status_text)

    log_output = window.ui_elements.get("log_output")
    if log_output:
        log_output.append(status_text)
    else:
        print("Error: log_output is not initialized")  # 错误信息

    status_label = window.ui_elements.get("status_label")
    if status_label:
        status_label.setText(f"状态: {status_text}")
    else:
        print("Error: status_label is not initialized")  # 错误信息


def show_message_box(message):
    """显示一个提示对话框"""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText(message)
    msg_box.setWindowTitle("提示")
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
