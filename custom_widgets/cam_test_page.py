import flet as ft
import cv2
from threading import Thread

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
        self.cam_image = ft.Image(src='/images/python4.png',filter_quality=ft.FilterQuality.MEDIUM,expand=1)
        self.cam_test_btn = ft.IconButton(ft.icons.PLAY_ARROW, on_click=self.cam_test_btn_clicked)
        self.cam_test_btn.icon_color = ft.colors.GREEN


        row1 = ft.Row([cam_type_label, ft.Row(expand=1),self.cam_type_input, ])
        row2 = ft.Row([cam_idx_label, ft.Row(expand=1),self.cam_idx_input, ])
        row3 = ft.Row([cam_size_label,  ft.Row(expand=1),self.cam_size_input])
        row4 = ft.Row([ ft.Row(expand=1),self.cam_test_btn])
        row5 = ft.Row([self.cam_image],expand=1)



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
        self.is_running = True
        self.cam_thread = Thread(target=self.start_cam_thread)
        self.cam_thread.start()

        print('相机开始')

    def cam_stop(self):
        """相机停止"""
        print('相机停止')
        self.is_running = False

        if self.cap:
            if self.cam_type == '0':
                self.cap.release()
                self.cap = None
            elif self.cam_type == '1':
                from hik_CAM.getFrame import exit_cam
                exit_cam(self.cap, self.data_buf)
                self.cap = None
        self.cam_image.src_base64 = ''
        self.page.update()
        try:
            if self.cam_thread:
                if self.cam_thread.is_alive():
                    self.cam_thread.join()
                    self.cam_thread = None
        except Exception as e:
            print(f'相机停止线程异常: {e}')

    def start_cam_thread(self):
        """相机开始线程"""
        print('相机开始线程')
        self._init_cam()
        
        while self.is_running:
            print('相机线程运行中')
            if self.cam_type == '0':
                ret,frame=self._get_frame_from_cv_cam()
            elif self.cam_type == '1':
                ret,frame=self._get_frame_from_hik_cam()

            self.show_frame(frame)



    def _init_cam(self):
        """初始化相机"""
        print('初始化相机')
        if self.cam_type == '0':
            self.cap = cv2.VideoCapture(int(self.cam_idx))
        elif self.cam_type == '1':
            from hik_CAM.getFrame import start_cam
            self.cap, self.stOutFrame, self.data_buf = start_cam(int(self.cam_idx))

    def _get_frame_from_cv_cam(self):
        """获取CV相机帧"""
        print('获取CV相机帧')
        ret,frame=self.cap.read()
        return ret,frame


    def _get_frame_from_hik_cam(self):
        """获取Hikvision相机帧"""
        print('获取Hikvision相机帧')
        from hik_CAM.getFrame import get_frame
        ret, frame = get_frame(self.cap, self.stOutFrame)
        return ret,frame



    def show_frame(self,frame):
        """显示相机帧"""
        print('显示相机帧')
        self.cam_image.src_base64 = frame
        self.page.update()


