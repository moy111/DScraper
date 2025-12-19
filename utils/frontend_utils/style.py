# style.py
class StyleSheetHelper:

    @staticmethod
    def _get_mode_colors(is_dark_mode):
        """根据黑暗模式和白天模式返回背景颜色和边框颜色"""
        if is_dark_mode:
            return "#6A6A6A", "#444444", "#555555", "#444444"  # 深色模式
        else:
            return "#ffffff", "#dcdcdc", "#e6e6e6", "#d9d9d9"  # 浅色模式

    @staticmethod
    def get_path_button_style(is_dark_mode):
        """返回给路径按钮的样式，支持黑暗模式和白天模式"""
        # 获取背景色、边框色、悬停色和按下色
        background_color, border_color, hover_color, pressed_color = StyleSheetHelper._get_mode_colors(is_dark_mode)

        return f"""
            QPushButton {{
                border-radius: 15px; /* 设置圆角 */
                background-color: {background_color}; /* 设置背景颜色 */
                border: 1px solid {border_color}; /* 设置边框颜色 */
                padding: 5px; /* 内边距，确保图标和文本不紧贴边缘 */
            }}
            QPushButton:hover {{
                background-color: {hover_color}; /* 悬停时背景颜色 */
            }}
            QPushButton:pressed {{
                background-color: {pressed_color}; /* 按下时背景颜色 */
            }}
        """

    @staticmethod
    def get_label_style(is_dark_mode):
        """返回给状态标签的样式，支持黑暗模式和白天模式"""
        # 获取背景色和边框色
        background_color, border_color, _, _ = StyleSheetHelper._get_mode_colors(is_dark_mode)

        return f"""
            background-color: {background_color}; /* 设置背景颜色 */
            padding: 5px; /* 内边距 */
            border: 1px solid {border_color}; /* 设置边框颜色 */
            border-radius: 3px; /* 设置圆角 */
        """

    @staticmethod
    def get_label_style(is_dark_mode):
        """返回给状态标签的样式，支持黑暗模式和白天模式"""
        # 获取背景色和边框色
        background_color, border_color, _, _ = StyleSheetHelper._get_mode_colors(is_dark_mode)

        return f"""
            background-color: {background_color}; /* 设置背景颜色 */
            padding: 5px; /* 内边距 */
            border: 1px solid {border_color}; /* 设置边框颜色 */
            border-radius: 3px; /* 设置圆角 */
        """

    @staticmethod
    def get_colorful_border_style():
        """返回彩色边框的样式"""
        return """
            border: 1.5px solid qradialgradient(cx: 0.5, cy: 0.5, radius: 1, fx: 0.5, fy: 0.5, 
                                               stop:0 #FF6055, stop:0.5 #648EC8, stop:1 #2BC840);
            border-radius: 15px;
            padding: 10px;
        """

    @staticmethod
    def get_normal_border_style():
        """返回普通边框的样式"""
        return """
            border: 1px solid #a9a9a9;
            border-radius: 15px;
            padding: 10px;
        """

    @staticmethod
    def get_button_style(border_style, is_dark_mode):
        """返回公共按钮样式，接受一个边框样式和是否深色模式的参数"""
        # 根据系统模式切换背景颜色
        background_color = "#ffffff" if not is_dark_mode else "#6A6A6A"  # 浅色模式和深色模式的背景色
        hover_color = "#E2EFF9" if not is_dark_mode else "#555555"  # 浅色模式和深色模式的悬停背景色
        pressed_color = "#d9d9d9" if not is_dark_mode else "#444444"  # 按下时背景颜色

        return f"""
            QPushButton {{
                {border_style}  /* 使用传入的边框样式 */
                background-color: {background_color}; /* 默认背景颜色 */
                padding: 8px; /* 内容边距 */
            }}
            QPushButton:hover {{
                background-color: {hover_color}; /* 悬停时背景颜色 */
            }}
            QPushButton:pressed {{
                background-color: {pressed_color}; /* 按下时背景颜色 */
            }}
        """