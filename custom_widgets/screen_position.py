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
import logging
import threading
import math
# from hik_CAM_linux.getFrame import start_cam, exit_cam, get_frame

#save log to file
logging.basicConfig(level=logging.INFO, filename='user_data/log.log')
logger = logging.getLogger(__name__)

#TODO 
# 1. 替换为喷漆线已修改的.py


class Screen(ft.Container):
    def __init__(self, index: str):
        super().__init__()
        self.index = index
        self.expand = 1
        self.padding = ft.Padding(0, 0, 0, 0)
        self.cap = None
        self.flow_thread = None
        self.socket_connect_thread = None
        self.modbus_connect_thread = None
        self.status_output_thread = None
        self.is_running = False
        self.socket_connect_result = None
        self.modbus_connect_result = None
        self.pn_in_model_config = True
        self.gpio_dir={
            0:20,
            1:21,
            2:26
        }

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
        self.visual_result = ft.Image(src='/images/siri.gif',fit=ft.ImageFit.CONTAIN,expand=1)
        self.start_stop_btn = ft.IconButton(icon=ft.icons.PLAY_ARROW, on_click=self.on_start_stop_btn_click)
        self.progress_bar = ft.ProgressBar( height=3, visible=False,expand=1)

        flow_config = CONFIG_OBJ[self.current_flow]
        if flow_config['layer_config_use'] == 'True':
            self.objects_sequence=self._load_layer_config(flow_config)
            self.objects_quantity = len(self.objects_sequence)
            self.current_object_index = 0


        

        row1 = ft.Row([select_flow_label, flow_select, self.start_stop_btn])
        row2 = ft.Row([self.progress_bar])
        row4 = ft.Row([self.flow_result])
        row3 = ft.Row([self.visual_result],expand=1,alignment=ft.MainAxisAlignment.CENTER)
        card_content = ft.Container(ft.Column([row1, row2, row3, row4], spacing=10), padding=10)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(1,1,1,1),expand=1)

        self.content = ft.Column([card], alignment=ft.MainAxisAlignment.CENTER)
        # create bgcolor text
        self.objects_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER) 
        if flow_config['layer_config_use'] == 'True':
            for object in self.objects_sequence:
                self.objects_row.controls.append(ft.Text(object, size=14, bgcolor=ft.colors.BLUE_GREY_100))

        self.content.controls.append(self.objects_row)

    
    def flow_select_change(self, e: ft.ControlEvent):
        """流程选择改变事件"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Flow Select Change to [{e.control.value}]")
        flow = e.control.value
        self.flow_result.value = f"当前流程：{flow}"
        self.page.update()
        self.current_flow = flow

        flow_config = CONFIG_OBJ[self.current_flow]
        self.objects_row.controls = []

        if flow_config['layer_config_use'] == 'True':
            self.objects_sequence=self._load_layer_config(flow_config)
            self.objects_quantity = len(self.objects_sequence)
            self.current_object_index = 0
            for object in self.objects_sequence:
                self.objects_row.controls.append(ft.Text(object, size=14, bgcolor=ft.colors.BLUE_GREY_100))
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
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Stop Flow")
        self.start_stop_btn.icon = ft.icons.PLAY_ARROW
        self.progress_bar.visible = False
        # self.page.update()
        flow_config = CONFIG_OBJ[self.current_flow]
        if flow_config['layer_config_use'] == 'True':
            self.current_object_index=0
            self._reset_objects_row()
        self.is_running = False

        if self.cap:
            try:
                self.cap.release()
                self.cap = None
            except Exception as e:
                from hik_CAM_linux.getFrame import exit_cam
                exit_cam(self.cap, self.data_buf)
                self.cap = None



        if self.modbus_connect_result:
            self.client.close()
            self.modbus_connect_result = None


        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Current Thread: {threading.enumerate()}")

        try:
            if self.flow_thread:
                if self.flow_thread.is_alive():
                    self.flow_thread.join()
                    self.flow_thread = None
        except Exception as e:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Error killing thread: {e}")
        # 打印当前线程
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Current Thread: {threading.enumerate()}")

        self.visual_result.src_base64 = ''
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Stop Flow End")
        self.flow_result.value = f"当前流程：[{self.current_flow}] 已停止..."
        self.page.update()


    def start_flow(self, e: ft.ControlEvent):
        """开始流程"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Start Flow")
        self.start_stop_btn.icon = ft.icons.STOP
        self.progress_bar.visible = True
        self.page.update()
        
        self.is_running = True
        self.flow_thread = Thread(target=self.start_flow_thread, args=(e,))
        self.flow_thread.start()

    def start_flow_thread(self, e: ft.ControlEvent):
        """开始流程线程"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Start Flow Thread")
        flow_config = CONFIG_OBJ[self.current_flow]
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Flow Config: {flow_config}")
        if not self.check_config(flow_config):
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Config check failed")
            self.flow_thread=None
            self.stop_flow(e)
        if_use_status_output = flow_config['status_output']
        if if_use_status_output == 'True' and self.modbus_connect_result:
            self._start_status_output_thread(flow_config)

        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Start Flow Thread Loop")
        while self.is_running:
            need_check_modbus_connect = flow_config['trigger_type'] == '1' or flow_config['plc_output'] == 'True' or flow_config['status_output'] == 'True'
            if (not self.modbus_connect_result) and need_check_modbus_connect:
                self.flow_result.value = f"当前流程：[{self.current_flow}] Modbus TCP connect failed! try reconnect..."
                self.visual_result.src_base64 = ''
                self.page.update()
                continue
            need_check_socket_connect = flow_config['model_config_use'] == 'True' or flow_config['socket'] == 'True'
            if (not self.socket_connect_result) and need_check_socket_connect:
                self.flow_result.value = f"当前流程：[{self.current_flow}] Socket connection failed! try reconnect..."
                self.visual_result.src_base64 = ''
                self.page.update()
                continue

            if not self.pn_in_model_config:
                self.flow_result.value = f"当前流程：[{self.current_flow}] 料号不在模型配置中，请检查配置"
                self.visual_result.src_base64 = ''
                self.page.update()
                continue

            self.flow_result.value = f"当前流程：[{self.current_flow}] 工作中..."
            self.page.update()
            if flow_config['trigger_type'] == '0':
                #实时探测模式
                
                if flow_config['layer_config_use'] == 'True':
                    #分层识别模式
                    # print(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] objects_sequence: {objects_sequence}")
                    ret,frame=self._get_frame_from_cam(flow_config)
                    res=self._detect_object(frame,flow_config)
                    if res is None:
                        continue
                    ok_or_ng=self._logic_process(res,flow_config)
                    self._output_result(res,ok_or_ng,flow_config)
                else:   
                    ret,frame=self._get_frame_from_cam(flow_config)
                    res=self._detect_object(frame,flow_config)
                    if res is None:
                        continue
                    ok_or_ng=self._logic_process(res,flow_config)
                    self._output_result(res,ok_or_ng,flow_config)

            elif flow_config['trigger_type'] == '1':
                #触发器模式
                trigger=self._listen_trigger(flow_config)
                if trigger:
                    ret,frame=self._get_frame_from_cam(flow_config)
                    res=self._detect_object(frame,flow_config)
                    if res is None:
                        continue
                    ok_or_ng=self._logic_process(res,flow_config)
                    self._output_result(res,ok_or_ng,flow_config)

                else:
                    continue
            elif flow_config['trigger_type'] == '2':
                #定时探测模式
                ret,frame=self._get_frame_from_cam(flow_config)


                res=self._detect_object(frame,flow_config)
                if res is None:
                    continue
                ok_or_ng=self._logic_process(res,flow_config)
                self._output_result(res,ok_or_ng,flow_config)

                time.sleep(1)
                

    def check_config(self, flow_config):
        """检查配置"""
        self.flow_result.value = f"当前流程：{self.current_flow} 配置检查中..."
        self.page.update()
        # check camera
        cam_check_result = self._check_camera(flow_config)
        # check model
        model_check_result = self._check_model(flow_config)
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
            self.modbus_connect_thread = Thread(target=self._detect_plc_connect, args=(flow_config,))
            self.modbus_connect_thread.daemon = True
            self.modbus_connect_thread.start()
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
            self.socket_connect_thread = Thread(target=self._detect_socket_connect, args=(flow_config,))
            self.socket_connect_thread.daemon = True
            self.socket_connect_thread.start()
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
        self.flow_result.value += f"CAM:{'✅' if cam_check_result == True else '❌' if cam_check_result == False else '⚫'}   "
        self.flow_result.value += f"MODEL:{'✅' if model_check_result == True else '❌' if model_check_result == False else '⚫'}   "
        self.flow_result.value += f"PLC:{'✅' if plc_connect_check_result == True else '❌' if plc_connect_check_result == False else '⚫'}   "
        self.flow_result.value += f"GPIO:{'✅' if gpio_output_check_result == True else '❌' if gpio_output_check_result == False else '⚫'}   "
        self.flow_result.value += f"SOCKET:{'✅' if socket_check_result == True else '❌' if socket_check_result == False else '⚫'}   "
        self.flow_result.value += f"SAVE:{'✅' if save_result_check == True else '❌' if save_result_check == False else '⚫'}    "
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
            self.visual_result.src_base64 = ''
            self.page.update()
            return False

    def _check_camera(self, flow_config):
        """检查相机"""
        cam_type = flow_config['cam1_type']
        cam_idx = flow_config['cam1_idx']
        cam_size = flow_config['cam1_size']
        cam_use = flow_config['cam1_use']
        if cam_use:
            if cam_type == '0':
                try:
                    logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Check Camera : CV camera")
                    self.cap = cv2.VideoCapture(int(cam_idx))
                    #  取10帧   
                    for _ in range(10):
                        ret,frame=self.cap.read()
                        # print(frame.shape)
                    return True
                except Exception as e:
                    logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Error initializing camera: {e}")
                    return False
            elif cam_type == '1':
                try:
                    logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Check Camera : HIK camera")
                    from hik_CAM_linux.getFrame import start_cam, exit_cam, get_frame
                    self.cap, self.stOutFrame, self.data_buf = start_cam(nConnectionNum=int(cam_idx))
                   #  取10帧   
                    for _ in range(5):
                        ret,frame=get_frame(self.cap, self.stOutFrame)
                    self.cap.MV_CC_StopGrabbing()
                        # print(frame.shape)
                    return True
                except Exception as e:
                    logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Error initializing camera: {e}")
                    return False
            else:
                return False
        else:
            return True
        
    def _check_model(self, flow_config):
        """检查模型"""
        model_path = flow_config['model1_path']
        model_confidence = flow_config['model1_confidence']
        model_iou = flow_config['model1_iou']
        model_use = flow_config['model1_use']
        flow_config = CONFIG_OBJ[self.current_flow]

        if_use_model_config = flow_config['model_config_use']
        

        if if_use_model_config == 'True':
            return True
        elif flow_config['layer_config_use'] == 'True':
            model_path,conf_thres,iou_thres,img_size= self._load_layer_model_config(flow_config)
            self.model=YOLO(model_path)
        else:
            if model_use:
                try:
                    self.model = YOLO(model_path)
                    return True
                except Exception as e:
                    logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Error initializing model: {e}")
                    return False
            else:
                return True
        
    def _check_plc_connect(self, plc_ip: str, plc_port: int):
        """检查PLC连接"""
        try:
            from pymodbus.client import ModbusTcpClient
            self.client = ModbusTcpClient(plc_ip, port=plc_port, slave=1)
            self.modbus_connect_result = self.client.connect()

            if self.modbus_connect_result:
                logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC initialized, IP: {plc_ip}, port : {plc_port}, status : {self.modbus_connect_result}")
            else:
                logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC connection failed, IP: {plc_ip}, port : {plc_port}, status : {self.modbus_connect_result}")

            return self.modbus_connect_result
        except Exception as e:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Error initializing PLC: {e}")
            self.modbus_connect_result = False
            return self.modbus_connect_result
    def _detect_plc_connect(self, flow_config):
        """检测PLC连接"""
        plc_ip = flow_config['plc_ip']
        plc_port = int(flow_config['plc_port'])
        while True:
            self.modbus_connect_result = self.client.connect()
            if not self.modbus_connect_result:
                logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC connection failed, IP: {plc_ip}, port : {plc_port}, status : {self.modbus_connect_result}")
            time.sleep(3)
    def _detect_socket_connect(self, flow_config):
        """检测socket连接"""
        socket_ip = flow_config['socket_ip']
        socket_port = int(flow_config['socket_port'])
        while True:
            self._check_socket(socket_ip, socket_port)
            time.sleep(3)

    def _check_gpio_output(self, gpio_output_point):
        """检查GPIO输出"""
        gpio_output_point = self.gpio_dir[int(gpio_output_point) ]
        try:    
            import Jetson.GPIO as GPIO
            self.GPIO=GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setwarnings(False)
            self.GPIO.setup(gpio_output_point, self.GPIO.OUT, initial=self.GPIO.LOW)
            return True
        except Exception as e:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] GPIO error: {e}")
            return False

    def _check_socket(self, socket_ip: str, socket_port: int):
        """检查socket连接"""
        try:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.settimeout(1)
            self.socket_client.connect((socket_ip, socket_port))
            result = True
        except Exception as e:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Error initializing socket: {e}")
            result = False
        finally:
            self.socket_client.close()
        self.socket_connect_result = result
        return self.socket_connect_result

    def _listen_trigger(self, flow_config):
        """监听触发器"""
        address = int(flow_config['plc_trigger_address'])
        count = int(flow_config['plc_trigger_count'])
        slave=1
        self.modbus_connect_result=self.client.connect()
        if  self.modbus_connect_result:
            pass
            # logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC connection success")
        else:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC connection failed")
            return False

        try:
            result = self.client.read_holding_registers(address, count,slave=1)
        except Exception as e:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC read failed: {e}")
            return False
        type=flow_config['signal_type']
        # 当type为0时，监听result的上升延信号
        if type == '0':
            # 记录上一次的值
            if not hasattr(self, 'last_trigger_value'):
                self.last_trigger_value = 0
            
            # 获取当前值
            try:
                current_value = result.registers[0] if result and result.registers else 0
            except Exception as e:
                logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC read failed: {e}")
                return False
            
            # 检测上升沿 - 从0变为1
            if current_value == 1 and self.last_trigger_value == 0:
                self.last_trigger_value = current_value
                logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Detector Trigger :上升沿")
                return True
            
            # 更新上一次的值
            self.last_trigger_value = current_value
            return False
        else:
            # 记录上一次的值
            if not hasattr(self, 'last_trigger_value'):
                self.last_trigger_value = 1
            
            # 获取当前值
            try:
                current_value = result.registers[0] if result and result.registers else 1   
            except Exception as e:
                logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC read failed: {e}")
                return False
            
            # 检测下降沿 - 从1变为0
            if current_value == 0 and self.last_trigger_value == 1:
                self.last_trigger_value = current_value
                logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Detector Trigger :下降沿")
                return True
            
            # 更新上一次的值
            self.last_trigger_value = current_value
            return False    
        

    def _start_status_output_thread(self, flow_config):
        """启动状态输出线程"""
        self.status_output_thread = Thread(target=self._status_output_thread, args=(flow_config,))
        self.status_output_thread.daemon = True
        self.status_output_thread.start()

    def _status_output_thread(self, flow_config):
        """状态输出线程"""
        status_output_address = int(flow_config['status_output_address'])
        status_output_value = int(flow_config['status_output_value'])
        while self.is_running :
            if not self.modbus_connect_result:
                time.sleep(3)
                continue
            self.client.write_register(status_output_address, status_output_value)
            logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Status_out_put :address {status_output_address} value {status_output_value}")
            time.sleep(3)
        self.status_output_thread = None

    def _get_frame_from_cam(self, flow_config):
        """获取相机帧"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Get Frame from CAM...")
        if flow_config['cam1_type'] == "0":
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 重置指针（部分摄像头有效）
            for _ in range(int(self.cap.get(cv2.CAP_PROP_BUFFERSIZE))):  # 清空缓冲区
                self.cap.grab()  # 快速丢弃旧帧（不解码）
            ret, frame = self.cap.read()  # 读取最新帧

        elif flow_config['cam1_type'] == "1":
            from hik_CAM_linux.getFrame import start_cam, exit_cam, get_frame
            self.cap.MV_CC_StartGrabbing()
            ret, frame = get_frame(self.cap, self.stOutFrame)
            self.cap.MV_CC_StopGrabbing()

        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except cv2.error as e:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] OpenCV error: {e}")
        return ret, frame

    def _detect_object(self, frame, flow_config):
        """检测物体"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Detect Object...")
        if_model_config_use = flow_config['model_config_use']
        if_layer_config_use = flow_config['layer_config_use']
        if if_model_config_use == 'True':
            model_path,conf_thres,iou_thres,img_size= self._load_model_config(flow_config)
            if model_path is None:
                return None
            self.model = YOLO(model_path)
            results = self.model(frame, conf=conf_thres, iou=iou_thres, imgsz=img_size)
        elif if_layer_config_use == 'True':
            model_path,conf_thres,iou_thres,img_size= self._load_layer_model_config(flow_config)
            if model_path is None:
                return None
            classes = self.model.names
            class_values = list(classes.values())
            class_name=self.objects_sequence[self.current_object_index]
            class_index=class_values.index(class_name)
            results = self.model(frame, conf=conf_thres, iou=iou_thres, imgsz=img_size,classes=[class_index])
        else:
            conf_thres = float(flow_config['model1_confidence'])
            iou_thres = float(flow_config['model1_iou'])
            img_size = int(flow_config['cam1_size'])
            results = self.model(frame, conf=conf_thres, iou=iou_thres, imgsz=img_size)
        return results

    def _load_model_config(self, flow_config):
        """加载模型配置"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Load Model Config...")
        model_config_file_path = flow_config['model_config_file_path']
        model_config_file = pd.read_csv(model_config_file_path,header=0,index_col=0,encoding='utf-8')
        socket_ip = flow_config['socket_ip']
        socket_port = int(flow_config['socket_port'])
        try:
            logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Connect to Socket TCP...")
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_client.settimeout(1)
            self.socket_client.connect((socket_ip, socket_port))
            self.socket_client.sendall(b'LON\r')
            response = self.socket_client.recv(1024)
            if response:
                logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Received response: {response.decode('utf-8')}")
                self.socket_data=response.decode('utf-8').strip()
            else:
                logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] No socket data received.")
        except Exception as e:
            self.flow_result.value = f"当前流程：[{self.current_flow}] Socket TCP connect failed!"
            self.visual_result.src_base64 = ''
            self.page.update()
            self.socket_connect_result = False
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Socket TCP connect failed Error: {e}")
        finally:
            self.socket_client.close()
        data_PN=int(self.socket_data[-10:])
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] data: {self.socket_data}    data_PN: {data_PN}")
        if data_PN not in model_config_file.index:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] data_PN: {data_PN} not in model_config_file")
            self.pn_in_model_config = False
            self.reset_pn_in_model_config_thread = Thread(target=self._reset_pn_in_model_config, args=(flow_config,))
            self.reset_pn_in_model_config_thread.start()
            return None,None,None,None
        model_path=model_config_file.loc[data_PN]['model']
        conf=float(model_config_file.loc[data_PN]['conf'])
        iou=float(model_config_file.loc[data_PN]['iou'])
        img_size=int(model_config_file.loc[data_PN]['imgsz'])
        self.selected_objects=model_config_file.loc[data_PN]['select_objects'].split(',')[0:-1]

        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}]--- model_path: {model_path}")
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}]--- conf: {conf}")
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}]--- iou: {iou}")
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}]--- img_size: {img_size}")
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}]--- selected_objects: {self.selected_objects}")
        return model_path,conf,iou,img_size
    def _load_layer_model_config(self, flow_config):
        """加载分层识别配置"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Load layer config...")
        layer_config_file_path = flow_config['layer_config_file_path']
        layer_config_file = pd.read_csv(layer_config_file_path, header=0, index_col=0, encoding='utf-8')
        layer_PN=self.current_flow
        if layer_PN not in layer_config_file.index:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] layer_PN: {layer_PN} not in layer_config_file")
            return None,None,None,None
        model_path=layer_config_file.loc[layer_PN]['model']
        conf=float(layer_config_file.loc[layer_PN]['conf'])
        iou=float(layer_config_file.loc[layer_PN]['iou'])
        img_size=int(layer_config_file.loc[layer_PN]['imgsz'])
        return model_path,conf,iou,img_size
    def _reset_pn_in_model_config(self, flow_config):
        """重置PN在模型配置中"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Reset PN in model config...")
        time.sleep(3)
        self.pn_in_model_config = True
        self.reset_pn_in_model_config_thread = None
        
    def _logic_process(self, result, flow_config):
        """逻辑处理"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Logic process...")
        res_json_load = json.loads(result[0].tojson())
        detected_objects = [r['name'] for r in res_json_load]   
        if_model_config_use = flow_config['model_config_use']
        if_layer_config_use = flow_config['layer_config_use']
        if if_model_config_use == 'True':
            self.selected_objects = self.selected_objects
        else:
            self.selected_objects = flow_config['model1_selected_objects'].split(',')[0:-1]
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Detected_objects: {detected_objects}")
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Selected_objects: {self.selected_objects}")
        logic_type = flow_config['logic_type']
        if logic_type == '0':  # detected objects [in] selected_objects
            if if_layer_config_use == 'True':
                logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Select_objects: {self.objects_sequence[self.current_object_index]}")
                check_result = all(item in self.objects_sequence[self.current_object_index] for item in detected_objects) and len(detected_objects) > 0


            else:
                check_result = all(item in self.selected_objects for item in detected_objects) and len(detected_objects) > 0
            

        elif logic_type == '1':  # selected_objects [in] detected objects
            check_result = all(item in detected_objects for item in self.selected_objects) and len(detected_objects) > 0
        elif logic_type == '2':  # selected_objects [=] detected objects
            check_result = len(detected_objects) == len(self.selected_objects) and all(item in detected_objects for item in self.selected_objects)
        elif logic_type == '3':  # detected objects [in] target position (position model)
            logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Res json: {res_json_load}")
            boxes=[r['box'] for r in res_json_load if r['name'] in self.selected_objects]   
            x1=[r['x1'] for r in boxes]   
            x2=[r['x2'] for r in boxes]   
            y1=[r['y1'] for r in boxes]   
            y2=[r['y2'] for r in boxes] 
            # Find all center points of the boxes
            center_points = [(int((x1[i] + x2[i]) / 2), int((y1[i] + y2[i]) / 2)) for i in range(len(x1))]
            # Find the center point of the target position
            point_use = []
            point_use.append(flow_config['position_1_use'])
            point_use.append(flow_config['position_2_use'])
            point_use.append(flow_config['position_3_use'])
            point_use.append(flow_config['position_4_use'])
            point_use.append(flow_config['position_5_use'])
            point_use.append(flow_config['position_6_use'])
            target_center_point = []
            target_center_point.append((int(flow_config['position_1_center_x']), int(flow_config['position_1_center_y'])))
            target_center_point.append((int(flow_config['position_2_center_x']), int(flow_config['position_2_center_y'])))
            target_center_point.append((int(flow_config['position_3_center_x']), int(flow_config['position_3_center_y'])))
            target_center_point.append((int(flow_config['position_4_center_x']), int(flow_config['position_4_center_y'])))
            target_center_point.append((int(flow_config['position_5_center_x']), int(flow_config['position_5_center_y'])))
            target_center_point.append((int(flow_config['position_6_center_x']), int(flow_config['position_6_center_y'])))
            target_radius = []
            target_radius.append(int(flow_config['position_1_radius']))
            target_radius.append(int(flow_config['position_2_radius']))
            target_radius.append(int(flow_config['position_3_radius']))
            target_radius.append(int(flow_config['position_4_radius']))
            target_radius.append(int(flow_config['position_5_radius']))
            target_radius.append(int(flow_config['position_6_radius']))
            # Calculate the distance between the center points
            self.target_check_exist = []                
            for i in range(len(point_use)):
                if point_use[i]=='True':
                    if len(center_points) == 0:
                        point_i_exist=False
                        self.target_check_exist.append(point_i_exist)
                    else:
                        for j in range(len(center_points)):
                            distance = math.sqrt((center_points[j][0] - target_center_point[i][0]) ** 2 + (center_points[j][1] - target_center_point[i][1]) ** 2)
                            if distance <= target_radius[i]:
                                point_i_exist=True
                                break
                            else:
                                point_i_exist=False
                        self.target_check_exist.append(point_i_exist)
                else:
                    self.target_check_exist.append('n/a')
            logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Target check exist: {self.target_check_exist}")
            check_result = True
        else:
            check_result = False
        return check_result
    def _reset_objects_row(self):
        self.objects_row.controls=[]
        for object in self.objects_sequence:
            self.objects_row.controls.append(ft.Text(object, size=14, bgcolor=ft.colors.BLUE_GREY_100))
        self.page.update()

    def _output_result(self,res, ok_ng: bool, flow_config):
        """输出结果"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Output result...")
        if_gpio_output = flow_config['gpio']
        if_visual_output = flow_config['visual']
        if_plc_output = flow_config['plc_output']
        if_save_output = flow_config['result_save']
        if_layer_config_use = flow_config['layer_config_use']

        if if_layer_config_use =='True':
            if ok_ng:
                if self.current_object_index < len(self.objects_sequence)-1:
                    self.objects_row.controls[self.current_object_index].bgcolor = ft.colors.GREEN
                    self.page.update()
                    self.current_object_index +=1
                else:
                    self.objects_row.controls[self.current_object_index].bgcolor = ft.colors.GREEN
                    self.page.update()
                    self.current_object_index=0
                    time.sleep(3)
                    self._reset_objects_row()
            else:
                pass

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
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] GPIO output...")
        gpio_output_point = self.gpio_dir[int(flow_config['gpio_output_point'])]
        if ok_ng:
            self.GPIO.output(gpio_output_point, self.GPIO.HIGH)
        else:
            self.GPIO.output(gpio_output_point, self.GPIO.LOW)

    def _visual_output(self, res, ok_ng: bool, flow_config):
        """视觉输出"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Visual output...")
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
            
        # add target check exist text
        if_position_config_use = flow_config['position_config_use']
        if if_position_config_use == 'True':
            # 绘制目标位置的圆，并根据结果True/False/n/a绘制不同的颜色
            for i in range(len(self.target_check_exist)):

                circle_center_x_name = 'position_' + str(i+1) + '_center_x'
                circle_center_y_name = 'position_' + str(i+1) + '_center_y'
                circle_radius_name = 'position_' + str(i+1) + '_radius'
                if self.target_check_exist[i] == True:
                    res_plotted = cv2.circle(res_plotted, (int(flow_config[circle_center_x_name]), int(flow_config[circle_center_y_name])), int(flow_config[circle_radius_name]), (0, 255, 0), 2)
                elif self.target_check_exist[i] == False:
                    res_plotted = cv2.circle(res_plotted, (int(flow_config[circle_center_x_name]), int(flow_config[circle_center_y_name])), int(flow_config[circle_radius_name]), (0, 0, 255), 2)
                else:
                    res_plotted = cv2.circle(res_plotted, (int(flow_config[circle_center_x_name]), int(flow_config[circle_center_y_name])), int(flow_config[circle_radius_name]), (0, 0, 0), 2)

        img_pil = Image.fromarray(res_plotted)
        img_byte_arr = BytesIO()
        img_pil.save(img_byte_arr, format="JPEG")
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        self.visual_result.src_base64 = img_base64
        self.page.update()

    def _plc_output(self, ok_ng: bool, flow_config):
        """PLC输出"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] PLC output...")
        if_position_config_use = flow_config['position_config_use']
        if if_position_config_use == 'True':
            for i in range(len(self.target_check_exist)):
                plc_address = int(flow_config['position_' + str(i+1) + '_output_address'])
                if self.target_check_exist[i] == True:
                    self.client.write_register(plc_address,1)
                else:
                    self.client.write_register(plc_address,0)
        else:
            plc_address = int(flow_config['plc_output_address'])
            plc_value = int(flow_config['plc_output_value'])
            if ok_ng:
                self.client.write_register(plc_address, plc_value)
            else:
                self.client.write_register(plc_address,0)

    def _save_output(self, res, ok_ng: bool, flow_config):
        """保存输出"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Save output...")
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
            logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Save output: {pic_name}")

            # save all result in one .md file
            with open(os.path.join(save_path, md_file_name), 'a') as f:
                f.write(f'## {pn} {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n')
                f.write(f'### {res_json}\n')
                f.write(f'### {ok_ng}\n')
                f.write(f'![{pic_name}](./{pic_name})\n\n')
            logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Save output: {md_file_name}")



        except Exception as e:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>Error saving results: {e}")


    def _load_layer_config(self, flow_config):
        """加载分层识别配置"""
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] Load layer config...")
        layer_config_file_path = flow_config['layer_config_file_path']
        layer_config_file = pd.read_csv(layer_config_file_path, header=0, index_col=0, encoding='utf-8')
        layer_PN=self.current_flow
        logger.info(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] layer_PN: {layer_PN}")
        if layer_PN not in layer_config_file.index:
            logger.error(f"time: {time.strftime('%Y-%m-%d %H:%M:%S')}===>[{self.current_flow}] layer_PN: {layer_PN} not in layer_config_file")
            return None
        objects_sequence=layer_config_file.loc[layer_PN]['objects_sequence'].split(',')[0:-1]
        return objects_sequence
