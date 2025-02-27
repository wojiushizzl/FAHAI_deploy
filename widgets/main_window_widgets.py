import flet as ft
from custom_widgets.message_dialog import MessageDialog
from custom_widgets.login_dialog import LoginDialog
from custom_widgets.others import audio_played
from common.app_setting import Setting
from math import pi
import time
import os
from random import choice
from typing import Optional


class TitleBar(ft.Container):
    def __init__(self):
        """顶部标题栏组件"""
        super().__init__()
        self.padding = ft.Padding(15, 1, 1, 0)
        self.offset = ft.transform.Offset(0, 0)
        self.animate_offset = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT_CUBIC)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        icon_size = 16

        user_icon = ft.Image(src=r'/images/me.jpg', width=48, height=48, border_radius=24)
        current_state = ft.Container(ft.CircleAvatar(bgcolor=ft.colors.GREEN, radius=6),
                                     alignment=ft.alignment.bottom_left, tooltip='User')
        self.circle_area = ft.Stack([user_icon, current_state], width=48, height=48)
        self.info_area = ft.Container(ft.Column([ft.Text('欢迎您，Admin！', color=ft.colors.PRIMARY),
                                                 ft.Text('Online', size=12)], spacing=0), margin=ft.Margin(5, 0, 0, 0))

        self.drag_area = ft.WindowDragArea(
            ft.Container(ft.Text('', text_align=ft.TextAlign.CENTER, size=18), padding=10, margin=ft.Margin(0, 0, 40, 0)),
            expand=1, maximizable=True)
    
        self.notice_badge = ft.Badge(ft.IconButton(ft.icons.NOTIFICATIONS_OUTLINED, tooltip='通知', icon_size=icon_size,
                                                   icon_color=ft.colors.SECONDARY, on_click=self.notice_btn_event,
                                                   rotate=0, animate_rotation=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT_CUBIC)),
                                    #  alignment=ft.Alignment(1, 1), text='99+', bgcolor=ft.colors.RED_300, offset=(0, -12)
                                     )
        theme_btn = ft.IconButton(ft.icons.BRIGHTNESS_2_OUTLINED, on_click=self.theme_btn_event, tooltip='夜间模式',
                                  icon_size=icon_size, icon_color=ft.colors.SECONDARY)
        self.menu_btn = ft.IconButton(ft.icons.MENU, tooltip='更多内容', icon_size=icon_size,
                                      icon_color=ft.colors.SECONDARY)
        minimize_btn = ft.IconButton(ft.icons.REMOVE, on_click=self.minimize_btn_event, tooltip='最小化',
                                     icon_size=icon_size, icon_color=ft.colors.SECONDARY)
        maximize_btn = ft.IconButton(ft.icons.CROP_SQUARE, on_click=self.maximize_btn_event, tooltip='最大化',
                                     icon_size=icon_size, icon_color=ft.colors.SECONDARY)
        close_btn = ft.IconButton(ft.icons.CLOSE, on_click=lambda _: self.page.window.close(),
                                  tooltip='关闭', icon_size=icon_size,
                                  style=ft.ButtonStyle(color={'hovered': 'onprimary', '': 'secondary'},
                                                       bgcolor={'hovered': 'red400'},
                                                       shape=ft.RoundedRectangleBorder(8)))
        row = ft.Row([self.circle_area, self.info_area, self.drag_area, self.notice_badge, theme_btn,
                      self.menu_btn, minimize_btn, maximize_btn, close_btn], spacing=4)
        self.content = ft.Column([row, ft.Divider(height=1, trailing_indent=15)], spacing=4)





    def notice_btn_event(self, e: ft.ControlEvent):
        """标题栏中通知按钮的点击事件"""
        audio_played(self.page, '/sounds/bell.wav')
        e.control.rotate += pi / 9
        self.notice_badge.update()
        time.sleep(0.1)
        e.control.rotate -= pi / 9
        self.notice_badge.update()
        time.sleep(0.1)
        e.control.rotate -= pi / 9
        self.notice_badge.update()
        time.sleep(0.1)
        e.control.rotate += pi / 9
        self.notice_badge.update()
        MessageDialog(self.page, Setting.notice_message_path)

    def theme_btn_event(self, e: ft.ControlEvent):
        """标题栏中主题按钮的点击事件"""
        if e.control.icon == ft.icons.BRIGHTNESS_2_OUTLINED:
            e.control.icon = ft.icons.BRIGHTNESS_HIGH
            e.control.tooltip = '白天模式'
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            e.control.icon = ft.icons.BRIGHTNESS_2_OUTLINED
            e.control.tooltip = '夜间模式'
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.update()

    def minimize_btn_event(self, e: ft.ControlEvent):
        """标题栏中最小化按钮事件"""
        self.page.window.minimized = True
        self.page.update()

    def maximize_btn_event(self, e: ft.ControlEvent):
        """标题栏中最大化按钮事件"""
        if self.page.window.maximized:
            self.page.window.maximized = False
            e.control.tooltip = '最大化'
            e.control.icon = ft.icons.CROP_SQUARE
        else:
            self.page.window.maximized = True
            e.control.icon = ft.icons.LAYERS_OUTLINED
            e.control.tooltip = '向下还原'
        self.page.update()


class LeftDrawer(ft.NavigationDrawer):
    def __init__(self):
        """左侧抽屉组件"""
        super().__init__()

        self._init_widgets()
        self.on_change = self.widget_click_event

    def _init_widgets(self):
        """初始化组件"""
        list_title = ft.ListTile(leading=ft.Image(src=r'/images/me.jpg', height=48,
                                                  filter_quality=ft.FilterQuality.MEDIUM, border_radius=24),
                                 title=ft.Text('Admin'), content_padding=0)
        leading_widget = ft.NavigationDrawerDestination(icon_content=list_title)
        switch_widget = ft.NavigationDrawerDestination(icon=ft.icons.SWITCH_ACCOUNT_OUTLINED,
                                                       selected_icon=ft.icons.SWITCH_ACCOUNT, label='账号切换')
        logout_widget = ft.NavigationDrawerDestination(icon=ft.icons.LOGOUT, label='退出登录')
        self.controls = [leading_widget, ft.Divider(), ft.Divider(),
                         switch_widget, logout_widget]

    def widget_click_event(self, e: ft.ControlEvent):
        """左侧抽屉组件的点击事件"""
        if self.selected_index == 3:
            self.open = False
            LoginDialog(self.page)


class RightDrawer(ft.NavigationDrawer):
    def __init__(self):
        """右侧抽屉组件"""
        super().__init__()
        self.position = ft.NavigationDrawerPosition.END

        self._init_widgets()
        self.on_change = self.widget_click_event

    def _init_widgets(self):
        """初始化组件"""


        contact_widget = ft.NavigationDrawerDestination(
            '联系我们', icon=ft.icons.CONTACTS_OUTLINED, selected_icon=ft.icons.CONTACTS)
        exit_widget = ft.NavigationDrawerDestination(
            '退出', icon=ft.icons.EXIT_TO_APP, selected_icon=ft.icons.EXIT_TO_APP)
        self.controls = [ft.Divider(), contact_widget, ft.Divider(), exit_widget]

    def widget_click_event(self, e: ft.ControlEvent):
        """组件点击事件"""


        if self.selected_index == 0:
            #弹出信息框 TODO
            pass

        if self.selected_index == 1:
            self.page.window.close()


class LeftNavigationMenu(ft.Container):
    def __init__(self):
        """左侧菜单栏"""
        super().__init__()
        self.padding = ft.Padding(0, 15, 0, 0)
        self.width = 72
        self.offset = (0, 0)
        self.animate_offset = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT_CUBIC)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        leading_btn = ft.FloatingActionButton(icon=ft.icons.LAYERS, tooltip='隐藏内容', mini=True,
                                              on_click=self.leading_btn_click_event)
        self.page_btns = [
            ft.NavigationRailDestination(icon=ft.icons.HOME_OUTLINED, selected_icon=ft.icons.HOME, label='首页'),
            ft.NavigationRailDestination(icon=ft.icons.INTERESTS_OUTLINED, selected_icon=ft.icons.INTERESTS,
                                         label='部署管理'),
            ft.NavigationRailDestination(icon=ft.icons.INSERT_DRIVE_FILE_OUTLINED,
                                         selected_icon=ft.icons.INSERT_DRIVE_FILE, label='使用文档'),
            ft.NavigationRailDestination(icon=ft.icons.INSERT_CHART_OUTLINED, selected_icon=ft.icons.INSERT_CHART,
                                         label='系统日志'),
            ft.NavigationRailDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label='设置')
        ]
        navigation_rail = ft.NavigationRail(leading=None, destinations=self.page_btns, selected_index=0, height=360,
                                            animate_size=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT_CUBIC),
                                            bgcolor=ft.colors.TRANSPARENT)
        self.content = ft.Column([leading_btn, navigation_rail, ft.Column(expand=1)],
                                 horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)

    def leading_btn_click_event(self, e: ft.ControlEvent):
        """顶部按钮的点击事件"""
        if self.content.controls[1].height > 100:
            e.control.icon = ft.icons.LAYERS_OUTLINED
            e.control.tooltip = '显示更多内容'
            self.content.controls[1].height = 0
        else:
            e.control.icon = ft.icons.LAYERS
            e.control.tooltip = '隐藏内容'
            self.content.controls[1].height = 360

        self.update()
