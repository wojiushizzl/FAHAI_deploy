import flet as ft
from common.app_setting import Setting, CONFIG_OBJ
from threading import Thread
import datetime
import time
from custom_widgets.screen import Screen
from custom_widgets.screen_layer import Screen_layer

class HomeWindow(ft.Container):
    def __init__(self):
        """首页窗口"""
        super().__init__()
        self.expand = True
        self.padding = ft.Padding(0, 0, 30, 30)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.tab1 = One_Screen()
        self.tab2 = Two_Screen()
        self.tab4 = Four_Screen()
        self.tab5 = Layer_Screen()

        selected_tab = CONFIG_OBJ['home']['selected_tab']

        tab_widget = ft.Tabs(tabs=[self.tab1, self.tab2, self.tab4, self.tab5], animation_duration=300,
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
        self.flow_thread = None
        self.is_running = False
        self.text = 'Single'
        self.expand = True
        self.icon = ft.icons.FIT_SCREEN

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.screen1 = Screen('single_flow')
        self.content = ft.Column([self.screen1],alignment=ft.MainAxisAlignment.CENTER)


class Two_Screen(ft.Tab):
    def __init__(self):
        """双通道页面"""
        super().__init__()
        self.text = 'Double'
        self.expand = True
        self.icon = ft.icons.SPLITSCREEN

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.screen1 = Screen('double_flow1')
        self.screen2 = Screen('double_flow2')
        row1 = ft.Row([self.screen1, self.screen2],expand=1)
        self.content = ft.Column([row1],alignment=ft.MainAxisAlignment.CENTER)


        


class Four_Screen(ft.Tab):
    def __init__(self):
        """四通道页面"""
        super().__init__()
        self.text = 'Multi'
        self.expand = True
        self.icon = ft.icons.VERTICAL_SPLIT

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.screen1 = Screen('multi_flow1')
        self.screen2 = Screen('multi_flow2')
        self.screen3 = Screen('multi_flow3')
        self.screen4 = Screen('multi_flow4')
        row1 = ft.Row([self.screen1, self.screen2],expand=1)
        row2 = ft.Row([self.screen3, self.screen4],expand=1)
        self.content = ft.Column([row1, row2],alignment=ft.MainAxisAlignment.CENTER)



class Layer_Screen(ft.Tab):
    def __init__(self):
        """单通道页面"""
        super().__init__()
        self.text = 'Layer'
        self.expand = True
        self.icon = ft.icons.FIT_SCREEN

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.screen1 = Screen_layer('layer_flow')
        self.content = ft.Column([self.screen1],alignment=ft.MainAxisAlignment.CENTER)