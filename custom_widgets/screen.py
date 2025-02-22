import flet as ft
from common.app_setting import Setting, CONFIG_OBJ
import time
from threading import Thread
from ultralytics import YOLO
import cv2
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
        self.current_flow = CONFIG_OBJ['home'][self.index]
        flow_select = ft.Dropdown(
            options=flow_options,
            value=self.current_flow,
            dense=True,
            text_size=14,
            expand=1,
            on_change=self.flow_select_change)
        self.flow_result = ft.Markdown()
        self.flow_result.value = f"当前流程：{self.current_flow}"
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
        self.current_flow = flow
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
        print(f"\033[32m===>stop_flow [{self.current_flow}]\033[0m")
        self.start_stop_btn.icon = ft.icons.PLAY_ARROW
        self.progress_bar.visible = False
        self.page.update()
        
        self.is_running = False
        if self.flow_thread:
            self.flow_thread.join()
            self.flow_thread = None
        print(f"\033[32m===>stop_flow_end [{self.current_flow}]\033[0m")


    def start_flow(self, e: ft.ControlEvent):
        """开始流程"""
        print(f"\033[32m===>start_flow [{self.current_flow}]\033[0m")
        self.start_stop_btn.icon = ft.icons.STOP
        self.progress_bar.visible = True
        self.page.update()
        
        self.is_running = True
        self.flow_thread = Thread(target=self.start_flow_thread, args=(e,))
        self.flow_thread.start()

    def start_flow_thread(self, e: ft.ControlEvent):
        """开始流程线程"""
        print(f"\033[32m===>start_flow_thread [{self.current_flow}]\033[0m")
        flow_config = CONFIG_OBJ[self.current_flow]
        print(f'\033[33m[{self.current_flow}] flow_config: {flow_config}\033[0m')
        if not self.check_config(flow_config):
            print(f'\033[31m[{self.current_flow}] config error\033[0m')
            self.flow_thread=None
            self.stop_flow(e)
        if_use_status_output = flow_config['status_output']
        if if_use_status_output == 'True':
            self._start_status_output_thread(flow_config)

        while self.is_running:
            print(f"\033[32m===>start_flow_thread_loop [{self.current_flow}]\033[0m")
            time.sleep(0.5)
            if flow_config['trigger_type'] == '0':
                #实时探测模式
                ret,frame=self._get_frame_from_cam(flow_config)
                if ret:
                    print(f'\033[32m[{self.current_flow}] object detected\033[0m')
                    result=self._detect_object(frame,flow_config)
                    print(f'\033[32m[{self.current_flow}] logic process\033[0m')
                    ok_ng=self._logic_process(result,flow_config)
                    print(f'\033[32m[{self.current_flow}] output result\033[0m')
                    self._output_result(ok_ng,flow_config)
                else:
                    print(f'\033[31m[{self.current_flow}] get frame from CAM failed\033[0m')
                    self.flow_result.value = f"当前流程：[{self.current_flow}] 获取相机帧失败"
                    self.page.update()
                    self.flow_thread=None
                    self.stop_flow(e)
            elif flow_config['trigger_type'] == '1':
                #触发器模式
                print(f'\033[32m[{self.current_flow}] listen trigger\033[0m')
                time.sleep(0.5)
                print(f'\033[32m[{self.current_flow}] get frame from CAM\033[0m')
                time.sleep(0.5)
                print(f'\033[32m[{self.current_flow}] detect object\033[0m')
                time.sleep(0.5)
                print(f'\033[32m[{self.current_flow}] logic process\033[0m')
                time.sleep(0.5)
                print(f'\033[32m[{self.current_flow}] output result\033[0m')
                time.sleep(0.5)
            elif flow_config['trigger_type'] == '2':
                #定时探测模式
                print(f'\033[32m[{self.current_flow}] get frame from CAM\033[0m')
                time.sleep(0.5)
                print(f'\033[32m[{self.current_flow}] object detected\033[0m')
                time.sleep(0.5)
                print(f'\033[32m[{self.current_flow}] logic process\033[0m')
                time.sleep(0.5)
                print(f'\033[32m[{self.current_flow}] output result\033[0m')
                time.sleep(0.5)
                

    def check_config(self, flow_config):
        """检查配置"""
        self.flow_result.value = f"当前流程：{self.current_flow} 配置检查中..."
        self.page.update()
        # check camera
        cam_type = flow_config['cam1_type']
        cam_idx = flow_config['cam1_idx']
        cam_size = flow_config['cam1_size']
        cam_use = flow_config['cam1_use']
        cam_check_result = self._check_camera(cam_type, cam_idx, cam_size, cam_use)
        # check model
        model_path = flow_config['model1_path']
        model_confidence = flow_config['model1_confidence']
        model_iou = flow_config['model1_iou']
        model_use = flow_config['model1_use']
        model_check_result = self._check_model(model_path, model_confidence, model_iou, model_use)
        # check modbus TCP
        trigger_type = flow_config['trigger_type']
        plc_ip = flow_config['plc_ip']
        plc_port = flow_config['plc_port']
        if trigger_type == '0':
            plc_connect_check_result = True
        elif trigger_type == '1':
            plc_connect_check_result = self._check_plc_connect(plc_ip, plc_port)
        else:
            plc_connect_check_result = True
        # check gpio
        if_use_gpio = flow_config['gpio']   
        if if_use_gpio == 'True':
            gpio_output_point = flow_config['gpio_output_point']
            gpio_output_check_result = self._check_gpio_output(gpio_output_point)
        else:
            gpio_output_check_result = True

        #check socket tcp
        if_use_socket = flow_config['socket']
        if if_use_socket == 'True':
            socket_ip = flow_config['socket_ip']
            socket_port = flow_config['socket_port']
            socket_check_result = self._check_socket(socket_ip, socket_port)
        else:
            socket_check_result = True
        
        # check result update
        self.flow_result.value = f"当前流程：[{self.current_flow}] "
        self.flow_result.value += f"CAM:{'✅' if cam_check_result else '❌'} "
        self.flow_result.value += f"MODEL:{'✅' if model_check_result else '❌'} "
        self.flow_result.value += f"PLC:{'✅' if plc_connect_check_result else '❌'} "
        self.flow_result.value += f"GPIO:{'✅' if gpio_output_check_result else '❌'} "
        self.flow_result.value += f"SOCKET:{'✅' if socket_check_result else '❌'}"
        self.page.update()

        if cam_check_result and model_check_result and plc_connect_check_result and gpio_output_check_result and socket_check_result:
            self.flow_result.value += f" 配置检查通过"
            self.page.update()
            return True
        else:
            self.flow_result.value += f" 配置检查失败"
            self.page.update()
            return False

    def _check_camera(self, cam_type, cam_idx, cam_size, cam_use):
        """检查相机"""
        if cam_use:
            if cam_type == '0':
                print(f"\033[32m===>check_camera CV camera\033[0m")
                self.cap = cv2.VideoCapture(int(cam_idx))
                return True
            elif cam_type == '1':
                print(f"\033[32m===>check_camera HIK camera\033[0m")
                from hik_CAM.getFrame import start_cam, exit_cam, get_frame
                self.cap, self.stOutFrame, self.data_buf = start_cam(nConnectionNum=int(cam_idx))
                return True
            else:
                return False
        else:
            return True
        
    def _check_model(self, model_path, model_confidence, model_iou, model_use):
        """检查模型"""
        if model_use:
            self.model = YOLO(model_path)
            return True
        else:
            return True
        
    def _check_plc_connect(self, plc_ip, plc_port):
        """检查PLC连接"""
        #TODO  检查PLC连接
        return True
    
    
    def _check_gpio_output(self, gpio_output_point):
        """检查GPIO输出"""
        #TODO  检查GPIO输出
        return True

    def _check_socket(self, socket_ip, socket_port):
        """检查socket连接"""
        #TODO  检查socket连接
        return True

    def _start_status_output_thread(self, flow_config):
        """启动状态输出线程"""
        #TODO  启动状态输出线程
        self.status_output_thread = Thread(target=self._status_output_thread, args=(flow_config,))
        self.status_output_thread.start()

    def _status_output_thread(self, flow_config):
        """状态输出线程"""
        plc_ip = flow_config['plc_ip']
        plc_port = flow_config['plc_port']
        status_output_address = flow_config['status_output_address']
        status_output_value = flow_config['status_output_value']
        while self.is_running:
            print(f"status_out_put : {status_output_address} {status_output_value}")
            time.sleep(3)
        self.status_output_thread = None

    def _get_frame_from_cam(self, flow_config):
        """获取相机帧"""
        print(f'\033[32m[{self.current_flow}] get frame from CAM\033[0m')
        if flow_config['cam1_type'] == "0":
            ret, frame = self.cap.read()
        elif flow_config['cam1_type'] == "1":
            from hik_CAM.getFrame import start_cam, exit_cam, get_frame
            ret, frame = get_frame(self.cap, self.stOutFrame)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return ret, frame

    def _detect_object(self, frame, flow_config):
        """检测物体"""
        print(f'\033[32m[{self.current_flow}] detect object\033[0m')
        conf_thres = flow_config['model1_confidence']
        iou_thres = flow_config['model1_iou']
        img_size = flow_config['cam1_size']
        results = self.model(frame, conf=conf_thres, iou=iou_thres, imgsz=img_size)
        return results

    def _logic_process(self, result, flow_config):
        """逻辑处理"""
        #TODO  逻辑处理 
        return True, None

    def _output_result(self, ok_ng, flow_config):
        """输出结果"""
        #TODO  输出结果
        return True, None