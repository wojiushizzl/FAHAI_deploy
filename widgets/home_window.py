import flet as ft
from common.app_setting import Setting, CONFIG_OBJ
from threading import Thread
import datetime
import time

class HomeWindow(ft.Container):
    def __init__(self):
        """首页窗口"""
        super().__init__()
        self.expand = True
        self.padding = ft.Padding(0, 0, 72, 30)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.tab1 = One_Screen()
        self.tab2 = Two_Screen()
        self.tab4 = Four_Screen()

        selected_tab = CONFIG_OBJ['home']['selected_tab']

        tab_widget = ft.Tabs(tabs=[self.tab1, self.tab2, self.tab4], animation_duration=300,
                             selected_index=int(selected_tab), tab_alignment=ft.TabAlignment.START,key='home_tab',on_change=self.home_tab_change)
        self.content = tab_widget

    def home_tab_change(self, e: ft.ControlEvent):
        """首页tab切换事件"""
        print("===>home_tab_change")
        selected_index = e.control.selected_index
        CONFIG_OBJ['home']['selected_tab'] = str(selected_index)
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
        self.page.update()


class One_Screen(ft.Tab):
    def __init__(self):
        """单通道页面"""
        super().__init__()
        self.text = 'Single'
        self.icon = ft.icons.FIT_SCREEN

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))
        

class Two_Screen(ft.Tab):
    def __init__(self):
        """双通道页面"""
        super().__init__()
        self.text = 'Double'
        self.icon = ft.icons.SPLITSCREEN

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))
        
class Four_Screen(ft.Tab):
    def __init__(self):
        """四通道页面"""
        super().__init__()
        self.text = 'Multi'
        self.icon = ft.icons.VERTICAL_SPLIT

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))