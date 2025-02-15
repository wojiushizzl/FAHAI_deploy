import flet as ft


class DataOverviewWindow(ft.Container):
    def __init__(self):
        """数据概览窗口"""
        super().__init__()
        self.expand = True

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含数据概览功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))
