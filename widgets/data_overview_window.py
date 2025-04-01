import flet as ft
import os

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

        self.clean_log_btn = ft.TextButton(text="清理日志", on_click=self.clean_log_btn_click)
        # 获取日志文件大小
        file_size = os.path.getsize("user_data/log.log")
        self.log_quantity_text = ft.Text(value=f"日志大小：{file_size}字节", size=12, color=ft.colors.PRIMARY)

        self.row = ft.Row([self.clean_log_btn, ft.Text("|"),self.log_quantity_text], expand=True)

        self.content = ft.Column([self.row, self.log_text], expand=True,scroll=ft.ScrollMode.AUTO)

    # 定时更新log文本
    def update_log_text(self):
        """更新日志文本"""
        with open("user_data/log.log", "r") as f:
            self.log_text.value = f.read()  

    def clean_log_btn_click(self, e: ft.ControlEvent):
        """清理日志按钮点击事件"""
        # 仅保留最近的1000行
        with open("user_data/log.log", "r") as f:
            lines = f.readlines()   
        with open("user_data/log.log", "w") as f:
            f.writelines(lines[-1000:])
        self.update_log_text()
        self.update_log_quantity_text()
        self.page.update()

    def update_log_quantity_text(self):
        """更新日志大小文本"""
        file_size = os.path.getsize("user_data/log.log")
        self.log_quantity_text.value = f"日志大小：{file_size}字节"
        self.page.update()
