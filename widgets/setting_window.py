import time
import flet as ft
import os
from common.app_setting import Setting, CONFIG_OBJ
from PIL import Image
from random import choice
from base64 import b64encode
from threading import Thread
from typing import List, Optional, Union


class SettingWindow(ft.Container):
    def __init__(self):
        """设置窗口界面"""
        super().__init__()
        self.expand = 1
        self.padding = ft.Padding(10, 0, 82, 30)

        self._init_widgets()
        self._bind()

    def _init_widgets(self):
        """初始化组件"""
        self.base_tab = BaseTab()
        self.surface_tab = SurfaceTab()
        self.function_tab = FunctionTab()
        # self.shortcut_tab = ShortcutTab()
        tab_widget = ft.Tabs(tabs=[
            self.base_tab, 
            self.surface_tab, 
            self.function_tab, 
            # self.shortcut_tab
            ],
                             animation_duration=300, tab_alignment=ft.TabAlignment.CENTER, expand=1)
        self.content = tab_widget

    def _bind(self):
        """下级控件的事件绑定"""
        self.base_tab.reset_btn.on_click = self.reset_btn_clicked

    def save_config(self):
        """保存配置文件"""
        CONFIG_OBJ['base']['language'] = self.base_tab.language_input.value
        CONFIG_OBJ['base']['font'] = self.base_tab.font_input.value

        CONFIG_OBJ['surface']['theme'] = self.surface_tab.theme_input.value
        bg_image_idx = 0
        for idx, i in enumerate(self.surface_tab.card_row2.controls[1:]):
            if isinstance(i.padding, int) and i.padding > 0:
                bg_image_idx = idx
                break
        CONFIG_OBJ['surface']['bg_image_idx'] = str(bg_image_idx)
        bg_image_path = self.surface_tab.card_row2.controls[-1].data
        CONFIG_OBJ['surface']['bg_image_path'] = bg_image_path if bg_image_path else ''
        CONFIG_OBJ['surface']['bg_image_opacity'] = str(self.surface_tab.image_opacity_slider.value / 100)

        CONFIG_OBJ['function']['thread'] = str(self.function_tab.thread_slider.value)
        CONFIG_OBJ['function']['use_gpu'] = str(self.function_tab.use_gpu_switch.value)
 


        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)

    def reset_config(self, e: ft.ControlEvent):
        """初始化设置"""
        self.base_tab.language_input.value = Setting.language
        self.base_tab.font_input.value = Setting.font

        self.surface_tab.theme_input.value = Setting.theme
        if len(self.surface_tab.card_row2.controls) >= 6:
            self.surface_tab.card_row2.controls.pop()
            os.remove(Setting.bg_image_192_path)
        for i in self.surface_tab.card_row2.controls[1:]:
            i.border = None
            i.padding = 0
        self.surface_tab.card_row2.controls[1].border = ft.border.all(1, ft.colors.SECONDARY)
        self.surface_tab.card_row2.controls[1+Setting.bg_image_idx].border = ft.border.all(2, ft.colors.PRIMARY)
        self.surface_tab.card_row2.controls[1 + Setting.bg_image_idx].padding = 2
        image_opacity = int(Setting.bg_image_opacity * 100)
        self.surface_tab.image_opacity_slider.value = image_opacity
        self.surface_tab.image_opacity_label.value = str(image_opacity)

        self.function_tab.thread_slider.value = Setting.thread
        self.function_tab.thread_label.value = str(Setting.thread)
        self.function_tab.use_gpu_switch.value = Setting.use_gpu


        self.save_config()
        self.surface_tab.theme_change_event(...)
        self.base_tab.font_change_event(...)
        self.surface_tab.load_bg_image(Setting.bg_image_idx, Setting.bg_image_opacity, self.page)
        self.dialog_close(e)

    def reset_btn_clicked(self, e: ft.ControlEvent):
        """初始化配置"""
        dialog = ft.AlertDialog(modal=False, open=True, title=ft.Text('重置设置？', color=ft.colors.PRIMARY),
                                content=ft.Text('此操作将会更改所有设置项为初始值，是否确定更改？'),
                                actions=[ft.TextButton('重置', on_click=self.reset_config),
                                         ft.TextButton('取消', on_click=self.dialog_close)],
                                on_dismiss=self.dialog_close)
        self.page.overlay.append(dialog)
        self.page.update()

    def dialog_close(self, e: ft.ControlEvent):
        """弹窗关闭事件"""
        handle_control = e.control if isinstance(e.control, ft.AlertDialog) else e.control.parent
        if handle_control in self.page.overlay:
            handle_control.open = False
            self.page.update()
            self.page.overlay.remove(handle_control)


class BaseTab(ft.Tab):
    def __init__(self):
        """常规设置页面"""
        super().__init__()
        self.text = '常规'
        self.icon = ft.icons.AUTO_FIX_NORMAL

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        card_label = ft.Text('语言与字体', size=15)
        language_idx = CONFIG_OBJ['base']['language'] if CONFIG_OBJ.has_option('base', 'language') else Setting.language
        self.language_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', '中文（简体）'),
            ft.dropdown.Option('1', 'English')
        ], dense=True, text_size=14, expand=1, value=language_idx)
        row = ft.Row([ft.Text('选择语言 (language)', size=14, expand=2), self.language_input])

        font_idx = CONFIG_OBJ['base']['font'] if CONFIG_OBJ.has_option('base', 'font') else Setting.font
        self.font_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', '系统默认'),
            ft.dropdown.Option('1', '阿里普惠'),
            ft.dropdown.Option('2', '钉钉进步体'),
            ft.dropdown.Option('3', '站酷仓耳渔阳体'),
            ft.dropdown.Option('4', '微软雅黑'),
            ft.dropdown.Option('5', '等线'),
            ft.dropdown.Option('6', '仿宋'),
            ft.dropdown.Option('7', '黑体'),
            ft.dropdown.Option('8', '楷体'),
            ft.dropdown.Option('9', '宋体'),
            ft.dropdown.Option('10', '新宋体')
        ], dense=True, text_size=14, expand=1, value=font_idx, on_change=self.font_change_event)
        row2 = ft.Row([ft.Text('更换字体', size=14, expand=2), self.font_input])
        card_content = ft.Container(ft.Column([row, row2], spacing=20), padding=20)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))

        final_card_label = ft.Text('全局设置', size=15)
        self.reset_btn = ft.TextButton(content=ft.Text('初始化全部设置', color=ft.colors.TERTIARY))
        status_show = ft.Container()

        label = ft.Text('', size=12, width=100)
        label2 = ft.Text('', size=12, width=100, color=ft.colors.GREY)
        column = ft.Column([label, label2], spacing=0)
        self.update_btn = ft.ElevatedButton('检查更新', on_click=self.update_btn_clicked)
        self.final_card_row = ft.Row([self.reset_btn, ft.Row(expand=1), status_show, column, self.update_btn])
        card_content = ft.Container(self.final_card_row, padding=20)
        final_card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))

        column = ft.Column([card_label, card, final_card_label, final_card], width=720, spacing=12)
        tab_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))
        self.content = ft.Column([tab_container], scroll=ft.ScrollMode.AUTO)

    def font_change_event(self, e: ft.ControlEvent):
        """字体改变事件"""
        idx = int(self.font_input.value)
        if idx == 0:
            self.page.theme.font_family = ''
        elif idx == 1:
            self.page.fonts = {'font_a': '/fonts/AlibabaPuHuiTi-2-55-Regular.otf'}
            self.page.theme.font_family = 'font_a'
        elif idx == 2:
            self.page.fonts = {'font_b': '/fonts/DingTalk-JinBuTi.ttf'}
            self.page.theme.font_family = 'font_b'
        elif idx == 3:
            self.page.fonts = {'font_c': '/fonts/TsangerYuYangT-W02.ttf'}
            self.page.theme.font_family = 'font_c'
        else:
            self.page.theme.font_family = self.font_input.options[idx].text
        self.page.update()

    def update_btn_clicked(self, e: ft.ControlEvent):
        """检查更新按钮被点击的事件"""
        Thread(target=self.update_event, daemon=True).start()

    def update_event(self):
        """开启额外线程检查更新"""
        self.final_card_row.controls[2] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.final_card_row.controls[3].controls[0].value = '正在检查更新'
        self.final_card_row.controls[3].controls[1].value = f'版本 {Setting.version}'
        self.update_btn.disabled = True
        self.final_card_row.update()
        # 检查更新 TODO
        time.sleep(0.5)
        self.final_card_row.controls[2] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
        self.final_card_row.controls[3].controls[0].value = 'APP 已是最新版本'
        self.update_btn.disabled = False
        self.final_card_row.update()


class SurfaceTab(ft.Tab):
    def __init__(self):
        """外观设置页面"""
        super().__init__()
        self.text = '外观'
        self.icon = ft.icons.FACE_RETOUCHING_NATURAL

        # 主窗口的背景图像控件的引用
        self.window_container: Optional[ft.Container] = None
        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        card_label = ft.Text('外观', size=15)
        theme_idx = CONFIG_OBJ['surface']['theme'] if CONFIG_OBJ.has_option('surface', 'theme') else Setting.theme
        self.theme_input = ft.Dropdown(options=[
            ft.dropdown.Option('0', content=ft.Row([ft.Icon('palette', color='primary'), ft.Text('随机')], spacing=15)),
            ft.dropdown.Option('1', content=ft.Row([ft.Icon('palette', color='blue200'), ft.Text('经典蓝')], spacing=15)),
            ft.dropdown.Option('2', content=ft.Row([ft.Icon('palette', color='red200'), ft.Text('夕阳红')], spacing=15)),
            ft.dropdown.Option('3', content=ft.Row([ft.Icon('palette', color='orange200'), ft.Text('蜜橘橙')], spacing=15)),
            ft.dropdown.Option('4', content=ft.Row([ft.Icon('palette', color='yellow200'), ft.Text('柠檬黄')], spacing=15)),
            ft.dropdown.Option('5', content=ft.Row([ft.Icon('palette', color='green50'), ft.Text('草绿')], spacing=15)),
            ft.dropdown.Option('6', content=ft.Row([ft.Icon('palette', color='cyan200'), ft.Text('海洋蓝')], spacing=15)),
            ft.dropdown.Option('7', content=ft.Row([ft.Icon('palette', color='purple100'), ft.Text('紫罗兰')], spacing=15)),
            ft.dropdown.Option('8', content=ft.Row([ft.Icon('palette', color='pink200'), ft.Text('少女粉')], spacing=15)),
            ft.dropdown.Option('9', content=ft.Row([ft.Icon('palette', color='yellow50'), ft.Text('酸橙绿')], spacing=15))
        ], dense=True, text_size=14, expand=1, value=theme_idx, on_change=self.theme_change_event)
        row = ft.Row([ft.Text('主题色', size=14, expand=2), self.theme_input])

        label = ft.Text('背景图像', size=14, expand=1)
        self.card_row2 = ft.Row([label], spacing=4)
        self.card_row2.controls.extend(self.generate_bg_image())

        btn_style = ft.ButtonStyle(side=ft.BorderSide(width=1, color=ft.colors.PRIMARY), padding=ft.Padding(32, 4, 32, 4))
        choose_image_btn = ft.OutlinedButton(content=ft.Text('浏览照片', size=12), style=btn_style,
                                             on_click=self.choose_image_btn_clicked)
        row3 = ft.Row([ft.Text('选择一张照片', size=14, expand=1), choose_image_btn])

        label = ft.Text('图像不透明度', size=14, expand=1)
        image_opacity = CONFIG_OBJ.getfloat('surface', 'bg_image_opacity') if CONFIG_OBJ.has_option('surface', 'bg_image_opacity') else Setting.bg_image_opacity
        image_opacity = int(image_opacity * 100)
        self.image_opacity_slider = ft.Slider(image_opacity, min=0, max=100, divisions=100, expand=2, label='{value}',
                                              interaction=ft.SliderInteraction.SLIDE_THUMB,
                                              on_change=self.image_opacity_changed)
        self.image_opacity_label = ft.Text(str(image_opacity), size=16, weight=ft.FontWeight.BOLD, width=30)
        row4 = ft.Row([label, self.image_opacity_slider, self.image_opacity_label], spacing=0)
        card_content = ft.Container(ft.Column([row, self.card_row2, row3, row4], spacing=20), padding=20)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))

        column = ft.Column([card_label, card], width=720, spacing=12)
        tab_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))
        self.content = ft.Column([tab_container], scroll=ft.ScrollMode.AUTO)

    def generate_bg_image(self) -> List[ft.Container]:
        """生成多个背景图像展示"""
        box_side = 96
        bg_img = ft.Container(ft.Icon(ft.icons.DO_DISTURB), width=box_side, height=box_side, border_radius=4,
                              border=ft.border.all(1, ft.colors.SECONDARY), on_click=self.bg_image_changed)
        bg_img2 = ft.Container(ft.Image('/images/bg_192.jpg'), width=box_side, height=box_side, border_radius=4,
                               on_click=self.bg_image_changed)
        bg_img3 = ft.Container(ft.Image('/images/bg2_192.jpg'), width=box_side, height=box_side, border_radius=4,
                               on_click=self.bg_image_changed)
        bg_img4 = ft.Container(ft.Image('/images/bg3_192.jpg'), width=box_side, height=box_side, border_radius=4,
                               on_click=self.bg_image_changed)
        bg_images = [bg_img, bg_img2, bg_img3, bg_img4]

        bg_image_idx = CONFIG_OBJ.getint('surface', 'bg_image_idx') if CONFIG_OBJ.has_option('surface', 'bg_image_idx') else Setting.bg_image_idx
        bg_image_path = CONFIG_OBJ['surface']['bg_image_path'] if CONFIG_OBJ.has_option('surface', 'bg_image_path') else Setting.bg_image_path
        if os.path.exists(Setting.bg_image_192_path):
            with open(Setting.bg_image_192_path, 'rb') as f:
                img_data = f.read()
            img_b64 = b64encode(img_data).decode('utf-8')
            bg_img5 = ft.Container(ft.Image(src_base64=img_b64), width=box_side, height=box_side, border_radius=4,
                                   on_click=self.bg_image_changed, data=bg_image_path)
            bg_images.append(bg_img5)

        bg_images[bg_image_idx].border = ft.border.all(2, ft.colors.PRIMARY)
        bg_images[bg_image_idx].padding = 2
        return bg_images

    def theme_change_event(self, e: ft.ControlEvent):
        """主题色改变事件"""
        idx = int(self.theme_input.value)
        if idx == 0:
            colors = [i.content.controls[0].color for i in self.theme_input.options]
            colors.append(None)
            self.page.theme.color_scheme_seed = choice(colors)
        elif idx == 1:
            self.page.theme.color_scheme_seed = None
        else:
            self.page.theme.color_scheme_seed = self.theme_input.options[idx].content.controls[0].color
        self.page.update()

    def bg_image_changed(self, e: ft.ControlEvent):
        """根据容器的padding属性判断当前选择的背景图"""
        bg_image_obj = 0
        for idx, i in enumerate(self.card_row2.controls[1:]):
            if e.control == i:
                bg_image_obj = idx
            i.border = None
            i.padding = 0

        if bg_image_obj == 4:
            bg_image_obj = self.card_row2.controls[-1].data
        self.card_row2.controls[1].border = ft.border.all(1, ft.colors.SECONDARY)
        e.control.border = ft.border.all(2, ft.colors.PRIMARY)
        e.control.padding = 2
        self.card_row2.update()
        time.sleep(0.3)

        image_opacity = self.image_opacity_slider.value / 100
        self.load_bg_image(bg_image_obj, image_opacity, self.page)
        self.page.update()

    def image_opacity_changed(self, e: ft.ControlEvent):
        """外观设置中改变背景图像不透明度的事件"""
        if self.window_container.image is not None:
            self.window_container.image.opacity = e.control.value / 100
        self.image_opacity_label.value = str(int(e.control.value))
        self.page.update()

    def load_bg_image(self, bg_image_obj: Union[int, str], image_opacity: float, page: ft.Page):
        """
        加载软件界面的背景图
        :param bg_image_obj: 系统自带的背景图像（int）或用户自定义背景图像（str）
        :param image_opacity: 背景图像的不透明度
        :param page: 主页面控件
        :return:
        """
        if bg_image_obj == 0:
            self.window_container.image = None
            return
        elif bg_image_obj == 1:
            img_path = 'assets/images/bg_full.jpg'
        elif bg_image_obj == 2:
            img_path = 'assets/images/bg2_full.jpg'
        elif bg_image_obj == 3:
            img_path = 'assets/images/bg3_full.jpg'
        else:
            img_path = bg_image_obj

        if not os.path.exists(img_path):
            snack_bar: ft.SnackBar = page.overlay[0]
            snack_bar.content.value = '原图路径不存在😦，请重新选择背景图'
            snack_bar.open = True
            return
        if page.web:
            with open(img_path, 'rb') as f:
                img_data = f.read()
            img_b64 = b64encode(img_data).decode('utf-8')
            window_bg_image = ft.DecorationImage(src_base64=img_b64, opacity=image_opacity, fit=ft.ImageFit.FIT_WIDTH)
        else:
            window_bg_image = ft.DecorationImage(src=img_path, opacity=image_opacity, fit=ft.ImageFit.FIT_WIDTH)

        self.window_container.image = window_bg_image

    def choose_image_btn_clicked(self, e: ft.ControlEvent):
        """选择照片的事件"""
        dialog = ft.FilePicker(on_result=self.pick_image_finished, on_upload=self.upload_image_event)
        self.page.overlay.append(dialog)
        self.page.update()
        dialog.pick_files('选择图片', allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])

    def pick_image_finished(self, e: ft.FilePickerResultEvent):
        """选择图片结束后触发的事件"""
        if e.files is None:
            self.page.overlay.remove(e.control)
            self.page.update()
            return

        if self.page.web:
            upload_way = ft.FilePickerUploadFile(e.files[0].name, self.page.get_upload_url(e.files[0].name, 600))
            e.control.upload([upload_way])
            return

        img_path = e.files[0].path
        self.page.overlay.remove(e.control)
        self.page.update()
        self.add_image(img_path)

    def upload_image_event(self, e: ft.FilePickerUploadEvent):
        """上传图片的事件"""
        if e.progress == 1:
            img_path = f'{Setting.upload_dir}/{e.file_name}'
            self.page.overlay.remove(e.control)
            self.page.update()
            self.add_image(img_path)

    def add_image(self, img_path: str):
        """
        判断图片是否符合要求，并在界面中展示略缩图
        :param img_path: 图片路径
        :return:
        """
        img = Image.open(img_path)
        w, h = img.width, img.height
        if h > w or w < 800:
            snack_bar: ft.SnackBar = self.page.overlay[0]
            snack_bar.content.value = '图片像素宽必须大于高，且宽需大于800px'
            snack_bar.open = True
            self.page.update()
            return

        start_x = (w - h) // 2
        img2 = img.crop((start_x, 0, start_x + h, h)).resize((192, 192))
        if img2.mode != 'RGB':
            img2 = img2.convert('RGB')
        img2.save(Setting.bg_image_192_path)

        with open(Setting.bg_image_192_path, 'rb') as f:
            img_data = f.read()
        img_b64 = b64encode(img_data).decode('utf-8')
        if len(self.card_row2.controls) > 5:
            self.card_row2.controls[5].content.src_base64 = img_b64
            self.card_row2.controls[5].data = img_path
        else:
            bg_image = ft.Container(ft.Image(src_base64=img_b64), width=96, height=96, border_radius=4,
                                    on_click=self.bg_image_changed, data=img_path)
            self.card_row2.controls.append(bg_image)
        self.card_row2.update()
        CONFIG_OBJ['surface']['bg_image_path'] = img_path
        with open('user_data/config.ini', 'w', encoding='utf-8') as f:
            CONFIG_OBJ.write(f)


class FunctionTab(ft.Tab):
    def __init__(self):
        """功能设置页面"""
        super().__init__()
        self.text = '功能'
        self.icon = ft.icons.ATTRACTIONS

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        card_label = ft.Text('图像处理', size=15)
        label = ft.Text('图像功能运行的线程数', size=14, expand=1)
        # thread_count = CONFIG_OBJ.getint('function', 'thread') if CONFIG_OBJ.has_option('function', 'thread') else Setting.thread
        thread_count = CONFIG_OBJ.getfloat('function', 'thread') if CONFIG_OBJ.has_option('function', 'thread') else Setting.thread

        self.thread_slider = ft.Slider(thread_count, min=1, max=10, divisions=9, expand=1, label='{value}',
                                       interaction=ft.SliderInteraction.SLIDE_THUMB, tooltip='视CPU核心数，线程数不总是越多越好',
                                       on_change=self.thread_change_event)
        self.thread_label = ft.Text(str(thread_count), size=16, weight=ft.FontWeight.BOLD, width=30)
        row = ft.Row([label, self.thread_slider, self.thread_label], spacing=0)

        label = ft.Text('使用显卡', size=14)
        tooltip = ft.Tooltip(message='开启后，在耗时的图像功能中使用显卡计算')
        help_icon = ft.Icon('help', color=ft.colors.GREY, size=16, tooltip=tooltip)
        status_show = ft.Container()
        label2 = ft.Text('', size=12, width=110)
        btn_style = ft.ButtonStyle(side=ft.BorderSide(width=1, color=ft.colors.PRIMARY), padding=ft.Padding(12, 4, 12, 4))
        test_gpu_btn = ft.OutlinedButton(content=ft.Text('测试显卡是否可用', size=12), style=btn_style, on_click=self.test_gpu_btn_clicked)
        divider = ft.Container(ft.VerticalDivider(thickness=1), height=30)
        use_gpu = CONFIG_OBJ.getboolean('function', 'use_gpu') if CONFIG_OBJ.has_option('function', 'use_gpu') else Setting.use_gpu
        self.use_gpu_switch = ft.Switch(value=use_gpu, height=40)
        self.card_row2 = ft.Row([label, help_icon, ft.Row(expand=1), status_show, label2, test_gpu_btn, divider, self.use_gpu_switch])
        card_content = ft.Container(ft.Column([row, self.card_row2], spacing=20), padding=20)
        card = ft.Card(card_content, variant=ft.CardVariant.ELEVATED, elevation=2, margin=ft.Margin(0, 0, 0, 12))



        column = ft.Column([card_label, card], width=720, spacing=12)
        tab_container = ft.Container(column, padding=36, alignment=ft.Alignment(0, -1))
        self.content = ft.Column([tab_container], scroll=ft.ScrollMode.AUTO)

    def thread_change_event(self, e: ft.ControlEvent):
        """改变线程数的事件"""
        self.thread_label.value = str(int(e.control.value))
        self.thread_label.update()

    def test_gpu_btn_clicked(self, e: ft.ControlEvent):
        """测试显卡按钮被点击的事件"""
        Thread(target=self.test_gpu_event, daemon=True).start()

    def test_gpu_event(self):
        """开启额外线程测试显卡"""
        self.card_row2.controls[3] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.card_row2.controls[4].value = '测试中，请稍候'
        self.card_row2.controls[5].disabled = True
        self.card_row2.update()

        # 测试显卡是否可用 TODO
        time.sleep(0.5)
        self.card_row2.controls[3] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
        self.card_row2.controls[4].value = '显卡正常使用'
        self.card_row2.controls[5].disabled = False
        self.card_row2.update()


class ShortcutTab(ft.Tab):
    def __init__(self):
        """快捷键设置页面"""
        super().__init__()
        self.text = '快捷键'
        self.icon = ft.icons.KEYBOARD

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        tab_content = ft.Container(ft.Text('这是快捷键设置窗口', size=24, color=ft.colors.PRIMARY), alignment=ft.Alignment(0, 0))
        self.content = tab_content
