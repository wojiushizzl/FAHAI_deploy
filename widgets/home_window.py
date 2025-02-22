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
        self.padding = ft.Padding(0, 0, 30, 30)

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
        self.expand = True
        self.icon = ft.icons.FIT_SCREEN

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        select_flow_label = ft.Text('Select the flow', size=15)
        flow_options = CONFIG_OBJ['deploy_function']['project_list'].split(',')[0:-1]
        flow_options = [ft.dropdown.Option(i, i) for i in flow_options]
        current_flow = CONFIG_OBJ['home']['Single_flow']
        flow_select = ft.Dropdown(
            options=flow_options,
            value=current_flow,
            dense=True,
            text_size=14,
            expand=1,
            on_change=self.flow_select_change)
        self.flow_result = ft.Markdown()
        self.flow_result.value = f"当前流程：{CONFIG_OBJ['home']['Single_flow']}"
        self.visual_result = ft.Image(src='/images/python4.png',filter_quality=ft.FilterQuality.MEDIUM,expand=1)
        self.start_stop_btn = ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=self.on_start_stop_btn_click)
        self.progress_bar = ft.ProgressBar( height=3, visible=False,expand=1)

        row1 = ft.Row([select_flow_label, flow_select, self.start_stop_btn])
        row2 = ft.Row([self.progress_bar])
        row4 = ft.Row([self.flow_result])
        row3 = ft.Row([self.visual_result],expand=1,alignment=ft.MainAxisAlignment.CENTER)
        card_content = ft.Container(ft.Column([row1, row2, row3, row4], spacing=10), padding=10)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(1,1,1,1),expand=1)

        self.content = ft.Column([card], alignment=ft.MainAxisAlignment.CENTER)


    
    def flow_select_change(self, e: ft.ControlEvent):
        """流程选择改变事件"""
        print("===>flow_select_change")
        flow = e.control.value
        self.flow_result.value = f"当前流程：{flow}"
        self.page.update()
        CONFIG_OBJ['home']['Single_flow'] = flow
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
    
    def on_start_stop_btn_click(self, e: ft.ControlEvent):
        """开始流程"""
        print("===>switch_flow")
        if self.start_stop_btn.icon == ft.icons.PLAY_ARROW:
            self.start_flow(e)
        else:
            self.stop_flow(e)


    def stop_flow(self, e: ft.ControlEvent):
        """停止流程"""
        print("===>stop_flow")
        self.start_stop_btn.icon = ft.icons.PLAY_ARROW
        self.progress_bar.visible = False
        self.page.update()

    def start_flow(self, e: ft.ControlEvent):
        """开始流程"""
        print("===>start_flow")
        self.start_stop_btn.icon = ft.icons.STOP
        self.progress_bar.visible = True
        self.page.update()


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
        flow_options = CONFIG_OBJ['deploy_function']['project_list'].split(',')[0:-1]
        flow_options = [ft.dropdown.Option(i, i) for i in flow_options]

        select_flow1_label = ft.Text('Select the flow', size=15)
        current_flow1 = CONFIG_OBJ['home']['Double_flow1']
        flow_select1 = ft.Dropdown(
            options=flow_options,
            value=current_flow1,
            dense=True,
            text_size=14,
            expand=1,
            on_change=self.flow1_select_change)
        self.flow1_result = ft.Markdown()
        self.flow1_result.value = f"当前流程：{CONFIG_OBJ['home']['Double_flow1']}"
        self.visual1_result = ft.Image(src='/images/python4.png',filter_quality=ft.FilterQuality.MEDIUM,expand=1)
        self.start_stop_btn1 = ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=self.on_start_stop_btn1_click)
        self.progress_bar1 = ft.ProgressBar( height=3, visible=False,expand=1)

        flow1_row1 = ft.Row([select_flow1_label, flow_select1, self.start_stop_btn1])
        flow1_row2 = ft.Row([self.progress_bar1])
        flow1_row4 = ft.Row([self.flow1_result])
        flow1_row3 = ft.Row([self.visual1_result],expand=1,alignment=ft.MainAxisAlignment.CENTER)
        flow1_card_content = ft.Container(ft.Column([flow1_row1, flow1_row2, flow1_row3, flow1_row4], spacing=10), padding=10)
        flow1_card = ft.Card(flow1_card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(1,1,1,1),expand=1)



        select_flow2_label = ft.Text('Select the flow', size=15)
        current_flow2 = CONFIG_OBJ['home']['Double_flow2']
        flow_select2 = ft.Dropdown(
            options=flow_options,
            value=current_flow2,
            dense=True,
            text_size=14,
            expand=1,
            on_change=self.flow2_select_change)
        self.flow2_result = ft.Markdown()
        self.flow2_result.value = f"当前流程：{CONFIG_OBJ['home']['Double_flow2']}"
        self.visual2_result = ft.Image(src='/images/python4.png',filter_quality=ft.FilterQuality.MEDIUM,expand=1)
        self.start_stop_btn2 = ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=self.on_start_stop_btn2_click)
        self.progress_bar2 = ft.ProgressBar( height=3, visible=False,expand=1)

        flow2_row1 = ft.Row([select_flow2_label, flow_select2, self.start_stop_btn2])
        flow2_row2 = ft.Row([self.progress_bar2])
        flow2_row4 = ft.Row([self.flow2_result])
        flow2_row3 = ft.Row([self.visual2_result],expand=1,alignment=ft.MainAxisAlignment.CENTER)
        flow2_card_content = ft.Container(ft.Column([flow2_row1, flow2_row2, flow2_row3, flow2_row4], spacing=10), padding=10)
        flow2_card = ft.Card(flow2_card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(1,1,1,1),expand=1)

        self.content = ft.Row([flow1_card, flow2_card], alignment=ft.MainAxisAlignment.CENTER)
        


    def flow1_select_change(self, e: ft.ControlEvent):
        """流程选择改变事件"""
        print("===>flow_select_change")
        flow = e.control.value
        self.flow1_result.value = f"当前流程：{flow}"
        self.page.update()
        CONFIG_OBJ['home']['Double_flow1'] = flow
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
    
    def on_start_stop_btn1_click(self, e: ft.ControlEvent):
        """开始流程"""
        print("===>switch_flow")
        if self.start_stop_btn1.icon == ft.icons.PLAY_ARROW:
            self.start_flow1(e)
        else:
            self.stop_flow1(e)


    def stop_flow1(self, e: ft.ControlEvent):
        """停止流程"""
        print("===>stop_flow")
        self.start_stop_btn1.icon = ft.icons.PLAY_ARROW
        self.progress_bar1.visible = False
        self.page.update()

    def start_flow1(self, e: ft.ControlEvent):
        """开始流程"""
        print("===>start_flow")
        self.start_stop_btn1.icon = ft.icons.STOP
        self.progress_bar1.visible = True
        self.page.update()
    def flow2_select_change(self, e: ft.ControlEvent):
        """流程选择改变事件"""
        print("===>flow_select_change")
        flow = e.control.value
        self.flow2_result.value = f"当前流程：{flow}"
        self.page.update()
        CONFIG_OBJ['home']['Double_flow2'] = flow
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
    
    def on_start_stop_btn2_click(self, e: ft.ControlEvent):
        """开始流程"""
        print("===>switch_flow")
        if self.start_stop_btn2.icon == ft.icons.PLAY_ARROW:
            self.start_flow2(e)
        else:
            self.stop_flow2(e)


    def stop_flow2(self, e: ft.ControlEvent):
        """停止流程"""
        print("===>stop_flow")
        self.start_stop_btn2.icon = ft.icons.PLAY_ARROW
        self.progress_bar2.visible = False
        self.page.update()

    def start_flow2(self, e: ft.ControlEvent):
        """开始流程"""
        print("===>start_flow")
        self.start_stop_btn2.icon = ft.icons.STOP
        self.progress_bar2.visible = True
        self.page.update()


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
        self.content = ft.Column([ft.Text("这是包含多通道图像处理功能的界面，功能即将推出", size=24)],alignment=ft.MainAxisAlignment.CENTER)
