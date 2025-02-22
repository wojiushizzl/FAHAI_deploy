import flet as ft
from common.app_setting import Setting, CONFIG_OBJ
import time
from threading import Thread

class Screen(ft.Container):
    def __init__(self, index: str):
        super().__init__()
        self.index = index
        self.expand = 1
        self.padding = ft.Padding(0, 0, 0, 0)
        self.flow_thread = None
        self.is_running = False
        self._init_widgets()
    def _init_widgets(self):
        """初始化组件"""
        select_flow_label = ft.Text('Select the flow', size=15)
        flow_options = CONFIG_OBJ['deploy_function']['project_list'].split(',')[0:-1]
        flow_options = [ft.dropdown.Option(i, i) for i in flow_options]
        current_flow = CONFIG_OBJ['home'][self.index]
        flow_select = ft.Dropdown(
            options=flow_options,
            value=current_flow,
            dense=True,
            text_size=14,
            expand=1,
            on_change=self.flow_select_change)
        self.flow_result = ft.Markdown()
        self.flow_result.value = f"当前流程：{CONFIG_OBJ['home'][self.index]}"
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
        CONFIG_OBJ['home'][self.index] = flow
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
    
    def on_start_stop_btn_click(self, e: ft.ControlEvent):
        """开始流程"""
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
        
        self.is_running = False
        if self.flow_thread:
            self.flow_thread.join()
            self.flow_thread = None
        print("===>stop_flow_end")


    def start_flow(self, e: ft.ControlEvent):
        """开始流程"""
        print("===>start_flow")
        self.start_stop_btn.icon = ft.icons.STOP
        self.progress_bar.visible = True
        self.page.update()
        
        self.is_running = True
        self.flow_thread = Thread(target=self.start_flow_thread, args=(e,))
        self.flow_thread.start()

    def start_flow_thread(self, e: ft.ControlEvent):
        """开始流程线程"""
        print("===>start_flow_thread")
        while self.is_running:
            print("===>start_flow_thread_loop")
            time.sleep(0.5)
            print('listen trigger')
            time.sleep(0.5)
            print('detected trigger')
            time.sleep(0.5)
            print('get frame from CAM')
            time.sleep(0.5)
            print('detect object')
            time.sleep(0.5)
            print('logic process')
            time.sleep(0.5)
            print('output result')
            time.sleep(0.5)

