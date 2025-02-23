import flet as ft
from custom_widgets.flow_setting_page import FlowSettingPage
from custom_widgets.cam_test_page import CamTestPage
from custom_widgets.model_test_page import ModelTestPage
from custom_widgets.connect_test_page import ConnectTestPage
from custom_widgets.output_test_page import OutputTestPage
from common.app_setting import Setting, CONFIG_OBJ
import os
import pickle
import datetime
import time
from threading import Thread
from typing import List, Optional
import json


class InterestsWindow(ft.Container):
    def __init__(self):
        """兴趣内容窗口"""
        super().__init__()
        self.expand = 1
        self.padding = ft.Padding(10, 0, 30, 30)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.tab1 = FlowSettingPage()
        self.tab2 = CamTestPage()
        # self.tab3 = ModelTestPage()
        self.tab4 = ConnectTestPage()
        # self.tab5 = OutputTestPage()


        tab_widget = ft.Tabs(tabs=[
            self.tab1, 
            self.tab2, 
            # self.tab3,
            self.tab4,
            # self.tab5
            ], animation_duration=300,
                             selected_index=0, tab_alignment=ft.TabAlignment.START)
        self.content = tab_widget

