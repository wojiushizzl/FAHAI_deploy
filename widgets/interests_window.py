import flet as ft
from custom_widgets.image_viewer import ImageViewer
from common.app_setting import Setting, CONFIG_OBJ
import os
import pickle
import datetime
import time
from threading import Thread
from typing import List, Optional


class InterestsWindow(ft.Container):
    def __init__(self):
        """兴趣内容窗口"""
        super().__init__()
        self.expand = 1
        self.padding = ft.Padding(10, 0, 82, 30)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.tab1 = BaseTab1()
        self.tab2 = BaseTab2()
        self.tab3 = BaseTab3()
        self.tab4 = BaseTab4()
        self.tab5 = BaseTab5()


        tab_widget = ft.Tabs(tabs=[self.tab1, self.tab2, self.tab3, self.tab4, self.tab5], animation_duration=300,
                             selected_index=1, tab_alignment=ft.TabAlignment.START)
        self.content = tab_widget


class BaseTab1(ft.Tab):
    def __init__(self):
        """基础功能页面"""
        super().__init__()
        self.text = '基础功能'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))




class BaseTab2(ft.Tab):
    def __init__(self):
        """基础功能页面"""
        super().__init__()
        self.text = '基础功能'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))


class BaseTab3(ft.Tab):
    def __init__(self):
        """基础功能页面"""
        super().__init__()
        self.text = '基础功能'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))

class BaseTab4(ft.Tab):
    def __init__(self):
        """基础功能页面"""
        super().__init__()
        self.text = '基础功能'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))


class BaseTab5(ft.Tab):
    def __init__(self):
        """基础功能页面"""
        super().__init__()
        self.text = '基础功能'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))

