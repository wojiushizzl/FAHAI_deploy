import flet as ft
from common.app_setting import Setting, CONFIG_OBJ
import time
from threading import Thread
from ultralytics import YOLO
import cv2
import json
from PIL import Image
from io import BytesIO
import base64
import socket
import os
import pandas as pd

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
        self.visual_result = ft.Image(src='/images/python4.png',fit=ft.ImageFit.CONTAIN,expand=1)
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

        if self.cap:
            self.cap.release()
            self.cap = None

        self.visual_result.src_base64 = ''
        self.page.update()
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

        print(f"\033[32m===>start_flow_thread_loop [{self.current_flow}]\033[0m")
        while self.is_running:
            if flow_config['trigger_type'] == '0':
                #实时探测模式
                ret,frame=self._get_frame_from_cam(flow_config)
                if ret:
                    res=self._detect_object(frame,flow_config)
                    ok_or_ng=self._logic_process(res,flow_config)
                    self._output_result(res,ok_or_ng,flow_config)
                else:
                    print(f'\033[31m[{self.current_flow}] get frame from CAM failed\033[0m')
                    self.flow_result.value = f"当前流程：[{self.current_flow}] 获取相机帧失败"
                    self.page.update()
                    self.flow_thread=None
                    self.stop_flow(e)
            elif flow_config['trigger_type'] == '1':
                #触发器模式
                trigger=self._listen_trigger(flow_config)
                if trigger:
                    ret,frame=self._get_frame_from_cam(flow_config)
                    if ret:
                        res=self._detect_object(frame,flow_config)
                        ok_or_ng=self._logic_process(res,flow_config)
                        self._output_result(res,ok_or_ng,flow_config)
                    else:
                        print(f'\033[31m[{self.current_flow}] get frame from CAM failed\033[0m')
                        self.flow_result.value = f"当前流程：[{self.current_flow}] 获取相机帧失败"
                        self.page.update()
                        self.flow_thread=None
                        self.stop_flow(e)
                else:
                    continue
            elif flow_config['trigger_type'] == '2':
                #定时探测模式
                ret,frame=self._get_frame_from_cam(flow_config)
                if ret:
                    res=self._detect_object(frame,flow_config)
                    ok_or_ng=self._logic_process(res,flow_config)
                    self._output_result(res,ok_or_ng,flow_config)
                else:
                    print(f'\033[31m[{self.current_flow}] get frame from CAM failed\033[0m')
                    self.flow_result.value = f"当前流程：[{self.current_flow}] 获取相机帧失败"
                    self.page.update()
                    self.flow_thread=None
                    self.stop_flow(e)
                time.sleep(1)
                

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
        plc_output = flow_config['plc_output']
        trigger_type = flow_config['trigger_type']
        status_output = flow_config['status_output']
        plc_ip = flow_config['plc_ip']
        plc_port = int(flow_config['plc_port'])

        if trigger_type == '0' and plc_output == 'False' and status_output == 'False':
            plc_connect_check_result = None
        elif trigger_type == '1' or plc_output == 'True' or status_output == 'True':
            plc_connect_check_result = self._check_plc_connect(plc_ip, plc_port)
        else:
            plc_connect_check_result = None
        
        # check gpio
        if_use_gpio = flow_config['gpio']   
        if if_use_gpio == 'True':
            gpio_output_point = flow_config['gpio_output_point']
            gpio_output_check_result = self._check_gpio_output(gpio_output_point)
        else:
            gpio_output_check_result = None

        #check socket tcp
        if_use_model_config = flow_config['model_config_use']
        if_use_socket = flow_config['socket']
        if if_use_socket == 'True' or if_use_model_config == 'True':
            socket_ip = flow_config['socket_ip']
            socket_port = int(flow_config['socket_port'])
            socket_check_result = self._check_socket(socket_ip, socket_port)
        else:
            socket_check_result = None
        #check if save
        if_save_result=flow_config['result_save']
        if if_save_result =='True':
            save_result_check = True
        else:
            save_result_check = None
        # check result update
        self.flow_result.value = f"当前流程：[{self.current_flow}]      "
        self.flow_result.value += f"CAM:{'✅' if cam_check_result == True else '❌' if cam_check_result == False else ' N/A'}   "
        self.flow_result.value += f"MODEL:{'✅' if model_check_result == True else '❌' if model_check_result == False else 'N/A'}   "
        self.flow_result.value += f"PLC:{'✅' if plc_connect_check_result == True else '❌' if plc_connect_check_result == False else 'N/A'}   "
        self.flow_result.value += f"GPIO:{'✅' if gpio_output_check_result == True else '❌' if gpio_output_check_result == False else 'N/A'}   "
        self.flow_result.value += f"SOCKET:{'✅' if socket_check_result == True else '❌' if socket_check_result == False else 'N/A'}   "
        self.flow_result.value += f"SAVE:{'✅' if save_result_check == True else '❌' if save_result_check == False else 'N/A'}    "
        self.page.update()

        if (cam_check_result == True or cam_check_result == None) and \
           (model_check_result == True or model_check_result == None) and \
           (plc_connect_check_result == True or plc_connect_check_result == None) and \
           (gpio_output_check_result == True or gpio_output_check_result == None) and \
           (socket_check_result == True or socket_check_result == None):
            self.flow_result.value += f" 配置检查通过 ===> 流程启动"
            self.page.update()
            return True
        else:
            self.flow_result.value += f" 配置检查失败 ===> 流程停止" 
            self.page.update()
            return False

    def _check_camera(self, cam_type, cam_idx, cam_size, cam_use):
        """检查相机"""
        if cam_use:
            if cam_type == '0':
                try:
                    print(f"\033[32m===>check_camera CV camera\033[0m")
                    self.cap = cv2.VideoCapture(int(cam_idx))
                    return True
                except Exception as e:
                    print(f"===> Error initializing camera: ", e)
                    return False
            elif cam_type == '1':
                try:
                    print(f"\033[32m===>check_camera HIK camera\033[0m")
                    from hik_CAM.getFrame import start_cam, exit_cam, get_frame
                    self.cap, self.stOutFrame, self.data_buf = start_cam(nConnectionNum=int(cam_idx))
                    return True
                except Exception as e:
                    print(f"===> Error initializing camera: ", e)
                    return False
            else:
                return False
        else:
            return True
        
    def _check_model(self, model_path, model_confidence, model_iou, model_use):
        """检查模型"""
        if model_use:
            try:
                self.model = YOLO(model_path)
                return True
            except Exception as e:
                print(f"===> Error initializing model: ", e)
                return False
        else:
            return True
        
    def _check_plc_connect(self, plc_ip: str, plc_port: int):
        """检查PLC连接"""
        try:
            from pymodbus.client import ModbusTcpClient
            self.client = ModbusTcpClient(plc_ip, port=plc_port, slave=1)
            result = self.client.connect()

            if result:
                print(f"===>  PLC initialized, IP: ", plc_ip, "port : ", plc_port, "status : ", result)
            else:
                print(f"===>  PLC connection failed, IP: ", plc_ip, "port : ", plc_port, "status : ", result)

            return result
        except Exception as e:
            print(f"===> Error initializing PLC: ", e)
            return False
    
    
    def _check_gpio_output(self, gpio_output_point):
        """检查GPIO输出"""
        gpio_output_point = int(gpio_output_point)  
        try:    
            import Jetson.GPIO as GPIO
            self.GPIO=GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setwarnings(False)
            self.GPIO.setup(gpio_output_point, self.GPIO.OUT, initial=self.GPIO.LOW)
            return True
        except Exception as e:
            print(f"GPIO error: {e}")
            return False

    def _check_socket(self, socket_ip: str, socket_port: int):
        """检查socket连接"""
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.settimeout(1)
            self.socket_client.connect((socket_ip, socket_port))
            result = True
        except Exception as e:
            print(f"===> Error initializing socket: ", e)
            result = False
        finally:
            self.socket_client.close()
        return result

    def _listen_trigger(self, flow_config):
        """监听触发器"""
        address = int(flow_config['plc_trigger_address'])
        count = int(flow_config['plc_trigger_count'])
        slave=1
        self.client.connect()
        result = self.client.read_holding_registers(address, count,slave=1)
        type=flow_config['signal_type']
        # 当type为0时，监听result的上升延信号
        if type == '0':
            # 记录上一次的值
            if not hasattr(self, 'last_trigger_value'):
                self.last_trigger_value = 0
            
            # 获取当前值
            current_value = result.registers[0] if result and result.registers else 0
            
            # 检测上升沿 - 从0变为1
            if current_value == 1 and self.last_trigger_value == 0:
                self.last_trigger_value = current_value
                print(f"\033[32m===>listen_trigger [{self.current_flow}] trigger 上升沿\033[0m")
                return True
            
            # 更新上一次的值
            self.last_trigger_value = current_value
            return False
        else:
            # 记录上一次的值
            if not hasattr(self, 'last_trigger_value'):
                self.last_trigger_value = 1
            
            # 获取当前值
            current_value = result.registers[0] if result and result.registers else 1   
            
            # 检测下降沿 - 从1变为0
            if current_value == 0 and self.last_trigger_value == 1:
                self.last_trigger_value = current_value
                print(f"\033[32m===>listen_trigger [{self.current_flow}] trigger 下降沿\033[0m")
                return True
            
            # 更新上一次的值
            self.last_trigger_value = current_value
            return False    
        

    def _start_status_output_thread(self, flow_config):
        """启动状态输出线程"""
        self.status_output_thread = Thread(target=self._status_output_thread, args=(flow_config,))
        self.status_output_thread.start()

    def _status_output_thread(self, flow_config):
        """状态输出线程"""
        status_output_address = int(flow_config['status_output_address'])
        status_output_value = int(flow_config['status_output_value'])
        while self.is_running:
            self.client.write_register(status_output_address, status_output_value)
            print(f"status_out_put : {status_output_address} {status_output_value}")
            time.sleep(3)
        self.status_output_thread = None

    def _get_frame_from_cam(self, flow_config):
        """获取相机帧"""
        print(f'\033[32m[{self.current_flow}] get frame from CAM\033[0m')
        if flow_config['cam1_type'] == "0":
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 重置指针（部分摄像头有效）
            for _ in range(int(self.cap.get(cv2.CAP_PROP_BUFFERSIZE))):  # 清空缓冲区
                self.cap.grab()  # 快速丢弃旧帧（不解码）
            ret, frame = self.cap.read()  # 读取最新帧


        elif flow_config['cam1_type'] == "1":
            from hik_CAM.getFrame import start_cam, exit_cam, get_frame
            ret, frame = get_frame(self.cap, self.stOutFrame)
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except cv2.error as e:
            print(f"OpenCV error: {e}")
        return ret, frame

    def _detect_object(self, frame, flow_config):
        """检测物体"""
        print(f'\033[32m[{self.current_flow}] detect object\033[0m')
        if_model_config_use = flow_config['model_config_use']
        if if_model_config_use == 'True':
            model_path,conf_thres,iou_thres,img_size= self._load_model_config(flow_config)
            self.model = YOLO(model_path)
        else:
            conf_thres = float(flow_config['model1_confidence'])
            iou_thres = float(flow_config['model1_iou'])
            img_size = int(flow_config['cam1_size'])
        results = self.model(frame, conf=conf_thres, iou=iou_thres, imgsz=img_size)
        return results

    def _load_model_config(self, flow_config):
        """加载模型配置"""
        model_config_file_path = flow_config['model_config_file_path']
        model_config_file = pd.read_csv(model_config_file_path,header=0,index_col=0,encoding='utf-8')
        socket_ip = flow_config['socket_ip']
        socket_port = int(flow_config['socket_port'])
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.settimeout(1)
            self.socket_client.connect((socket_ip, socket_port))
            self.socket_client.sendall(b'LON\r\n')
            response = self.socket_client.recv(1024)
            if response:
                print(f"Received response: {response.decode('utf-8')}")
                self.socket_data=response.decode('utf-8').strip()
            else:
                print("\033[31mNo data received.\033[0m")
        except Exception as e:
            print(f"\033[31mError: {e}\033[0m")
        finally:
            self.socket_client.close()
        data_PN=int(self.socket_data[-10:])
        print(f'data: {self.socket_data}    data_PN: {data_PN}')
        model_path=model_config_file.loc[data_PN]['model']
        conf=float(model_config_file.loc[data_PN]['conf'])
        iou=float(model_config_file.loc[data_PN]['iou'])
        img_size=int(model_config_file.loc[data_PN]['imgsz'])
        self.selected_objects=model_config_file.loc[data_PN]['select_objects'].split(',')[0:-1]

        print(f'model_path: {model_path}')
        print(f'conf: {conf}')
        print(f'iou: {iou}')
        print(f'img_size: {img_size}')
        print(f'selected_objects: {self.selected_objects}')
        return model_path,conf,iou,img_size

    def _logic_process(self, result, flow_config):
        """逻辑处理"""
        print(f'\033[32m[{self.current_flow}] logic process\033[0m')
        res_json_load = json.loads(result[0].tojson())
        detected_objects = [r['name'] for r in res_json_load]   
        print(f'detected_objects: {detected_objects}')
        if_model_config_use = flow_config['model_config_use']
        if if_model_config_use == 'True':
            self.selected_objects = self.selected_objects
        else:
            self.selected_objects = flow_config['model1_selected_objects'].split(',')[0:-1]

        print(f'selected_objects: {self.selected_objects}')
        logic_type = flow_config['logic_type']
        if logic_type == '0':  # detected objects [in] selected_objects
            check_result = all(item in self.selected_objects for item in detected_objects) and len(detected_objects) > 0

        elif logic_type == '1':  # selected_objects [in] detected objects
            check_result = all(item in detected_objects for item in self.selected_objects) and len(detected_objects) > 0
        elif logic_type == '2':  # selected_objects [=] detected objects
            check_result = len(detected_objects) == len(self.selected_objects) and all(item in detected_objects for item in self.selected_objects)
        else:
            check_result = False
        return check_result

    def _output_result(self,res, ok_ng: bool, flow_config):
        """输出结果"""
        print(f'\033[32m[{self.current_flow}] output result\033[0m')
        if_gpio_output = flow_config['gpio']
        if_visual_output = flow_config['visual']
        if_plc_output = flow_config['plc_output']
        if_save_output = flow_config['result_save']

        if if_gpio_output == 'True':
            self._gpio_output( ok_ng, flow_config)
        
        if if_visual_output == 'True':
            self._visual_output(res, ok_ng, flow_config)
        
        if if_plc_output == 'True':
            self._plc_output(ok_ng, flow_config)
        
        if if_save_output == 'True':
            self._save_output(res, ok_ng, flow_config)

        
    def _gpio_output(self, ok_ng: bool, flow_config):
        """GPIO输出"""
        gpio_output_point = int(flow_config['gpio_output_point'])
        if ok_ng:
            self.GPIO.output(gpio_output_point, self.GPIO.HIGH)
        else:
            self.GPIO.output(gpio_output_point, self.GPIO.LOW)

    def _visual_output(self, res, ok_ng: bool, flow_config):
        """视觉输出"""
        res_plotted = res[0].plot()
        if ok_ng:
            res_plotted = cv2.putText(res_plotted, "Logic check pass", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        (0, 255, 0), 2, cv2.LINE_AA)
        else:
            res_plotted = cv2.putText(res_plotted, "Logic check failed", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        (0, 0, 255), 2, cv2.LINE_AA)
        # add time text
        res_plotted = cv2.putText(res_plotted,
                                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 0, 255), 2, cv2.LINE_AA)
        
        # add  PN text
        if_model_config_use = flow_config['model_config_use']
        if if_model_config_use == 'True':
            res_plotted = cv2.putText(res_plotted, self.socket_data, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 0, 255), 2, cv2.LINE_AA)
        img_pil = Image.fromarray(res_plotted)
        img_byte_arr = BytesIO()
        img_pil.save(img_byte_arr, format="JPEG")
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        self.visual_result.src_base64 = img_base64
        self.page.update()

    def _plc_output(self, ok_ng: bool, flow_config):
        """PLC输出"""
        plc_address = int(flow_config['plc_output_address'])
        plc_value = int(flow_config['plc_output_value'])
        if ok_ng:
            self.client.write_register(plc_address, plc_value)
        else:
            self.client.write_register(plc_address,0)

    def _save_output(self, res, ok_ng: bool, flow_config):
        """保存输出"""
        save_path = flow_config['result_save_path']
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        frame = res[0].plot()
        res_json = res[0].tojson()
        md_file_name = self.current_flow + '_' + '.md'
        if not os.path.exists(os.path.join(save_path, md_file_name)):
            with open(os.path.join(save_path, md_file_name), 'w') as f:
                f.write(f'## {self.current_flow} {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n')
        try:
            if_model_config_use = flow_config['model_config_use']
            if if_model_config_use == 'True':
                pn = self.socket_data
            else:
                pn = self.current_flow
            # save frame
            pic_name = pn + '_' + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '_' + str(
                ok_ng) + '.jpg'
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(os.path.join(save_path, pic_name), frame)

            # save all result in one .md file
            with open(os.path.join(save_path, md_file_name), 'a') as f:
                f.write(f'## {pn} {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n')
                f.write(f'### {res_json}\n')
                f.write(f'### {ok_ng}\n')
                f.write(f'![{pic_name}](./{pic_name})\n\n')

        except Exception as e:
            print(f"Error saving results: {e}")
