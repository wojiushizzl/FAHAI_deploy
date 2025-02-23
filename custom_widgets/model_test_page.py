import flet as ft




class ModelTestPage(ft.Tab):
    def __init__(self):
        """模型测试页面"""
        super().__init__()
        self.text = 'Model test'
        self.icon = ft.icons.FUNCTIONS

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的模型测试功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))



