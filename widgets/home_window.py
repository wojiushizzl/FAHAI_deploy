import flet as ft


class HomeWindow(ft.Container):
    def __init__(self):
        """首页窗口"""
        super().__init__()
        self.expand = True
        self.padding = ft.Padding(0, 0, 72, 30)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        image_widget = ft.Image(src='/images/python4.png', filter_quality=ft.FilterQuality.MEDIUM)
        # image_widget = ft.Image(src='/images/siri.gif', filter_quality=ft.FilterQuality.MEDIUM)

        self.content = image_widget
