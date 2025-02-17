import flet as ft
from .main_window_widgets import TitleBar, LeftDrawer, RightDrawer, LeftNavigationMenu
from .home_window import HomeWindow
from .interests_window import InterestsWindow
from .data_overview_window import DataOverviewWindow
from .markdown_window import MarkdownWindow
from .setting_window import SettingWindow
from custom_widgets.others import audio_played
from common.app_setting import Setting, CONFIG_OBJ
import asyncio
import os
from random import choice
from typing import Optional


class MainWindow:
    def __init__(self, page: ft.Page):
        """主窗口"""
        self.page = page
        self.page.title = Setting.title
        self.page.padding = 0
        self.page.spacing = 0
        self.page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[ft.Locale('en', 'English'), ft.Locale('zh', 'Chinese')],
            current_locale=ft.Locale('zh', 'Chinese')
        )
        self.page.window.icon = '/images/app.ico'
        self.page.window.title_bar_hidden = True
        self.page.window.opacity = 0.995
        self.page.window.min_width = 900
        self.page.window.min_height = 556
        self.page.window.full_screen = True

        self.title_bar = TitleBar()
        self.page.drawer = LeftDrawer()
        self.page.end_drawer = RightDrawer()
        self.left_menu = LeftNavigationMenu()
        self.home_window = HomeWindow()
        self.interests_window: Optional[InterestsWindow] = None
        self.data_overview_window: Optional[DataOverviewWindow] = None
        self.markdown_window: Optional[MarkdownWindow] = None
        self.setting_window = SettingWindow()

        self._init_widgets()
        self.load_surface()
        self._bind()
        self.page.window.center()
        self.page.run_task(self.open_event)

    def _init_widgets(self):
        """初始化组件"""


        self.content_stack = ft.Stack([self.home_window], alignment=ft.Alignment(0, 0),
                                      fit=ft.StackFit.EXPAND)
        content_widget = ft.Container(margin=ft.Margin(10, 0, 10, 0), expand=1, content=self.content_stack)
        divider = ft.VerticalDivider(1, leading_indent=10, trailing_indent=10)
        self.divider_container = ft.Container(divider, opacity=1, animate_opacity=500)
        row_widgets = ft.Row([self.left_menu, self.divider_container, content_widget],
                             expand=True, spacing=0)

        column = ft.Column([self.title_bar, row_widgets], spacing=0)
        self.window_container = ft.Container(column, image=None, expand=1)
        # 部分子界面需要频繁修改主界面的控件，为子界面创建控件的引用
        self.setting_window.surface_tab.window_container = self.window_container
        self.page.add(self.window_container)
        self.page.floating_action_button = ft.FloatingActionButton(icon=ft.icons.GAMES, opacity=0.4, mini=True,
                                                                   tooltip='Clean Mode', animate_opacity=1000,
                                                                   on_click=self.float_btn_click_event, )
        self.page.floating_action_button_location = 'startFloat'


    def _bind(self):
        """下级控件的事件绑定"""
        self.title_bar.circle_area.controls[1].on_click = self.circle_area_click_event
        self.title_bar.menu_btn.on_click = self.menu_btn_click_event
        self.left_menu.content.controls[1].on_change = self.switch_windows

    def circle_area_click_event(self, e: ft.ControlEvent):
        """标题栏中的头像按钮的点击事件"""
        self.page.drawer.open = True
        self.page.update()

    def menu_btn_click_event(self, e: ft.ControlEvent):
        """标题栏中的菜单按钮的点击事件"""
        self.page.end_drawer.open = True
        self.page.update()

    def switch_windows(self, e: ft.ControlEvent):
        """点击左菜单栏切换窗口"""
        current_window = self.content_stack.controls[0]
        if e.control.selected_index == 0 and current_window != self.home_window:
            self.content_stack.controls[0] = self.home_window
            self.content_stack.update()
        if e.control.selected_index == 1 and current_window != self.interests_window:
            if self.interests_window is None:
                self.interests_window = InterestsWindow()
            self.content_stack.controls[0] = self.interests_window
            self.content_stack.update()
        if e.control.selected_index == 2 and current_window != self.markdown_window:
            if self.markdown_window is None:
                self.markdown_window = MarkdownWindow()
            self.content_stack.controls[0] = self.markdown_window
            self.content_stack.update()
        if e.control.selected_index == 3 and current_window != self.data_overview_window:
            if self.data_overview_window is None:
                self.data_overview_window = DataOverviewWindow()
            self.content_stack.controls[0] = self.data_overview_window
            self.content_stack.update()
        if e.control.selected_index == 4 and current_window != self.setting_window:
            self.content_stack.controls[0] = self.setting_window
            self.content_stack.update()

        # 切换界面触发的特殊事件，如保存设置、释放内存等
        if current_window != self.setting_window:
            self.setting_window.save_config()
        if current_window != self.markdown_window:
            self.markdown_window = None
        if current_window != self.data_overview_window:
            self.data_overview_window = None


    def float_btn_click_event(self, e: ft.ControlEvent):
        """主窗口中浮动按钮的点击事件"""
        if self.page.floating_action_button.opacity == 0.4:
            self.page.floating_action_button.opacity = 0.1
            self.page.floating_action_button.tooltip = 'clean mode'
            self.title_bar.offset = (0, -1)
            self.left_menu.offset = (-1, 0)
            self.divider_container.opacity = 0
            self.page.window.always_on_top = True
        else:
            self.page.floating_action_button.opacity = 0.4
            self.page.floating_action_button.tooltip = 'clean mode'
            self.title_bar.offset = (0, 0)
            self.left_menu.offset = (0, 0)
            self.divider_container.opacity = 1
            self.page.window.always_on_top = False
        self.page.update()

    async def open_event(self):
        """软件启动事件"""
        if os.path.exists(Setting.temp_dir):
            files = os.listdir(Setting.temp_dir)
            for i in files:
                os.remove(f'{Setting.temp_dir}/{i}')

        user_data_dir = f"{os.getenv('APP_DIR')}/user_data"
        if not os.path.exists(user_data_dir):
            os.mkdir(user_data_dir)

        await asyncio.sleep(0.5)
        audio_played(self.page)
        self.content_stack.update()
        await asyncio.sleep(10)

        self.title_bar.notice_badge.label_visible = False
        self.page.update()

        self.title_bar.notice_badge.label_visible = False
        self.page.update()

    def load_surface(self):
        """程序启动时加载界面外观"""
        font_idx = CONFIG_OBJ['base']['font'] if CONFIG_OBJ.has_option('base', 'font') else Setting.font
        font_idx = int(font_idx)
        if font_idx == 0:
            self.page.theme = ft.Theme(font_family='')
        elif font_idx == 1:
            self.page.fonts = {'my_font': '/fonts/AlibabaPuHuiTi-2-55-Regular.otf'}
            self.page.theme = ft.Theme(font_family='my_font')
        elif font_idx == 2:
            self.page.fonts = {'my_font': '/fonts/DingTalk-JinBuTi.ttf'}
            self.page.theme = ft.Theme(font_family='my_font')
        elif font_idx == 3:
            self.page.fonts = {'my_font': '/fonts/TsangerYuYangT-W02.ttf'}
            self.page.theme = ft.Theme(font_family='my_font')
        else:
            font = self.setting_window.base_tab.font_input.options[font_idx].text
            self.page.theme = ft.Theme(font_family=font)

        theme_idx = CONFIG_OBJ['surface']['theme'] if CONFIG_OBJ.has_option('surface', 'theme') else Setting.theme
        theme_idx = int(theme_idx)
        if theme_idx == 0:
            colors = [i.content.controls[0].color for i in self.setting_window.surface_tab.theme_input.options]
            colors.append(None)
            theme = choice(colors)
        elif theme_idx == 1:
            theme = None
        else:
            theme = self.setting_window.surface_tab.theme_input.options[theme_idx].content.controls[0].color

        self.page.theme.color_scheme_seed = theme
        bg_image_obj = CONFIG_OBJ.getint('surface', 'bg_image_idx') if CONFIG_OBJ.has_option('surface', 'bg_image_idx') else Setting.bg_image_idx
        if bg_image_obj == 4:
            bg_image_obj = CONFIG_OBJ['surface']['bg_image_path']
        image_opacity = CONFIG_OBJ.getfloat('surface', 'bg_image_opacity') if CONFIG_OBJ.has_option('surface', 'bg_image_opacity') else Setting.bg_image_opacity
        self.setting_window.surface_tab.load_bg_image(bg_image_obj, image_opacity, self.page)
