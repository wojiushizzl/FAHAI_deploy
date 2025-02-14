import flet as ft
from custom_widgets.image_viewer import ImageViewer
from common.app_setting import Setting, CONFIG_OBJ
from custom_requests.catgpt import CatGPT
import os
import pickle
import datetime
import time
from threading import Thread
from typing import List, Optional


class InterestsWindow(ft.Container):
    def __init__(self):
        """兴趣内容窗口"""
        super().__init__()
        self.expand = 1
        self.padding = ft.Padding(10, 0, 82, 30)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.base_tab = BaseTab()
        self.generate_tab = GenerateTab()
        self.chat_tab = ChatTab()
        tab_widget = ft.Tabs(tabs=[self.base_tab, self.generate_tab, self.chat_tab], animation_duration=300,
                             selected_index=1, tab_alignment=ft.TabAlignment.START)
        self.content = tab_widget


class BaseTab(ft.Tab):
    def __init__(self):
        """基础功能页面"""
        super().__init__()
        self.text = '基础功能'
        self.icon = ft.icons.LOCAL_FLORIST

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        self.content = ft.Container(ft.Text("这是包含基本的图像处理功能的界面，功能即将推出", size=24,
                                            color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))


class GenerateTab(ft.Tab):
    def __init__(self):
        """图像生成页面"""
        super().__init__()
        self.text = '进阶功能'
        self.icon = ft.icons.LOCAL_FIRE_DEPARTMENT

        self.travel = None
        self.run_thread: Optional[Thread] = None
        self.first_selected = True
        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        main_btn = ft.IconButton(ft.icons.PLAY_CIRCLE_OUTLINE, tooltip='开始', icon_size=36,
                                 icon_color=ft.colors.PRIMARY, on_click=self.main_btn_clicked)
        show_hide_btn = ft.IconButton(ft.icons.KEYBOARD_DOUBLE_ARROW_UP, tooltip='显示配置栏', icon_size=36,
                                      icon_color=ft.colors.SECONDARY, on_click=self.show_hide_btn_clicked)
        txt = """点击左侧按钮打开配置栏，可选择不同的功能；\n美颜功能需要选择原图后，点击最左侧开始按钮；\n换脸功能需选择原图及模板图后，点击最左侧开始按钮。"""
        help_icon = ft.IconButton(ft.icons.HELP_OUTLINE, icon_size=36, icon_color=ft.colors.SECONDARY,
                                  tooltip=ft.Tooltip(message=txt))
        toolbar = ft.Row([main_btn, show_hide_btn, help_icon], alignment=ft.MainAxisAlignment.CENTER)

        self.image_viewer = ImageViewer(save_dir=Setting.download_dir, upload_dir=Setting.upload_dir)
        self.image_viewer.expand = 1
        self.image_viewer.width = None
        label = ft.Row([ft.Text('原图')], alignment=ft.MainAxisAlignment.CENTER)
        image_box = ft.Container(ft.Column([self.image_viewer, label]), expand=3)

        self.image_viewer2 = ImageViewer(save_dir=Setting.download_dir, upload_dir=Setting.upload_dir)
        self.image_viewer2.expand = 1
        self.image_viewer2.width = None
        label2 = ft.Row([ft.Text('模板图')], alignment=ft.MainAxisAlignment.CENTER)
        image_box2 = ft.Container(ft.Column([self.image_viewer2, label2]), expand=3)

        self.image_viewer3 = ImageViewer(True, save_dir=Setting.download_dir, upload_dir=Setting.upload_dir)
        self.image_viewer3.expand = 1
        self.image_viewer3.width = None
        label3 = ft.Row([ft.Text('生成图')], alignment=ft.MainAxisAlignment.CENTER)
        image_box3 = ft.Container(ft.Column([self.image_viewer3, label3]), expand=3)
        row = ft.Row([image_box, ft.Row(expand=1), image_box2, ft.Row(expand=1), image_box3], spacing=0)
        container = ft.Container(row, expand=7, padding=ft.Padding(40, 0, 40, 10))

        label = ft.Text('功能选择', size=16)
        segments = [ft.Segment('1', ft.Icon(ft.icons.LOOKS_ONE), ft.Text('美颜', size=12, tooltip='选择原图后点击开始按钮')),
                    ft.Segment('2', ft.Icon(ft.icons.LOOKS_TWO), ft.Text('换脸', size=12, tooltip='选择原图及模板图后点击开始按钮'))]
        self.segment_btn = ft.SegmentedButton(selected_icon=ft.Icon(ft.icons.CHECK), selected={'1'},
                                              on_change=self.segment_btn_clicked, segments=segments)
        box = ft.Container(ft.Column([label, self.segment_btn]), margin=5)

        label2 = ft.Text('结果图展示', size=16)
        self.switch = ft.Switch('生成大头照', value=False)
        box2 = ft.Container(ft.Column([label2, self.switch]), margin=5)
        self.setting_card = ft.Card(ft.Row([box, box2], alignment=ft.MainAxisAlignment.CENTER, spacing=40), height=0,
                                    animate_size=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT_CUBIC),
                                    color=ft.colors.TRANSPARENT, variant=ft.CardVariant.OUTLINED)

        status_show = ft.Container()
        status_label = ft.Text(value='', width=150, size=16)
        time_label = ft.Text(value='', size=14)
        column = ft.Column([status_label, time_label], spacing=2)
        self.status_show_row = ft.Row([status_show, column], alignment=ft.MainAxisAlignment.CENTER,
                                      vertical_alignment=ft.CrossAxisAlignment.CENTER)
        status_show_container = ft.Container(self.status_show_row)

        column = ft.Column([ft.Column(expand=1), container, ft.Column([status_show_container], expand=1),
                            self.setting_card], spacing=10)
        content_container = ft.Container(column, expand=1)
        interest_content = ft.Container(ft.Column([toolbar, content_container], spacing=0))
        self.content = interest_content

    def show_hide_btn_clicked(self, e: ft.ControlEvent):
        """显示或隐藏配置栏"""
        if self.setting_card.height == 0:
            self.setting_card.height = 100
            e.control.icon = ft.icons.KEYBOARD_DOUBLE_ARROW_DOWN
            e.control.tooltip = '显示配置栏'
        else:
            self.setting_card.height = 0
            e.control.icon = ft.icons.KEYBOARD_DOUBLE_ARROW_UP
            e.control.tooltip = '隐藏配置栏'

        self.update()

    def main_btn_clicked(self, e: ft.ControlEvent):
        """点击运行按钮的事件"""
        if not os.path.exists(Setting.temp_dir):
            os.makedirs(Setting.temp_dir, exist_ok=True)

        if self.run_thread is None or not self.run_thread.is_alive():
            self.run_thread = Thread(target=self.thread_event, daemon=True)
            self.run_thread.start()

    def thread_event(self):
        """开启额外线程运行图像生成功能"""
        self.status_show_row.controls[0] = ft.ProgressRing(height=16, width=16, stroke_width=2)
        self.status_show_row.controls[1].controls[0].value = '正在处理中'
        self.status_show_row.controls[1].controls[1].value = '耗时：？'
        self.status_show_row.update()

        time.sleep(0.3)
        self.status_show_row.controls[0] = ft.Icon(ft.icons.ERROR, size=20, color=ft.colors.ERROR)
        self.status_show_row.controls[1].controls[0].value = '此版本不支持该功能'
        self.status_show_row.controls[1].controls[1].value = '耗时：0.0s'
        self.status_show_row.update()

    def segment_btn_clicked(self, e: ft.ControlEvent):
        """功能选择按钮被点击触发的事件"""
        if not self.first_selected:
            return

        if tuple(self.segment_btn.selected)[0] != '2':
            return

        txt = '''此协议仅关于“换脸”功能。使用该功能前请仔细阅读许可协议（“许可证”），选择“同意”即表示用户同意接受本许可的条款约束，如果用户不同意本许可的条款，请选择“拒绝”。\n
        1、使用该功能生成的图片如需对外传播，请注明图片出处，明确表示图片为AI生成，现实并不存在。
        2、生成的图片不能对他人造成困扰、欺骗，不用于非法、不道德的目的，软件的制作者对因该功能滥用造成的不良后果概不负责。'''
        dialog = ft.AlertDialog(modal=True, open=True, title=ft.Text('许可协议', color=ft.colors.PRIMARY),
                                content=ft.Text(txt),
                                actions=[ft.TextButton('同意', on_click=self.dialog_btn_clicked),
                                         ft.TextButton('拒绝', on_click=self.dialog_btn_clicked)])
        self.page.overlay.append(dialog)
        self.page.update()

    def dialog_btn_clicked(self, e: ft.ControlEvent):
        """许可协议对话框中的按钮被点击的事件"""
        txt = e.control.text
        if txt == '同意':
            self.first_selected = False
        else:
            self.segment_btn.selected = {'1'}

        e.control.parent.open = False
        self.page.update()
        self.page.overlay.remove(e.control.parent)


class ChatTab(ft.Tab):
    def __init__(self):
        """AI聊天页面"""
        super().__init__()
        self.text = '聊天对话'
        self.icon = ft.icons.CHAT

        self.cat_gpt: Optional[CatGPT] = None
        self.run_thread: Optional[Thread] = None
        self.qwen_controls = []
        self.yuanqi_controls = []
        self._load_data()
        self._init_widgets()

    def _load_data(self):
        """从本地文件中导入聊天记录，保证消息记录不为空"""
        if os.path.exists(Setting.gpt_message_path):
            with open(Setting.gpt_message_path, 'rb') as f:
                self.message_data = pickle.load(f)
        else:
            now_datetime = str(datetime.datetime.now())[:19]
            qwen_messages = [{'datetime': now_datetime, 'content': '您好！有什么可以帮助您的吗？', 'continuous': False,
                              'role': 'assistant', 'token_count': 0}]
            yuanqi_messages = [{'datetime': now_datetime, 'content': '你好，有什么想和我说的吗~', 'continuous': False,
                                'role': 'assistant', 'token_count': 0}]
            self.message_data = {'qwen': qwen_messages, 'yuanqi': yuanqi_messages}

    @staticmethod
    def mes_container_hover(e: ft.ControlEvent):
        """将鼠标放在消息上的事件"""
        e.control.parent.controls[0].opacity = 1 if e.data == 'true' else 0
        e.control.parent.controls[0].update()

    def _init_widgets(self):
        # 左侧配置项
        self.qwen_chat = ft.Container(image=ft.DecorationImage(src='/images/qwen.png'), shape=ft.BoxShape.CIRCLE,
                                      width=48, height=48, on_click=self.switch_gpt, tooltip='通义千问',
                                      shadow=ft.BoxShadow(blur_style=ft.ShadowBlurStyle.OUTER, blur_radius=12,
                                                          color=ft.colors.SECONDARY))
        self.yuanqi_chat = ft.Container(image=ft.DecorationImage(src='/images/yuanqi.jpg'), shape=ft.BoxShape.CIRCLE,
                                        width=48, height=48, on_click=self.switch_gpt, tooltip='心灵树洞')
        column = ft.Column([self.qwen_chat, self.yuanqi_chat], alignment=ft.MainAxisAlignment.END,
                           horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.left_container = ft.Container(column, padding=ft.Padding(0, 10, 0, 100))

        # 右侧配置项
        common_setting_text = ft.Text('通用配置', size=14)
        txt = '开启后，AI助理将回忆与您最近的聊天内容，\n通常会得到更准确的回复，但会消耗更多Token。'
        self.record_context_chip = ft.Chip(ft.Text('记录上下文', size=12), elevation=8, autofocus=False,
                                           on_select=lambda _: ..., tooltip=txt)
        clean_context_chip = ft.Chip(ft.Text('清除上下文', size=12), elevation=8, leading=ft.Icon('cleaning_services'),
                                     on_click=self.clean_context_clicked)
        common_setting_container = ft.Container(
            ft.Column([common_setting_text, self.record_context_chip, clean_context_chip]))
        qwen_setting_text = ft.Text('通义千问配置', size=14)
        options = [ft.dropdown.Option('0', 'qwen-max'),
                   ft.dropdown.Option('1', 'qwen-plus'),
                   ft.dropdown.Option('2', 'qwen-turbo'),
                   ft.dropdown.Option('3', 'qwen-long'),
                   ft.dropdown.Option('4', 'qwen2-math-72b-instruct')]
        self.model_dropdown = ft.Dropdown('1', options=options, dense=True, text_size=12,
                                          tooltip='点击切换通义千问模型')
        self.qwen_setting_container = ft.Container(ft.Column([qwen_setting_text, self.model_dropdown]))
        self.yuanqi_setting_container = ft.Container()
        self.setting_column = ft.Column([common_setting_container, self.qwen_setting_container],
                                        alignment=ft.MainAxisAlignment.END, spacing=30)
        right_container = ft.Container(self.setting_column, margin=ft.Margin(0, 10, 0, 100), width=120)

        # 中间消息显示及输入框
        self.qwen_controls = self.generate_message_views(self.message_data['qwen'])
        self.yuanqi_controls = self.generate_message_views(self.message_data['yuanqi'])
        self.list_view = ft.ListView(self.qwen_controls, auto_scroll=True, padding=ft.Padding(20, 10, 20, 10))
        card = ft.Card(self.list_view, expand=1, variant=ft.CardVariant.OUTLINED, color=ft.colors.TRANSPARENT)

        self.text_input = ft.TextField(hint_text='请输入您想问的问题', max_length=6000, shift_enter=True,
                                       border_radius=10, autofocus=True, text_size=14,
                                       max_lines=3, expand=1, on_submit=self.input_submit)
        self.send_btn = ft.IconButton(ft.icons.SEND_ROUNDED, tooltip='发送', icon_size=30, on_click=self.input_submit)
        row = ft.Row([self.text_input, ft.Container(self.send_btn, padding=ft.Padding(0, 0, 0, 10))])
        container = ft.Container(row, padding=ft.Padding(10, 0, 10, 0))

        center_container = ft.Container(ft.Column([card, container]), expand=1)
        content_container = ft.Container(ft.Row([self.left_container, center_container, right_container]),
                                         margin=ft.Margin(20, 20, 0, 0))
        self.content = content_container

    def generate_message_view(self, message: dict, show_system_msg: bool = False) -> Optional[list]:
        """
        根据单条消息记录生成信息展示组件
        :param message: 消息记录
        :param show_system_msg: 是否展示系统消息
        :return: 如果符合要求，返回信息展示控件组成的列表
        """
        if message['role'] == 'system' and not show_system_msg:
            return

        today_obj = datetime.date.today()
        today = str(today_obj)
        controls = []
        # 如果消息间隔时间过长，在消息窗口中间展示时间
        if not message['continuous']:
            publish_datetime = message['datetime']
            if publish_datetime[:10] == today:
                time_show = publish_datetime[11:16]
            elif (today_obj - datetime.date(int(publish_datetime[:4]), int(publish_datetime[5:7]),
                                            int(publish_datetime[8:10]))).days == 1:
                time_show = f'昨天{publish_datetime[10:16]}'
            else:
                time_show = publish_datetime[5:16]

            text = ft.Text(time_show, color=ft.colors.SECONDARY, expand=1, text_align=ft.TextAlign.CENTER, size=12)
            controls.append(text)

        # 当消息类型为用户、AI助理或系统时，分别创建不同的组件
        time_show = message['datetime'][5:]
        text = ft.Text(time_show, size=12, opacity=0, animate_opacity=300)
        container_expand = None if len(message['content']) < 30 else 3
        if message['role'] == 'user':
            mes_control = ft.Text(message['content'], selectable=True, size=14)
            container = ft.Container(mes_control, bgcolor='primarycontainer', padding=10, border_radius=10,
                                     on_hover=self.mes_container_hover)
            column = ft.Column([text, container], spacing=0, expand=container_expand,
                               horizontal_alignment=ft.CrossAxisAlignment.END)
            row = ft.Row([ft.Row(expand=2), column])
        elif message['role'] == 'assistant':
            if message['token_count'] > 0:
                text.value = f'{text.value} | Tokens: {message["token_count"]}'
            mes_control = ft.Markdown(message['content'], selectable=True,
                                      extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, auto_follow_links=True)
            container = ft.Container(mes_control, bgcolor='secondarycontainer', padding=10, border_radius=10,
                                     on_hover=self.mes_container_hover)
            column = ft.Column([text, container], spacing=0, expand=container_expand,
                               horizontal_alignment=ft.CrossAxisAlignment.START)
            row = ft.Row([column, ft.Row(expand=2)])
        else:
            mes_control = ft.Text(message['content'], size=12, color=ft.colors.TERTIARY)
            row = ft.Row([mes_control], alignment=ft.MainAxisAlignment.CENTER)

        controls.append(row)
        return controls

    def generate_message_views(self, messages: List[dict]):
        """
        根据不同类型的消息记录生成多个信息展示组件
        :param messages: 多条消息记录组成的列表
        :return: 多个信息展示组件
        """
        controls = []
        for i in messages:
            results = self.generate_message_view(i)
            if results:
                controls.extend(results)
            else:
                continue
        return controls

    def switch_gpt(self, e: ft.ControlEvent):
        """切换AI聊天助理"""
        box_shadow = ft.BoxShadow(blur_style=ft.ShadowBlurStyle.OUTER, blur_radius=12, color=ft.colors.SECONDARY)
        if e.control is self.qwen_chat:
            self.qwen_chat.shadow = box_shadow
            self.yuanqi_chat.shadow = None
            self.list_view.controls = self.qwen_controls
            self.setting_column.controls[1] = self.qwen_setting_container
        else:
            self.yuanqi_chat.shadow = box_shadow
            self.qwen_chat.shadow = None
            self.list_view.controls = self.yuanqi_controls
            self.setting_column.controls[1] = self.yuanqi_setting_container

        self.update()

    def input_submit(self, e: ft.ControlEvent):
        """输入框的提交事件"""
        txt = self.text_input.value.strip()
        if not txt:
            return
        if self.run_thread is not None and self.run_thread.is_alive():
            return

        datetime_obj = datetime.datetime.now()
        now_datetime = str(datetime_obj)[:19]
        if self.qwen_chat.shadow:
            last_datetime = self.message_data['qwen'][-1]['datetime']
        else:
            last_datetime = self.message_data['yuanqi'][-1]['datetime']
        last_datetime_obj = datetime.datetime(int(last_datetime[:4]), int(last_datetime[5:7]), int(last_datetime[8:10]),
                                              int(last_datetime[11:13]), int(last_datetime[14:16]),
                                              int(last_datetime[17:19]))
        continuous = False if (datetime_obj - last_datetime_obj).seconds > 300 else True

        message = {'datetime': now_datetime, 'content': txt, 'continuous': continuous, 'role': 'user', 'token_count': 0}
        results = self.generate_message_view(message)
        if self.qwen_chat.shadow:
            self.qwen_controls.extend(results)
            self.message_data['qwen'].append(message)
        else:
            self.yuanqi_controls.extend(results)
            self.message_data['yuanqi'].append(message)

        self.list_view.controls.extend(results)
        self.text_input.value = ''
        self.update()

        with open(Setting.gpt_message_path, 'wb') as f:
            pickle.dump(self.message_data, f)
        self.run_thread = Thread(target=self.thread_event, daemon=True)
        self.run_thread.start()

    def thread_event(self):
        """开启额外线程聊天"""
        if self.cat_gpt is None:
            qwen_bearer = CONFIG_OBJ['function']['qwen_key']
            yuanqi_bearer = CONFIG_OBJ['function']['yuanqi_token']
            yuanqi_id = CONFIG_OBJ['function']['yuanqi_id']
            self.cat_gpt = CatGPT(qwen_bearer, yuanqi_bearer, yuanqi_id)

        self.send_btn.disabled = True
        self.send_btn.update()
        datetime_obj = datetime.datetime.now()
        now_datetime = str(datetime_obj)[:19]
        gpt_type = 'qwen' if self.qwen_chat.shadow else 'yuanqi'
        record_context = self.record_context_chip.selected
        if gpt_type == 'qwen':
            model_type = self.model_dropdown.options[int(self.model_dropdown.value)].text
            flag, msg, tokens = self.cat_gpt.qwen_gpt(self.message_data['qwen'], model_type, record_context)
            last_datetime = self.message_data['qwen'][-1]['datetime']
        else:
            flag, msg, tokens = self.cat_gpt.yuanqi_gpt(self.message_data['yuanqi'], record_context)
            last_datetime = self.message_data['yuanqi'][-1]['datetime']

        last_datetime_obj = datetime.datetime(int(last_datetime[:4]), int(last_datetime[5:7]),
                                              int(last_datetime[8:10]), int(last_datetime[11:13]),
                                              int(last_datetime[14:16]), int(last_datetime[17:19]))
        continuous = False if (datetime_obj - last_datetime_obj).seconds > 300 else True
        message = {'datetime': now_datetime, 'content': msg, 'continuous': continuous,
                   'role': 'assistant' if flag else 'system', 'token_count': tokens}

        results = self.generate_message_view(message, True)
        # 判断是否在等待回复过程中切换聊天机器人，如果发生切换就不显示消息在listview中，系统消息不做保存
        if gpt_type == 'qwen':
            self.qwen_controls.extend(results)
            if flag:
                self.message_data['qwen'].append(message)
            if self.qwen_chat.shadow:
                self.list_view.controls.extend(results)
        else:
            self.yuanqi_controls.extend(results)
            if flag:
                self.message_data['yuanqi'].append(message)
            if self.yuanqi_chat.shadow:
                self.list_view.controls.extend(results)

        self.send_btn.disabled = False
        self.update()
        if len(self.message_data['qwen']) > 200:
            self.message_data['qwen'] = self.message_data['qwen'][-200:]
        if len(self.message_data['yuanqi']) > 200:
            self.message_data['yuanqi'] = self.message_data['qwen'][-200:]
        with open(Setting.gpt_message_path, 'wb') as f:
            pickle.dump(self.message_data, f)

    def clean_context_clicked(self, e: ft.ControlEvent):
        """清除上下文按钮被点击的事件"""
        dialog = ft.AlertDialog(modal=False, open=True, title=ft.Text('清除聊天记录？', color=ft.colors.PRIMARY),
                                content=ft.Text('此操作将清除当前的聊天记录，是否继续？'),
                                actions=[ft.TextButton('清除', on_click=self.clean_context),
                                         ft.TextButton('取消', on_click=self.dialog_close)],
                                on_dismiss=self.dialog_close)
        self.page.overlay.append(dialog)
        self.page.update()

    def clean_context(self, e: ft.ControlEvent):
        """确定清除上下文的事件"""
        now_datetime = str(datetime.datetime.now())[:19]
        if self.qwen_chat.shadow:
            message = {'datetime': now_datetime, 'content': '您好！有什么可以帮助您的吗？', 'continuous': False,
                       'role': 'assistant', 'token_count': 0}
            self.message_data['qwen'] = [message]
            self.qwen_controls = self.generate_message_view(message)
            self.list_view.controls = self.qwen_controls
        else:
            message = {'datetime': now_datetime, 'content': '你好，有什么想和我说的吗~', 'continuous': False,
                       'role': 'assistant', 'token_count': 0}
            self.message_data['yuanqi'] = [message]
            self.yuanqi_controls = self.generate_message_view(message)
            self.list_view.controls = self.yuanqi_controls

        with open(Setting.gpt_message_path, 'wb') as f:
            pickle.dump(self.message_data, f)
        self.dialog_close(e)

    def dialog_close(self, e: ft.ControlEvent):
        """弹窗关闭事件"""
        handle_control = e.control if isinstance(e.control, ft.AlertDialog) else e.control.parent
        if handle_control in self.page.overlay:
            handle_control.open = False
            self.page.update()
            self.page.overlay.remove(handle_control)
