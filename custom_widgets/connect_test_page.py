import flet as ft
import time
from threading import Thread
import socket
from pymodbus.client import ModbusTcpClient



class ConnectTestPage(ft.Tab):
    def __init__(self):
        """连接测试页面"""
        super().__init__()
        self.text = 'Connect test'
        self.icon = ft.icons.FUNCTIONS

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        connect_test_label = ft.Text('Modbus Connect test', size=12)
        modbus_connect_ip_label = ft.Text('Modbus Connect IP', size=12)
        modbus_connect_port_label = ft.Text('Modbus Connect Port', size=12)
        self.modbus_connect_ip_input = ft.TextField(value='192.168.1.1',text_size=12)
        self.modbus_connect_port_input = ft.TextField(value='502',text_size=12)
        row1 = ft.Row([modbus_connect_ip_label, ft.Row(expand=1), self.modbus_connect_ip_input ])
        row2 = ft.Row([modbus_connect_port_label, ft.Row(expand=1), self.modbus_connect_port_input ])
        status_show = ft.Container()
        label = ft.Text('', size=12, width=100)
        label2 = ft.Text('', size=12, width=100, color=ft.colors.GREY)
        column = ft.Column([label, label2], spacing=0)
        self.modbus_connect_test_btn = ft.ElevatedButton('modbus connect test', on_click=self.modbus_connect_test_btn_clicked)
        self.modbus_connect_test_row3 = ft.Row([ft.Row(expand=1),status_show, column, self.modbus_connect_test_btn])
        card_content = ft.Container(ft.Column([row1, row2, self.modbus_connect_test_row3], spacing=20), padding=20)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))
        column = ft.Column([connect_test_label,card], width=720, spacing=12)
        modbus_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))


        modbus_read_label = ft.Text('Modbus Read test', size=12)
        modbus_read_address_label = ft.Text('Modbus Address', size=12)
        self.modbus_read_address_input = ft.TextField(value='0',text_size=12)
        modbus_read_address_row = ft.Row([modbus_read_address_label, ft.Row(expand=1), self.modbus_read_address_input ])
        modbus_read_count_label = ft.Text('Modbus Count', size=12)
        self.modbus_read_count_input = ft.TextField(value='1',text_size=12)
        modbus_read_count_row = ft.Row([modbus_read_count_label, ft.Row(expand=1), self.modbus_read_count_input ])
        modbus_read_slave_label = ft.Text('Modbus Slave', size=12)
        self.modbus_read_slave_input = ft.TextField(value='1',text_size=12)
        modbus_read_slave_row = ft.Row([modbus_read_slave_label, ft.Row(expand=1), self.modbus_read_slave_input ])
        status_show = ft.Container()
        label = ft.Text('', size=12, width=100)
        label2 = ft.Text('', size=12, width=100, color=ft.colors.GREY)
        column = ft.Column([label, label2], spacing=0)
        self.modbus_read_test_btn = ft.ElevatedButton('modbus read test', on_click=self.modbus_read_test_btn_clicked)
        self.modbus_read_test_row3 = ft.Row([ft.Row(expand=1),status_show, column, self.modbus_read_test_btn])
        card_content = ft.Container(ft.Column([modbus_read_address_row, modbus_read_count_row, modbus_read_slave_row, self.modbus_read_test_row3], spacing=20), padding=20)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))
        column = ft.Column([modbus_read_label,card], width=720, spacing=12)
        modbus_read_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))


        modbus_write_label = ft.Text('Modbus Write test', size=12)
        modbus_write_address_label = ft.Text('Modbus Address', size=12)
        self.modbus_write_address_input = ft.TextField(value='0',text_size=12)
        modbus_write_address_row = ft.Row([modbus_write_address_label, ft.Row(expand=1), self.modbus_write_address_input ])
        modbus_write_value_label = ft.Text('Modbus Value', size=12)
        self.modbus_write_value_input = ft.TextField(value='1',text_size=12)
        modbus_write_value_row = ft.Row([modbus_write_value_label, ft.Row(expand=1), self.modbus_write_value_input ])
        status_show = ft.Container()
        label = ft.Text('', size=12, width=100)
        label2 = ft.Text('', size=12, width=100, color=ft.colors.GREY)
        column = ft.Column([label, label2], spacing=0)
        self.modbus_write_test_btn = ft.ElevatedButton('modbus write test', on_click=self.modbus_write_test_btn_clicked)
        self.modbus_write_test_row3 = ft.Row([ft.Row(expand=1),status_show, column, self.modbus_write_test_btn])
        card_content = ft.Container(ft.Column([modbus_write_address_row, modbus_write_value_row, self.modbus_write_test_row3], spacing=20), padding=20)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))
        column = ft.Column([modbus_write_label,card], width=720, spacing=12)
        modbus_write_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))


        socket_connect_label = ft.Text('Socket Connect test', size=12)
        socket_connect_ip_label = ft.Text('Socket Connect IP', size=12)
        socket_connect_port_label = ft.Text('Socket Connect Port', size=12)
        socket_connect_buffersize_label = ft.Text('Socket Connect Buffer Size', size=12)
        self.socket_connect_ip_input = ft.TextField(value='127.0.0.1',text_size=12)
        self.socket_connect_port_input = ft.TextField(value='9005',text_size=12)
        self.socket_connect_buffersize_input = ft.TextField(value='1024',text_size=12)
        row1 = ft.Row([socket_connect_ip_label, ft.Row(expand=1), self.socket_connect_ip_input ])
        row2 = ft.Row([socket_connect_port_label, ft.Row(expand=1), self.socket_connect_port_input ])
        row3 = ft.Row([socket_connect_buffersize_label, ft.Row(expand=1), self.socket_connect_buffersize_input ])
        status_show = ft.Container()
        label = ft.Text('', size=12, width=100)
        label2 = ft.Text('', size=12, width=100, color=ft.colors.GREY)
        column = ft.Column([label, label2], spacing=0)
        self.socket_connect_test_btn = ft.ElevatedButton('socket connect test', on_click=self.socket_connect_test_btn_clicked)
        self.socket_connect_test_row3 = ft.Row([ft.Row(expand=1),status_show, column, self.socket_connect_test_btn])
        card_content = ft.Container(ft.Column([row1, row2, row3, self.socket_connect_test_row3], spacing=20), padding=20) 
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))
        column = ft.Column([socket_connect_label,card], width=720, spacing=12)
        socket_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))



        socket_command_label = ft.Text('Socket Command test', size=12)
        socket_command_address_label = ft.Text('Socket Command ', size=12)
        self.socket_command_address_input = ft.TextField(value='READ',text_size=12)
        socket_command_address_row = ft.Row([socket_command_address_label, ft.Row(expand=1), self.socket_command_address_input ])
        status_show = ft.Container()
        label = ft.Text('', size=12, width=100)
        label2 = ft.Text('', size=12, width=100, color=ft.colors.GREY)
        column = ft.Column([label, label2], spacing=0)
        self.socket_command_test_btn = ft.ElevatedButton('socket command test', on_click=self.socket_command_test_btn_clicked)
        self.socket_command_test_row3 = ft.Row([ft.Row(expand=1),status_show, column, self.socket_command_test_btn])
        card_content = ft.Container(ft.Column([socket_command_address_row, self.socket_command_test_row3], spacing=20), padding=20)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))
        column = ft.Column([socket_command_label,card], width=720, spacing=12)
        socket_command_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))





        self.content = ft.Column([modbus_container, modbus_read_container, modbus_write_container, socket_container, socket_command_container], scroll=ft.ScrollMode.AUTO)    


    def modbus_connect_test_btn_clicked(self, e: ft.ControlEvent):
        """PLC连接按钮被点击的事件"""
        print("===>modbus_connect_test_event")
        Thread(target=self.modbus_connect_test_event, daemon=True).start()


    def modbus_connect_test_event(self):
        """开启额外线程检查更新"""
        self.modbus_connect_test_row3.controls[1] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.modbus_connect_test_row3.controls[2].controls[0].value = '正在检查PLC连接'
        self.modbus_connect_test_btn.disabled = True
        self.modbus_connect_test_row3.update()
        try:
            client = ModbusTcpClient(self.modbus_connect_ip_input.value, port=int(self.modbus_connect_port_input.value), slave=1)
            result = client.connect()
            print(f"PLC连接检查结果: {result}")
            if result:
                self.modbus_connect_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                self.modbus_connect_test_row3.controls[2].controls[0].value = 'PLC连接检查成功'
                self.modbus_connect_test_row3.controls[2].controls[1].value = f'IP:{self.modbus_connect_ip_input.value}, Port:{self.modbus_connect_port_input.value}'
                self.modbus_connect_test_btn.disabled = False
                self.modbus_connect_test_row3.update()
            else:
                self.modbus_connect_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                self.modbus_connect_test_row3.controls[2].controls[0].value = 'PLC连接检查失败'
                self.modbus_connect_test_row3.controls[2].controls[1].value = f'IP:{self.modbus_connect_ip_input.value}, Port:{self.modbus_connect_port_input.value}'
                self.modbus_connect_test_btn.disabled = False
                self.modbus_connect_test_row3.update()
        except Exception as e:
            self.modbus_connect_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
            self.modbus_connect_test_row3.controls[2].controls[0].value = 'PLC连接检查失败'
            self.modbus_connect_test_row3.controls[2].controls[1].value = f'Error:{e}'
            self.modbus_connect_test_btn.disabled = False
            self.modbus_connect_test_row3.update()
        finally:    
            client.close()


    def socket_connect_test_btn_clicked(self, e: ft.ControlEvent):
        """socket连接按钮被点击的事件"""
        print("===>socket_connect_test_event")
        Thread(target=self.socket_connect_test_event, daemon=True).start()


    def socket_connect_test_event(self):
        """开启额外线程检查更新"""
        self.socket_connect_test_row3.controls[1] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.socket_connect_test_row3.controls[2].controls[0].value = '正在检查socket连接'
        self.socket_connect_test_btn.disabled = True
        self.socket_connect_test_row3.update()
        try:
            # 创建socket对象
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.settimeout(1)
            print(f"Connecting to {self.socket_connect_ip_input.value}:{self.socket_connect_port_input.value}...")
            ip = self.socket_connect_ip_input.value
            port = int(self.socket_connect_port_input.value)
            # 连接到设备
            connect_result = tcp_socket.connect((ip, port))
            print(f"Connected successfully! {connect_result}")
            self.socket_connect_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
            self.socket_connect_test_row3.controls[2].controls[0].value = 'socket连接检查成功'
            self.socket_connect_test_row3.controls[2].controls[1].value = f'IP:{self.socket_connect_ip_input.value}, Port:{self.socket_connect_port_input.value}'
            self.socket_connect_test_btn.disabled = False
            self.socket_connect_test_row3.update()
        except socket.error as e:
            self.socket_connect_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
            self.socket_connect_test_row3.controls[2].controls[0].value = 'socket连接检查失败'
            self.socket_connect_test_row3.controls[2].controls[1].value = f'Error:{e}'
            self.socket_connect_test_btn.disabled = False
            self.socket_connect_test_row3.update()
        finally:
            tcp_socket.close()


    def modbus_read_test_btn_clicked(self, e: ft.ControlEvent):
        """modbus读取按钮被点击的事件"""
        print("===>modbus_read_test_event")
        Thread(target=self.modbus_read_test_event, daemon=True).start()

    def modbus_read_test_event(self):
        """开启额外线程检查更新"""
        self.modbus_read_test_row3.controls[1] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.modbus_read_test_row3.controls[2].controls[0].value = '正在检查modbus读取'
        self.modbus_read_test_btn.disabled = True
        self.modbus_read_test_row3.update()
        try:
            client = ModbusTcpClient(self.modbus_connect_ip_input.value, port=int(self.modbus_connect_port_input.value), slave=1)
            result = client.connect()
            if result:
                address = int(self.modbus_read_address_input.value)
                count = int(self.modbus_read_count_input.value)
                slave = int(self.modbus_read_slave_input.value)
                read_result = client.read_holding_registers(address, count, slave)
                if read_result:
                    self.modbus_read_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                    self.modbus_read_test_row3.controls[2].controls[0].value = 'modbus读取检查成功'
                    self.modbus_read_test_row3.controls[2].controls[1].value = f'Read Result:{read_result.registers}'
                    self.modbus_read_test_btn.disabled = False
                    self.modbus_read_test_row3.update()
                else:
                    self.modbus_read_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                    self.modbus_read_test_row3.controls[2].controls[0].value = 'modbus读取检查失败'
                    self.modbus_read_test_row3.controls[2].controls[1].value = f'Read Result:{read_result.registers}'
                    self.modbus_read_test_btn.disabled = False
                    self.modbus_read_test_row3.update()
            else:
                self.modbus_read_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                self.modbus_read_test_row3.controls[2].controls[0].value = 'modbus读取检查失败'
                self.modbus_read_test_row3.controls[2].controls[1].value = f'IP:{self.modbus_connect_ip_input.value}, Port:{self.modbus_connect_port_input.value}'
                self.modbus_read_test_btn.disabled = False
                self.modbus_read_test_row3.update()
        except Exception as e:
                self.modbus_read_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                self.modbus_read_test_row3.controls[2].controls[0].value = 'modbus读取检查失败'
                self.modbus_read_test_row3.controls[2].controls[1].value = f'Error:{e}'
                self.modbus_read_test_btn.disabled = False
                self.modbus_read_test_row3.update()
        finally:
            client.close()  
        
    def modbus_write_test_btn_clicked(self, e: ft.ControlEvent):
        """modbus写入按钮被点击的事件"""
        print("===>modbus_write_test_event")
        Thread(target=self.modbus_write_test_event, daemon=True).start()

    def modbus_write_test_event(self):
        """开启额外线程检查更新"""
        self.modbus_write_test_row3.controls[1] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.modbus_write_test_row3.controls[2].controls[0].value = '正在检查modbus写入'
        self.modbus_write_test_btn.disabled = True
        self.modbus_write_test_row3.update()
        try:
            client = ModbusTcpClient(self.modbus_connect_ip_input.value, port=int(self.modbus_connect_port_input.value), slave=1)
            result = client.connect()
            if result:
                address = int(self.modbus_write_address_input.value)
                value = int(self.modbus_write_value_input.value)
                write_result = client.write_registers(address, value)
                if write_result:
                    self.modbus_write_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                    self.modbus_write_test_row3.controls[2].controls[0].value = 'modbus写入检查成功'
                    self.modbus_write_test_row3.controls[2].controls[1].value = f'Address:{self.modbus_write_address_input.value}, Value:{self.modbus_write_value_input.value}'
                    self.modbus_write_test_btn.disabled = False
                    self.modbus_write_test_row3.update()
                else:
                    self.modbus_write_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                    self.modbus_write_test_row3.controls[2].controls[0].value = 'modbus写入检查失败'
                    self.modbus_write_test_row3.controls[2].controls[1].value = f'Address:{self.modbus_write_address_input.value}, Value:{self.modbus_write_value_input.value}'
                    self.modbus_write_test_btn.disabled = False
                    self.modbus_write_test_row3.update()    
            else:
                self.modbus_write_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                self.modbus_write_test_row3.controls[2].controls[0].value = 'modbus写入检查失败'
                self.modbus_write_test_row3.controls[2].controls[1].value = f'IP:{self.modbus_connect_ip_input.value}, Port:{self.modbus_connect_port_input.value}'
                self.modbus_write_test_btn.disabled = False
                self.modbus_write_test_row3.update()
        except Exception as e:
                self.modbus_write_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                self.modbus_write_test_row3.controls[2].controls[0].value = 'modbus写入检查失败'
                self.modbus_write_test_row3.controls[2].controls[1].value = f'Error:{e}'
                self.modbus_write_test_btn.disabled = False
                self.modbus_write_test_row3.update()
        finally:
            client.close()  

    def socket_command_test_btn_clicked(self, e: ft.ControlEvent):
        """socket命令按钮被点击的事件"""
        print("===>socket_command_test_event")
        Thread(target=self.socket_command_test_event, daemon=True).start()

    def socket_command_test_event(self):
        """开启额外线程检查更新"""
        self.socket_command_test_row3.controls[1] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.socket_command_test_row3.controls[2].controls[0].value = '正在检查socket命令'
        self.socket_command_test_btn.disabled = True
        self.socket_command_test_row3.update()
        try:
            # 创建socket对象
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.settimeout(1)
            print(f"Connecting to {self.socket_connect_ip_input.value}:{self.socket_connect_port_input.value}...")
            ip = self.socket_connect_ip_input.value
            port = int(self.socket_connect_port_input.value)
            # 连接到设备
            tcp_socket.connect((ip, port))
            print("Connected successfully!")

            # 发送命令
            command = self.socket_command_address_input.value
            tcp_socket.sendall(command.encode('utf-8'))
            print(f"Sent command: {command}")

            buffer_size = int(self.socket_connect_buffersize_input.value)   
            # 接收响应
            response = tcp_socket.recv(buffer_size)
            if response:
                print(f"Received response: {response.decode('utf-8')}")
                self.socket_command_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                self.socket_command_test_row3.controls[2].controls[0].value = 'socket命令检查成功'
                self.socket_command_test_row3.controls[2].controls[1].value = f'Response:{response.decode("utf-8")}'
                self.socket_command_test_btn.disabled = False
                self.socket_command_test_row3.update()      
            else:
                self.socket_command_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
                self.socket_command_test_row3.controls[2].controls[0].value = 'socket命令检查失败'
                self.socket_command_test_row3.controls[2].controls[1].value = f'Response:{response.decode("utf-8")}'
                self.socket_command_test_btn.disabled = False
                self.socket_command_test_row3.update()  
        except Exception as e:
            self.socket_command_test_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
            self.socket_command_test_row3.controls[2].controls[0].value = 'socket命令检查失败'
            self.socket_command_test_row3.controls[2].controls[1].value = f'Error:{e}'
            self.socket_command_test_btn.disabled = False
            self.socket_command_test_row3.update()
        finally:
            # 关闭连接
            tcp_socket.close()
