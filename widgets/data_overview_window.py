import flet as ft


class DataOverviewWindow(ft.Container):
    def __init__(self):
        """数据概览窗口"""
        super().__init__()
        self.expand = True
    
        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        # 展示user_data/log.log
        with open("user_data/log.log", "r") as f:
            self.log_text = ft.Text(value=f.read(), size=12, color=ft.colors.PRIMARY)

        self.content = ft.Column([self.log_text], expand=True,scroll=ft.ScrollMode.AUTO)

    # 定时更新log文本
    def update_log_text(self):
        """更新日志文本"""
        with open("user_data/log.log", "r") as f:
            self.log_text.value = f.read()  




