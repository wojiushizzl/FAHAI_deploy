import flet as ft
import cv2


class CamTestPage(ft.Tab):
    def __init__(self):
        """相机测试页面"""
        super().__init__()
        self.text = 'CAM test'
        self.icon = ft.icons.FUNCTIONS

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        cam_type='0'
        cam_idx='0'
        cam_size='640'
        cam_test_label = ft.Text('CAM test', size=15)
        cam_type_label = ft.Text('CAM type', size=12)
        cam_idx_label = ft.Text('CAM index', size=12)
        self.cam_type_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', 'CV CAM'),
            ft.dropdown.Option('1', 'Hikvision'),
            ft.dropdown.Option('2', 'other',disabled=True)
        ], dense=True, text_size=12, expand=1, value=cam_type)
        self.cam_idx_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', '0'),
            ft.dropdown.Option('1', '1'),
            ft.dropdown.Option('2', '2'),
            ft.dropdown.Option('3', '3'),
        ], dense=True, text_size=12, expand=1, value=cam_idx)
        cam_size_label = ft.Text('CAM size', size=12)
        self.cam_size_input = ft.TextField(value=cam_size,text_size=12)
        cam_image = ft.Image(src='/images/python4.png',filter_quality=ft.FilterQuality.MEDIUM,expand=1)
        self.cam_test_btn = ft.IconButton(ft.icons.PLAY_ARROW, on_click=self.cam_test_btn_clicked)
        self.cam_test_btn.icon_color = ft.colors.GREEN


        row1 = ft.Row([cam_type_label, ft.Row(expand=1),self.cam_type_input, ])
        row2 = ft.Row([cam_idx_label, ft.Row(expand=1),self.cam_idx_input, ])
        row3 = ft.Row([cam_size_label,  ft.Row(expand=1),self.cam_size_input])
        row4 = ft.Row([ ft.Row(expand=1),self.cam_test_btn])
        row5 = ft.Row([cam_image],expand=1)



        card_content = ft.Container(ft.Column([row1, row2, row3, row4, row5], spacing=20), padding=20)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))
        column = ft.Column([cam_test_label,card], width=720, spacing=12)
        tab_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))
        self.content = ft.Column([tab_container], scroll=ft.ScrollMode.AUTO)    


    def cam_test_btn_clicked(self,e:ft.ControlEvent):
        """相机测试按钮点击事件"""
        if self.cam_test_btn.icon == ft.icons.PLAY_ARROW:
            self.cam_test_btn.icon_color = ft.colors.RED
            self.cam_test_btn.icon=ft.icons.STOP
            self.page.update()
            self.cam_start()
        else:
            self.cam_test_btn.icon_color = ft.colors.GREEN
            self.cam_test_btn.icon=ft.icons.PLAY_ARROW
            self.page.update()
            self.cam_stop()

    def cam_start(self):
        """相机开始"""


        print('相机开始')

    def cam_stop(self):
        """相机停止"""
        print('相机停止')


