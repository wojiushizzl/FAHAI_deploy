import flet as ft
import os
import pickle
import datetime
import time
from typing import List


class MessageDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, message_path: str):
        """
        通知信息界面
        :param page: 主窗口中的page对象
        :param message_path: 通知数据保存的文件路径
        """
        super().__init__()
        self.page = page
        self.modal = False
        self.open = True
        self.on_dismiss = self.dialog_close
        self.actions_padding = ft.Padding(24, 0, 24, 10)
        self.message_type = 'system_messages'
        self.message_idx = 0
        self.message_path = message_path

        self._load_data()
        self._init_widgets()
        self.page.overlay.append(self)
        self.page.update()
        self.update_label_visible()

    def _init_widgets(self):
        """初始化组件"""
        btn_icon = ft.Badge(ft.Icon(ft.icons.OTHER_HOUSES, size=28), alignment=ft.Alignment(1, 1), small_size=8)
        self.system_notice_btn = ft.TextButton(content=ft.Row([btn_icon, ft.Text('系统通知', size=16)]),
                                               width=200, height=50, style=ft.ButtonStyle(color='onprimary', bgcolor='primary'),
                                               on_click=self.notice_btn_clicked)
        btn_icon = ft.Badge(ft.Icon(ft.icons.PERSON_PIN, size=32), alignment=ft.Alignment(1, 1), small_size=8)
        self.user_notice_btn = ft.TextButton(content=ft.Row([btn_icon, ft.Text('用户通知', size=16)]),
                                             width=200, height=50, style=ft.ButtonStyle(color='onsecondarycontainer', bgcolor='transparent'),
                                             on_click=self.notice_btn_clicked)
        btn_icon = ft.Badge(ft.Icon(ft.icons.SPEAKER_NOTES, size=28), alignment=ft.Alignment(1, 1), small_size=8)
        self.service_notice_btn = ft.TextButton(content=ft.Row([btn_icon, ft.Text('服务通知', size=16)]),
                                                width=200, height=50, style=ft.ButtonStyle(color='onsecondarycontainer', bgcolor='transparent'),
                                                on_click=self.notice_btn_clicked)
        menu_container = ft.Container(ft.Column([self.system_notice_btn, self.user_notice_btn, self.service_notice_btn], spacing=10))

        messages = self.message_data.get('system_messages', [])
        message_tiles = self.generate_message_tiles(messages)
        self.message_container = ft.Container(ft.Column(message_tiles, scroll=ft.ScrollMode.AUTO, spacing=0), width=400, alignment=ft.Alignment(0, -1))

        back_btn = ft.IconButton(ft.icons.ARROW_BACK, tooltip='返回消息主界面', on_click=self.back_btn_clicked)
        self.title_label = ft.Text('', expand=1, text_align=ft.TextAlign.CENTER, selectable=True, weight=ft.FontWeight.BOLD, size=16)
        self.collect_menu_item = ft.PopupMenuItem(content=ft.Row([ft.Icon(ft.icons.FAVORITE, color=ft.colors.SECONDARY), ft.Text('收藏')]), on_click=self.collect_btn_clicked)
        self.delete_menu_item = ft.PopupMenuItem(content=ft.Row([ft.Icon(ft.icons.DELETE, color=ft.colors.SECONDARY), ft.Text('删除')]), on_click=self.delete_btn_clicked)
        more_btn = ft.PopupMenuButton(icon=ft.icons.MORE_HORIZ, tooltip='更多操作', items=[self.collect_menu_item, self.delete_menu_item], icon_color=ft.colors.SECONDARY)
        title_bar = ft.Row([back_btn, self.title_label, more_btn])
        self.content_viewer = ft.Text(selectable=True)
        container = ft.Container(ft.Column([self.content_viewer], scroll=ft.ScrollMode.AUTO), padding=20, expand=1)

        self.content_container = ft.Container(ft.Column([title_bar, ft.Divider(height=1), container]), width=400)
        self.content = ft.Container(ft.Row([menu_container, ft.VerticalDivider(width=1), self.message_container], spacing=10), height=400)

        tooltip = ft.Tooltip(message='每种通知最多保留20条消息，请注意及时查收')
        self.actions = [ft.IconButton(ft.icons.HELP, tooltip=tooltip, icon_color=ft.colors.GREY, icon_size=18)]
        self.actions_alignment = ft.MainAxisAlignment.START

    def _load_data(self):
        """从本地文件中导入通知数据"""
        self.message_data = {}
        if not os.path.exists(self.message_path):
            return

        with open(self.message_path, 'rb') as f:
            self.message_data = pickle.load(f)

    def update_label_visible(self):
        """更新左侧通知菜单中的红点显示"""
        flag, flag2, flag3 = False, False, False
        for i in self.message_data.get('system_messages', []):
            if not i['had_reading']:
                flag = True
                break

        for i in self.message_data.get('user_messages', []):
            if not i['had_reading']:
                flag2 = True
                break

        for i in self.message_data.get('service_messages', []):
            if not i['had_reading']:
                flag3 = True
                break

        self.system_notice_btn.content.controls[0].label_visible = flag
        self.user_notice_btn.content.controls[0].label_visible = flag2
        self.service_notice_btn.content.controls[0].label_visible = flag3
        self.update()

    def generate_message_tiles(self, messages: list) -> List[ft.ListTile]:
        """
        将通知信息以ListTile组件展示
        :param messages: 系统通知、用户通知或服务通知的所有信息条目
        :return: ListTile组件组成的列表
        """
        today_obj = datetime.date.today()
        today = str(today_obj)
        message_tiles = []

        for i in messages:
            content = i['content']
            if len(content) > 24:
                content = content[:24].replace('\n', ' ')
                content = f'{content}...'

            publish_time = i['publish_date']
            if publish_time[:10] == today:
                publish_time = publish_time[11:]
            elif (today_obj - datetime.date(int(publish_time[:4]), int(publish_time[5:7]), int(publish_time[8:10]))).days == 1:
                publish_time = '昨天'
            else:
                publish_time = publish_time[5:10]

            title_color = None if i['had_reading'] else ft.colors.PRIMARY
            trailing_text = ft.Text(publish_time)
            trailing_icon = ft.Icon(ft.icons.FAVORITE if i['collected'] else None, size=12, color=ft.colors.SECONDARY)
            trailing = ft.Column([trailing_text, trailing_icon], spacing=5, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END)
            list_tile = ft.ListTile(title=ft.Text(i['title'], weight=ft.FontWeight.BOLD, color=title_color),
                                    subtitle=ft.Text(content, size=12),
                                    trailing=trailing, on_click=self.message_tile_clicked)
            message_tiles.append(list_tile)

        return message_tiles

    def message_tile_clicked(self, e: ft.ControlEvent):
        """信息条目被点击的事件"""
        mes_idx = e.control.parent.controls.index(e.control)
        self.message_idx = mes_idx
        mes_data = self.message_data[self.message_type][self.message_idx]

        self.title_label.value = mes_data['title']
        self.content_viewer.value = mes_data['content']
        if mes_data['collected']:
            self.collect_menu_item.content.controls[0].name = ft.icons.FAVORITE_BORDER
            self.collect_menu_item.content.controls[1].value = '取消收藏'
            self.delete_menu_item.disabled = True
        else:
            self.collect_menu_item.content.controls[0].name = ft.icons.FAVORITE
            self.collect_menu_item.content.controls[1].value = '收藏'
            self.delete_menu_item.disabled = False
        self.content.content.controls[2] = self.content_container

        mes_data['had_reading'] = True
        e.control.title.color = None
        self.update()

    def back_btn_clicked(self, e: ft.ControlEvent):
        """信息内容展示界面中，标题栏的返回按钮被点击的事件"""
        self.content.content.controls[2] = self.message_container
        self.update_label_visible()

    def collect_btn_clicked(self, e: ft.ControlEvent):
        """信息内容展示界面中，标题栏的收藏按钮点击事件"""
        mes_data = self.message_data[self.message_type][self.message_idx]
        mes_data['collected'] = not mes_data['collected']
        mes_tile = self.message_container.content.controls[self.message_idx]
        if mes_data['collected']:
            self.collect_menu_item.content.controls[0].name = ft.icons.FAVORITE_BORDER
            self.collect_menu_item.content.controls[1].value = '取消收藏'
            self.delete_menu_item.disabled = True
            mes_tile.trailing.controls[1].name = ft.icons.FAVORITE
        else:
            self.collect_menu_item.content.controls[0].name = ft.icons.FAVORITE
            self.collect_menu_item.content.controls[1].value = '收藏'
            self.delete_menu_item.disabled = False
            mes_tile.trailing.controls[1].name = None

        time.sleep(0.3)
        self.update()

    def delete_btn_clicked(self, e: ft.ControlEvent):
        """信息内容展示界面中，标题栏的删除按钮点击事件"""
        self.message_data[self.message_type].pop(self.message_idx)
        message_tiles = self.generate_message_tiles(self.message_data[self.message_type])
        self.message_container.content.controls = message_tiles
        self.content.content.controls[2] = self.message_container
        self.update_label_visible()
        # 删除消息后，更新消息数据
        with open(self.message_path, 'wb') as f:
            pickle.dump(self.message_data, f)
        

    def notice_btn_clicked(self, e: ft.ControlEvent):
        """左侧通知按钮被点击的事件"""
        for i in e.control.parent.controls:
            i.style = ft.ButtonStyle(color='onsecondarycontainer', bgcolor='transparent')
        e.control.style = ft.ButtonStyle(color='onprimary', bgcolor='primary')

        if e.control == self.system_notice_btn:
            messages = self.message_data.get('system_messages', [])
            self.message_type = 'system_messages'
        elif e.control == self.user_notice_btn:
            messages = self.message_data.get('user_messages', [])
            self.message_type = 'user_messages'
        else:
            messages = self.message_data.get('service_messages', [])
            self.message_type = 'service_messages'
        message_tiles = self.generate_message_tiles(messages)
        self.message_container.content.controls = message_tiles
        self.content.content.controls[2] = self.message_container
        self.update_label_visible()

    def dialog_close(self, e: ft.ControlEvent):
        """消息通知界面关闭后释放内存并保存消息数据"""
        self.open = False
        self.page.update()
        self.page.overlay.remove(self)
        # with open(self.message_path, 'wb') as f:
        #     pickle.dump(self.message_data, f)
