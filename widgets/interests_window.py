import flet as ft
from custom_widgets.image_viewer import ImageViewer
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
        self.tab1 = BaseTab1()
        self.tab2 = BaseTab2()
        self.tab3 = BaseTab3()
        self.tab4 = BaseTab4()
        self.tab5 = BaseTab5()


        tab_widget = ft.Tabs(tabs=[self.tab1, self.tab2, self.tab3, self.tab4, self.tab5], animation_duration=300,
                             selected_index=0, tab_alignment=ft.TabAlignment.START)
        self.content = tab_widget


class BaseTab1(ft.Tab):
    def __init__(self):
        """Function页面"""
        super().__init__()
        self.text = 'Function'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        # 项目选择
        project_label = ft.Text('Projects', size=15)
        tooltip = ft.Tooltip(message='Select the project to deploy')
        help_icon = ft.Icon('help', color=ft.colors.GREY, size=16, tooltip=tooltip)

        self.selected_project = CONFIG_OBJ['deploy_function']['project'] if CONFIG_OBJ.has_option('deploy_function', 'project') else Setting.project
        options=CONFIG_OBJ['deploy_function']['project_list']
        options=options.split(',')
        options=options[0:-1]
        options = [ft.dropdown.Option(i, i) for i in options]
        self.project_input = ft.Dropdown(options=options, dense=True, text_size=14, expand=1, value=self.selected_project, on_change=self.project_change_event)
        add_project_btn = ft.IconButton(icon=ft.icons.ADD, on_click=self.add_project_event)
        remove_project_btn = ft.IconButton(icon=ft.icons.DELETE, on_click=self.remove_project_event)
        row = ft.Row([ft.Text('Select the project (project)', size=14), help_icon, ft.Row(expand=1), self.project_input, add_project_btn, remove_project_btn])
        card_content = ft.Container(ft.Column([row], spacing=20), padding=20)
        project_card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))

        # 项目配置加载
        self.project_config_load()

        # 触发类型选择
        trigger_label = ft.Text('Trigger type', size=15)
        tooltip = ft.Tooltip(message='Select the trigger type')
        help_icon = ft.Icon('help', color=ft.colors.GREY, size=16, tooltip=tooltip)
        trigger_key = 'trigger_type'
        self.trigger_idx = CONFIG_OBJ[self.selected_project][trigger_key]
        self.trigger_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', 'Streaming'),
            ft.dropdown.Option('1', 'Signal-based'),
            ft.dropdown.Option('2', 'Time-based', disabled=True)
        ], dense=True, text_size=14, expand=1, value=self.trigger_idx, on_change=self.trigger_change_event,key=trigger_key)
        row = ft.Row([ft.Text('Select the trigger type (trigger)', size=14), help_icon,ft.Row(expand=1), self.trigger_input])

        plc_ip_key = 'plc_ip'
        self.plc_ip = CONFIG_OBJ[self.selected_project][plc_ip_key]
        plc_port_key = 'plc_port'
        self.plc_port = CONFIG_OBJ[self.selected_project][plc_port_key]
        Plc_ip_label = ft.Text('PLC IP', size=12)
        self.plc_ip_input = ft.TextField(value=self.plc_ip,width=200,text_size=14,on_change=self.project_config_save,key=plc_ip_key)
        Plc_port_label = ft.Text('PLC Port', size=12)
        self.plc_port_input = ft.TextField(value=self.plc_port,width=200,text_size=14,on_change=self.project_config_save,key=plc_port_key)
        plc_ip_row = ft.Row([Plc_ip_label, ft.Row(expand=1),self.plc_ip_input, ])
        plc_port_row = ft.Row([Plc_port_label, ft.Row(expand=1),self.plc_port_input, ])
    
        status_show = ft.Container()
        label = ft.Text('', size=12, width=100)
        label2 = ft.Text('', size=12, width=100, color=ft.colors.GREY)
        column = ft.Column([label, label2], spacing=0)
        self.test_plc_btn = ft.ElevatedButton('Test PLC', on_click=self.plc_connect_btn_clicked)
        self.trigger_row3 = ft.Row([ft.Row(expand=1),status_show, column, self.test_plc_btn])

        plc_trigger_address_key = 'plc_trigger_address'
        self.plc_trigger_address = CONFIG_OBJ[self.selected_project][plc_trigger_address_key]
        plc_trigger_count_key = 'plc_trigger_count'
        self.plc_trigger_count = CONFIG_OBJ[self.selected_project][plc_trigger_count_key]
        signal_type_key = 'signal_type'
        self.signal_type = CONFIG_OBJ[self.selected_project][signal_type_key]
        plc_trigger_address_label = ft.Text('PLC Trigger Address', size=12)
        plc_trigger_address_input = ft.TextField(value=self.plc_trigger_address,width=200,text_size=14,on_change=self.project_config_save,key=plc_trigger_address_key)
        plc_trigger_count_label = ft.Text('PLC Trigger Count', size=12)
        plc_trigger_count_input = ft.TextField(value=self.plc_trigger_count,width=200,text_size=14,on_change=self.project_config_save,key=plc_trigger_count_key)
        signal_type_label = ft.Text('Signal Type', size=12)
        signal_type_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', '上升沿'),
            ft.dropdown.Option('1', '下降沿'),
        ], dense=True, text_size=14, expand=1, value=self.signal_type, on_change=self.project_config_save,key=signal_type_key)
        plc_trigger_address_row = ft.Row([plc_trigger_address_label, ft.Row(expand=1),plc_trigger_address_input, ])
        plc_trigger_count_row = ft.Row([plc_trigger_count_label, ft.Row(expand=1),plc_trigger_count_input, ])
        signal_type_row = ft.Row([signal_type_label, ft.Row(expand=1),signal_type_input, ])

        card_content = ft.Container(ft.Column([row,  plc_ip_row, plc_port_row,  plc_trigger_address_row, plc_trigger_count_row, signal_type_row,self.trigger_row3,], spacing=20), padding=20)
        trigger_card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))

        # CAM设置
        cam_label = ft.Text('CAM settings', size=15)

        cam1_setting_label = ft.Text('CAM_1 settings', size=15)
        cam_tooltip = ft.Tooltip(message='Select the CAM type')
        help_icon = ft.Icon('help', color=ft.colors.GREY, size=16, tooltip=cam_tooltip)
        cam1_type_key = 'cam1_type'
        cam1_idx_key = 'cam1_idx'
        cam1_size_key = 'cam1_size'
        cam1_type=CONFIG_OBJ[self.selected_project][cam1_type_key]
        cam1_idx=CONFIG_OBJ[self.selected_project][cam1_idx_key]
        cam1_size = CONFIG_OBJ[self.selected_project][cam1_size_key]
        self.cam1_type_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', 'CV CAM'),
            ft.dropdown.Option('1', 'Hikvision'),
            ft.dropdown.Option('2', 'other',disabled=True)
        ], dense=True, text_size=14, expand=1, value=cam1_type, on_change=self.project_config_save,key=cam1_type_key)
        self.cam1_idx_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', '0'),
            ft.dropdown.Option('1', '1'),
            ft.dropdown.Option('2', '2'),
            ft.dropdown.Option('3', '3'),
        ], dense=True, text_size=14, expand=1, value=cam1_idx, on_change=self.project_config_save,key=cam1_idx_key)
        cam1_use_key = 'cam1_use'
        cam1_use=CONFIG_OBJ[self.selected_project][cam1_use_key]
        self.cam1_use_input = ft.Switch(value=cam1_use, on_change=self.project_config_save,key=cam1_use_key)
        self.cam1_size_input = ft.TextField(value=cam1_size,on_change=self.project_config_save,key=cam1_size_key)
        cam1_row = ft.Row([cam1_setting_label, help_icon, ft.Row(expand=1), self.cam1_type_input, self.cam1_idx_input,  self.cam1_use_input])
        cam1_row2 = ft.Row([ft.Text('Cam1 Size', size=14), ft.Row(expand=1), self.cam1_size_input])

        # cam2_setting_label = ft.Text('CAM_2 settings', size=15)
        # cam_tooltip = ft.Tooltip(message='Select the CAM type')
        # help_icon = ft.Icon('help', color=ft.colors.GREY, size=16, tooltip=cam_tooltip)
        # cam2_type_key = 'cam2_type'
        # cam2_idx_key = 'cam2_idx'
        # cam2_size_key = 'cam2_size'
        # cam2_type=CONFIG_OBJ[self.selected_project][cam2_type_key]
        # cam2_idx=CONFIG_OBJ[self.selected_project][cam2_idx_key]
        # cam2_size = CONFIG_OBJ[self.selected_project][cam2_size_key]
        # self.cam2_type_input = ft.Dropdown(options=[
        #     ft.dropdown.Option('0', 'CV CAM'),
        #     ft.dropdown.Option('1', 'Hikvision'),
        #     ft.dropdown.Option('2', 'other',disabled=True)
        # ], dense=True, text_size=14, expand=1, value=cam2_type, on_change=self.project_config_save,key=cam2_type_key)
        # self.cam2_idx_input = ft.Dropdown(options=[
        #     ft.dropdown.Option('0', '0'),
        #     ft.dropdown.Option('1', '1'),
        #     ft.dropdown.Option('2', '2'),
        #     ft.dropdown.Option('3', '3'),
        # ], dense=True, text_size=14, expand=1, value=cam2_idx, on_change=self.project_config_save,key=cam2_idx_key)
        # self.cam2_size_input = ft.TextField(value=cam2_size,on_change=self.project_config_save,key=cam2_size_key)
        # cam2_use_key = 'cam2_use'
        # cam2_use=CONFIG_OBJ[self.selected_project][cam2_use_key]
        # self.cam2_use_input = ft.Switch(value=cam2_use, on_change=self.project_config_save,key=cam2_use_key)
        # cam2_row = ft.Row([cam2_setting_label, help_icon, ft.Row(expand=1), self.cam2_type_input, self.cam2_idx_input,self.cam2_use_input])
        # cam2_row2 = ft.Row([ft.Text('Cam2 Size', size=14), ft.Row(expand=1), self.cam2_size_input])

        cam_card = ft.Card(ft.Container(ft.Column([cam1_row, cam1_row2]), padding=20), variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))


        # 模型选择
        model_label = ft.Text('Model settings', size=15)
        tooltip = ft.Tooltip(message='Select the model')
        help_icon = ft.Icon('help', color=ft.colors.GREY, size=16, tooltip=tooltip)

        model1_label = ft.Text('Model_1 path', size=15)
        model1_path_key = 'model1_path' 
        model1_confidence_key = 'model1_confidence'
        model1_iou_key = 'model1_iou'
        self.model1_path = CONFIG_OBJ[self.selected_project][model1_path_key]
        self.model1_confidence = CONFIG_OBJ[self.selected_project][model1_confidence_key]
        self.model1_iou = CONFIG_OBJ[self.selected_project][model1_iou_key]
        import_model1_btn = ft.OutlinedButton(content=ft.Text('Import model', size=12), on_click=self.import_model1_event)


        model1_use_key = 'model1_use'
        model1_use = CONFIG_OBJ[self.selected_project][model1_use_key]
        model1_use_input = ft.Switch(value=model1_use, on_change=self.project_config_save,key=model1_use_key)
        model1_row = ft.Row([
            model1_label, help_icon, ft.Row(expand=1), 
            ft.Text(self.model1_path[:20] + '...' if len(self.model1_path) > 20 else self.model1_path, size=10), 
            import_model1_btn, model1_use_input
            ]) 
        model1_confidence_input = ft.TextField(value=self.model1_confidence,on_change=self.project_config_save)
        model1_row2 = ft.Row([ft.Text('Model1 Confidence', size=14), ft.Row(expand=1), model1_confidence_input])
        model1_iou_input = ft.TextField(value=self.model1_iou,on_change=self.project_config_save,key=model1_iou_key)
        model1_row3 = ft.Row([ft.Text('Model1 IOU', size=14), ft.Row(expand=1), model1_iou_input])


        # model2_label = ft.Text('Model_2 path', size=15)
        # model2_path_key = 'model2_path'
        # model2_confidence_key = 'model2_confidence'
        # model2_iou_key = 'model2_iou'
        # model2_path = CONFIG_OBJ[self.selected_project][model2_path_key]
        # model2_confidence = CONFIG_OBJ[self.selected_project][model2_confidence_key]
        # model2_iou = CONFIG_OBJ[self.selected_project][model2_iou_key]
        # import_model2_btn = ft.OutlinedButton(content=ft.Text('Import model', size=12), on_click=self.import_model2_event)
        # model2_use_key = 'model2_use'
        # model2_use = CONFIG_OBJ[self.selected_project][model2_use_key]
        # model2_use_input = ft.Switch(value=model2_use, on_change=self.project_config_save,key=model2_use_key)
        # model2_row = ft.Row([
        #     model2_label, help_icon, ft.Row(expand=1), 
        #     ft.Text(model2_path[:20] + '...' if len(model2_path) > 20 else model2_path, size=10), 
        #     import_model2_btn, model2_use_input]) 
        # model2_confidence_input = ft.TextField(value=model2_confidence,on_change=self.project_config_save)
        # model2_row2 = ft.Row([ft.Text('Model2 Confidence', size=14), ft.Row(expand=1), model2_confidence_input])
        # model2_iou_input = ft.TextField(value=model2_iou,on_change=self.project_config_save,key=model2_iou_key)
        # model2_row3 = ft.Row([ft.Text('Model2 IOU', size=14), ft.Row(expand=1), model2_iou_input])


        model_card = ft.Card(ft.Container(ft.Column([model1_row, model1_row2, model1_row3]), padding=20), variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))


        # 输出设置
        output_label = ft.Text('Output settings', size=15)
        visual_key = 'visual'
        self.visual_input_value = CONFIG_OBJ[self.selected_project][visual_key]
        visual_label = ft.Text('Visual', size=14)
        visual_input = ft.Switch(value=self.visual_input_value, on_change=self.project_config_save,disabled=True,key=visual_key)
        visual_row = ft.Row([visual_label, ft.Row(expand=1), visual_input])

        gpio_key = 'gpio'
        self.gpio_input_value = CONFIG_OBJ[self.selected_project][gpio_key]
        gpio_output_point_key = 'gpio_output_point'
        gpio_output_point_value = CONFIG_OBJ[self.selected_project][gpio_output_point_key]
        gpio_label = ft.Text('GPIO', size=14)
        gpio_input = ft.Switch(value=self.gpio_input_value, on_change=self.project_config_save,key=gpio_key)
        gpio_row = ft.Row([gpio_label, ft.Row(expand=1), gpio_input])
        gpio_output_point_label = ft.Text('GPIO point', size=14)
        gpio_output_point = ft.Dropdown(options=[
            ft.dropdown.Option('0', '20'),
            ft.dropdown.Option('1', '21'),
            ft.dropdown.Option('2', '26'),
        ], dense=True, text_size=14, expand=1, value=gpio_output_point_value, on_change=self.project_config_save,key=gpio_output_point_key)
        gpio_output_point_row = ft.Row([gpio_output_point_label, ft.Row(expand=1), gpio_output_point])

        plc_output_key = 'plc_output'
        plc_output_address_key = 'plc_output_address'
        plc_output_value_key = 'plc_output_value'
        self.plc_output_input_value = CONFIG_OBJ[self.selected_project][plc_output_key]
        self.plc_output_address_value = CONFIG_OBJ[self.selected_project][plc_output_address_key]
        self.plc_output_value_value = CONFIG_OBJ[self.selected_project][plc_output_value_key]
        plc_output_label = ft.Text('PLC Output', size=14)
        plc_output_input = ft.Switch(value=self.plc_output_input_value, on_change=self.project_config_save,key=plc_output_key)
        plc_output_row = ft.Row([plc_output_label, ft.Row(expand=1), plc_output_input])
        plc_output_address_label = ft.Text('PLC Output Address', size=14)
        plc_output_address_input = ft.TextField(value=self.plc_output_address_value,on_change=self.project_config_save,key=plc_output_address_key)
        plc_output_address_row = ft.Row([plc_output_address_label, ft.Row(expand=1), plc_output_address_input]) 
        plc_output_value_label = ft.Text('PLC Output Value', size=14)
        plc_output_value_input = ft.TextField(value=self.plc_output_value_value,on_change=self.project_config_save,key=plc_output_value_key)
        plc_output_value_row = ft.Row([plc_output_value_label, ft.Row(expand=1), plc_output_value_input])

        status_output_key = 'status_output'
        status_output_address_key = 'status_output_address'
        status_output_value_key = 'status_output_value'
        self.status_output_input_value = CONFIG_OBJ[self.selected_project][status_output_key]
        self.status_output_address_value = CONFIG_OBJ[self.selected_project][status_output_address_key]
        self.status_output_value_value = CONFIG_OBJ[self.selected_project][status_output_value_key]
        status_output_label = ft.Text('Status Output', size=14)
        status_output_input = ft.Switch(value=self.status_output_input_value, on_change=self.project_config_save,key=status_output_key)
        status_output_row = ft.Row([status_output_label, ft.Row(expand=1), status_output_input])    
        status_output_address_label = ft.Text('Status Output Address', size=14)
        status_output_address_input = ft.TextField(value=self.status_output_address_value,on_change=self.project_config_save,key=status_output_address_key)
        status_output_address_row = ft.Row([status_output_address_label, ft.Row(expand=1), status_output_address_input])
        status_output_value_label = ft.Text('Status Output Value', size=14)
        status_output_value_input = ft.TextField(value=self.status_output_value_value,on_change=self.project_config_save,key=status_output_value_key)
        status_output_value_row = ft.Row([status_output_value_label, ft.Row(expand=1), status_output_value_input])

        result_save_key = 'result_save'
        result_save_path_key = 'result_save_path'
        self.result_save_value = CONFIG_OBJ[self.selected_project][result_save_key]
        self.result_save_path_value = CONFIG_OBJ[self.selected_project][result_save_path_key]
        result_save_label = ft.Text('Result save', size=14)
        result_save_input = ft.Switch(value=self.result_save_value, on_change=self.project_config_save,key=result_save_key)
        result_save_row = ft.Row([result_save_label, ft.Row(expand=1), result_save_input])
        result_save_path_label = ft.Text('Result save path', size=14)
        result_save_path_input = ft.Text(self.result_save_path_value[:20] + '...' if len(self.result_save_path_value) > 20 else self.result_save_path_value, 
                                       size=10, 
                                       tooltip=self.result_save_path_value)
        result_save_path_import_btn = ft.OutlinedButton(content=ft.Text('Import path', size=12), on_click=self.import_result_save_path_event)
        result_save_path_row = ft.Row([result_save_path_label, ft.Row(expand=1), result_save_path_input, result_save_path_import_btn])

        output_card = ft.Card(ft.Container(ft.Column([ visual_row, gpio_row, gpio_output_point_row, plc_output_row, plc_output_address_row, plc_output_value_row, status_output_row, status_output_address_row, status_output_value_row,result_save_row, result_save_path_row]), padding=20), variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))


        # 逻辑设置
        logic_label = ft.Text('Logic settings', size=15)    
        logic_type_key = 'logic_type'
        logic_type_value = CONFIG_OBJ[self.selected_project][logic_type_key]
        logic_type_label = ft.Text('Logic type', size=14)
        logic_type_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', 'detected objects [in] selected objects'),
            ft.dropdown.Option('1', 'selected objects [in] detected objects'),
            ft.dropdown.Option('2', 'detected objects [=] selected objects'),
        ], dense=True, text_size=14, expand=1, value=logic_type_value, on_change=self.project_config_save,key=logic_type_key)
        logic_type_row = ft.Row([logic_type_label, ft.Row(expand=1), logic_type_input])

        model1_selected_objects_key = 'model1_selected_objects'
        self.model1_selected_objects_value = CONFIG_OBJ[self.selected_project][model1_selected_objects_key].split(',')[0:-1]
        model1_selected_objects_label = ft.Text('Model1 selected objects', size=14)
        self.model1_selected_objects_show = ft.Text(self.model1_selected_objects_value, size=14)
        model1_selected_objects_row = ft.Row([model1_selected_objects_label, ft.Row(expand=1), self.model1_selected_objects_show])

        status_show = ft.Container()
        label = ft.Text('', size=12, width=100)
        label2 = ft.Text('', size=12, width=100, color=ft.colors.GREY)
        column = ft.Column([label, label2], spacing=0)
        self.check_model_btn = ft.ElevatedButton('Check model', on_click=self.check_model_btn_clicked)
        self.model_check_row = ft.Row([ft.Row(expand=1),status_show, column, self.check_model_btn])
        self.model_class_select = ft.Column([])
        

        # model2_selected_objects_key = 'model2_selected_objects'
        # model2_selected_objects_value = CONFIG_OBJ[self.selected_project][model2_selected_objects_key]
        # model2_selected_objects_label = ft.Text('Model2 selected objects', size=14)
        # model2_selected_objects_input = ft.Dropdown(options=[# TODO: 改为多选框，并从模型文件中读取
        #     ft.dropdown.Option('0', '0'),
        #     ft.dropdown.Option('1', '1'),
        #     ft.dropdown.Option('2', '2'),
        # ], dense=True, text_size=14, expand=1, value=model2_selected_objects_value, on_change=self.project_config_save,key=model2_selected_objects_key)
        # model2_selected_objects_row = ft.Row([model2_selected_objects_label, ft.Row(expand=1), model2_selected_objects_input])


        logic_card = ft.Card(ft.Container(ft.Column([logic_type_row, model1_selected_objects_row, self.model_check_row, self.model_class_select]), padding=20), variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))



        # 其他设置
        other_label = ft.Text('Other settings', size=15)

        scan_key = 'scan'
        scan_value = CONFIG_OBJ[self.selected_project][scan_key]
        scan_label = ft.Text('Scan', size=14)
        scan_input = ft.Switch(value=scan_value, on_change=self.project_config_save,key=scan_key)
        scan_row = ft.Row([scan_label, ft.Row(expand=1), scan_input])


        other_card = ft.Card(ft.Container(ft.Column([scan_row]), padding=20), variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))

        column = ft.Column([project_label, project_card, trigger_label, trigger_card, cam_label, cam_card, model_label, model_card, output_label, output_card, logic_label, logic_card, other_label, other_card], width=720, spacing=12)
        tab_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))
        self.content = ft.Column([tab_container], scroll=ft.ScrollMode.AUTO)





    def project_config_load(self):
        """加载项目配置"""
        # print("===>project_config_load")

        pass

    def project_config_save(self,e:ft.ControlEvent):
        """保存项目配置"""
        print("===>project_config_save")
        print(f'current project: {self.selected_project}, key: {e.control.key}, value: {e.control.value}')
        #保存到配置文件
        key = e.control.key # 获取控件的key
        value = e.control.value # 获取控件的value
        if CONFIG_OBJ.has_section(self.selected_project):
            CONFIG_OBJ.set(self.selected_project, key, str(value))  
        else:
            CONFIG_OBJ.add_section(self.selected_project)
            CONFIG_OBJ.set(self.selected_project, key, str(value))
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)




    def snack_message(self, message, color):
        self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()



    def project_change_event(self,e:ft.ControlEvent):
        """保存配置文件"""
        CONFIG_OBJ['deploy_function']['project'] = str(e.control.value)

        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
        self.selected_project = e.control.value
        self.refresh_config()


    def add_project_event(self, e: ft.ControlEvent):
        """添加项目事件"""
        print("===>add_project_event")
        #弹窗输入项目名称
        def on_dialog_submit(d):
            new_project_name = d.content.value
            if new_project_name:
                # check if choice already exists
                if new_project_name in [option.key for option in self.project_input.options]:
                    self.snack_message(f'Choice {new_project_name} already exists', 'red')
                    return
                        # 添加项目
                CONFIG_OBJ['deploy_function']['project_list'] = CONFIG_OBJ['deploy_function']['project_list']  + new_project_name+','
                # 添加项目配置
                CONFIG_OBJ[new_project_name] = {
                    'trigger_type' : 1,
                    'plc_ip' : '192.168.1.0',
                    'plc_port' : 5020,
                    'plc_trigger_address' : 1,
                    'plc_trigger_count' : 1,
                    'signal_type' : 1,
                    'cam1_type' : 0,
                    'cam1_idx' : 1,
                    'cam1_size' : 1024,
                    'cam1_use' : True,
                    'cam2_type' : 1,
                    'cam2_idx' : 1,
                    'cam2_size' : 6400,
                    'cam2_use' : True,
                    'model1_path' : 'c:/Users/Administrator/Desktop/test.pt',
                    'model1_confidence' : 0.5,
                    'model1_iou' : 0.54,
                    'model1_use' : True,
                    'model2_path' : 'c:/Users/Administrator/Desktop/test.pt',
                    'model2_confidence' : 0.5,
                    'model2_iou' : 0.51,
                    'model2_use' : False,
                    'visual' : True,
                    'gpio' : False,
                    'plc_output' : True,
                    'status_output' : True,
                    'status_output_address' : 3,
                    'status_output_value' : 666,
                    'result_save' : True,
                    'result_save_path' : 'c:/Users/Administrator/Desktop/result',
                    'gpio_output_point' : 2,
                    'plc_output_address' : 2,
                    'plc_output_value' : 888,
                    'logic_type' : 0,
                    'model1_selected_objects' : '',
                    'model2_selected_objects' : '',
                    'scan' : False
                }
                with open('user_data/config.ini', 'w', encoding='utf-8') as f:
                    CONFIG_OBJ.write(f)
                # 更新项目列表
                options=CONFIG_OBJ['deploy_function']['project_list']
                options=options.split(',')
                options=options[0:-1]
                options = [ft.dropdown.Option(i, i) for i in options]
                self.project_input.options = options
                self.project_input.value = new_project_name
                self.project_input.update()
                # 更新项目选择
                CONFIG_OBJ['deploy_function']['project'] = new_project_name
                with open('user_data/config.ini', 'w', encoding='utf-8') as f:
                    CONFIG_OBJ.write(f)
                self.selected_project = new_project_name

                self.refresh_config()

            d.open = False
            d.update()
            self.snack_message(f'Add choice{new_project_name} success', 'green')

        def on_dialog_cancel(d):
            d.open = False
            d.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Add Choice"),
            content=ft.TextField(label="Enter choice"),
            actions=[
                ft.TextButton("Submit", on_click=lambda _: on_dialog_submit(dialog)),
                ft.TextButton("Cancel", on_click=lambda _: on_dialog_cancel(dialog))
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()


    def refresh_config(self):
        """刷新配置"""
        print("===>refresh_config")
        #重新加载页面,如何实现def _init_widgets(self):重新加载
        self._init_widgets()
        self.page.update()


    def remove_project_event(self, e: ft.ControlEvent):
        """删除项目事件"""
        remove_project = self.selected_project
        print(f"===>remove_project_event, remove_project: {remove_project}")

        # 删除配置文件中的项目
        CONFIG_OBJ.remove_section(remove_project)
        # 删除配置文件中的项目列表
        CONFIG_OBJ['deploy_function']['project_list'] = CONFIG_OBJ['deploy_function']['project_list'].replace(remove_project+',', '')
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)

        #更新项目列表
        options=CONFIG_OBJ['deploy_function']['project_list']
        options=options.split(',')
        options=options[0:-1]
        self.selected_project = options[0]
        # 保存配置文件
        CONFIG_OBJ['deploy_function']['project'] = str(self.selected_project)

        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)


        options = [ft.dropdown.Option(i, i) for i in options]
        self.project_input.options = options
        self.project_input.value = self.selected_project
        self.project_input.update()
        self.refresh_config()

        pass
    
    def trigger_change_event(self, e: ft.ControlEvent):
        """触发类型选择事件"""
        print("===>trigger_change_event")
        self.project_config_save(e)
        

    def plc_connect_btn_clicked(self, e: ft.ControlEvent):
        """PLC连接按钮被点击的事件"""
        print("===>plc_connect_event")
        Thread(target=self.plc_connect_event, daemon=True).start()


    def plc_connect_event(self):
        """开启额外线程检查更新"""
        self.trigger_row3.controls[1] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.trigger_row3.controls[2].controls[0].value = '正在检查PLC连接'
        self.test_plc_btn.disabled = True
        self.trigger_row3.update()
        # 检查plc连接 TODO
        time.sleep(0.5)
        self.trigger_row3.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
        self.trigger_row3.controls[2].controls[0].value = 'PLC连接检查成功'
        self.trigger_row3.controls[2].controls[1].value = f'IP:{self.plc_ip_input.value}, Port:{self.plc_port_input.value}'
        self.test_plc_btn.disabled = False
        self.trigger_row3.update()


    def check_model_btn_clicked(self,e:ft.ControlEvent):
        """检查模型按钮被点击的事件"""
        print("===>check_model_btn_clicked")
        Thread(target=self.check_model_event, daemon=True).start()

    def check_model_event(self):
        """开启额外线程检查更新"""
        self.model_check_row.controls[1] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.model_check_row.controls[2].controls[0].value = '正在检查模型'
        self.check_model_btn.disabled = True
        self.model_check_row.update()

        try:
            
            from ultralytics import YOLO
            model = YOLO(self.model1_path)
            classes = model.names
            current_class = CONFIG_OBJ[self.selected_project]['model1_selected_objects'].split(',')[0:-1]


            class_values = list(classes.values())

            # 检查classes是否包含current_class
            for class_value in current_class:
                if class_value not in class_values:
                    self.snack_message(f'{class_value} not in model, reset to default', 'red')
                    CONFIG_OBJ[self.selected_project]['model1_selected_objects'] = ''
                    with open('user_data/config.ini', 'w', encoding='utf-8') as f:
                        CONFIG_OBJ.write(f)


            self.model_class_select.controls = []
            for i, class_key in enumerate(classes.keys()):
                self.model_class_select.controls.append(ft.Checkbox(
                    label=classes[class_key], 
                    value=True if classes[class_key] in current_class else False,
                    on_change=self.save_model_selected_class))

            self.model_class_select.update()

            self.model_check_row.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
            self.model_check_row.controls[2].controls[0].value = '模型检查成功'
            self.model_check_row.controls[2].controls[1].value = f'model1_class'
            self.check_model_btn.disabled = False
            self.model_check_row.update()


        except Exception as e:
            print(f"===>check_model_event error: {e}")
            self.model_check_row.controls[1] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
            self.model_check_row.controls[2].controls[0].value = '模型检查失败'
            self.model_check_row.controls[2].controls[1].value = f'请确认模型地址是否正确'
            self.check_model_btn.disabled = False
            self.model_check_row.update()


    def save_model_selected_class(self, e: ft.ControlEvent):
        """保存模型类别事件"""
        print("===>save_model_selected_class")
        # 获取当前选中的类别
        current_class = CONFIG_OBJ[self.selected_project]['model1_selected_objects']
        if e.control.value:
            CONFIG_OBJ[self.selected_project]['model1_selected_objects'] = current_class + e.control.label + ','
        else:
            CONFIG_OBJ[self.selected_project]['model1_selected_objects'] = current_class.replace(e.control.label + ',', '')
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)

        # 更新模型类别选择
        self.model1_selected_objects_value = CONFIG_OBJ[self.selected_project]['model1_selected_objects'].split(',')[0:-1]
        self.model1_selected_objects_show.value = self.model1_selected_objects_value
        self.model1_selected_objects_show.update()

    def import_result_save_path_event(self, e: ft.ControlEvent):
        """导入结果保存路径事件"""
        print("===>import_result_save_path_event")
        # 弹窗选择路径 
        dialog = ft.FilePicker(on_result=self.pick_result_save_path_finished)
        self.page.overlay.append(dialog)
        self.page.update()
        dialog.get_directory_path()
        pass
    
    def pick_result_save_path_finished(self, e: ft.FilePickerResultEvent):
        """选择结果保存路径结束后触发的事件"""
        if e.path is None:
            self.page.overlay.remove(e.control)
            self.page.update()
            return
        result_save_path = e.path
        self.page.overlay.remove(e.control)
        self.page.update()
        CONFIG_OBJ[self.selected_project]['result_save_path'] = result_save_path
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
        self.refresh_config()
    
    def import_model1_event(self, e: ft.ControlEvent):
        """导入模型事件"""
        print("===>import_model1_event")
        # 弹窗选择路径 
        dialog = ft.FilePicker(on_result=self.pick_model1_finished)
        self.page.overlay.append(dialog)
        self.page.update()
        dialog.pick_files('选择模型', allowed_extensions=['pt'])
        pass

    def pick_model1_finished(self, e: ft.FilePickerResultEvent):
        """选择模型结束后触发的事件"""
        if e.files is None:
            self.page.overlay.remove(e.control)
            self.page.update()
            return
        model1_path = e.files[0].path
        self.page.overlay.remove(e.control)
        self.page.update()
        CONFIG_OBJ[self.selected_project]['model1_path'] = model1_path
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
        self.refresh_config()


    def import_model2_event(self, e: ft.ControlEvent):
        """导入模型事件"""
        print("===>import_model2_event")
        # 弹窗选择路径 
        dialog = ft.FilePicker(on_result=self.pick_model2_finished)
        self.page.overlay.append(dialog)
        self.page.update()
        dialog.pick_files('选择模型', allowed_extensions=['pt'])
        pass

    def pick_model2_finished(self, e: ft.FilePickerResultEvent):
        """选择模型结束后触发的事件"""
        if e.files is None:
            self.page.overlay.remove(e.control)
            self.page.update()
            return
        model2_path = e.files[0].path
        self.page.overlay.remove(e.control)
        self.page.update()
        CONFIG_OBJ[self.selected_project]['model2_path'] = model2_path
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)
        self.refresh_config()


class BaseTab2(ft.Tab):
    def __init__(self):
        """CAM页面"""
        super().__init__()
        self.text = 'CAM'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))


class BaseTab3(ft.Tab):
    def __init__(self):
        """Model页面"""
        super().__init__()
        self.text ='Model'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))

class BaseTab4(ft.Tab):
    def __init__(self):
        """Output页面"""
        super().__init__()
        self.text = 'Output'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))


class BaseTab5(ft.Tab):
    def __init__(self):
        """PLC test页面"""
        super().__init__()
        self.text = 'PLC test'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))

