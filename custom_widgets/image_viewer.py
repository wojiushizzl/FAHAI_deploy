import flet as ft
import os
from PIL import Image
from base64 import b64encode, b64decode


class ImageViewer(ft.Container):
    def __init__(self, only_show: bool = False, save_dir: str = 'downloads', upload_dir: str = 'uploads'):
        """
        图片展示组件，可方便切换图片及取消
        :param only_show: 是否仅展示图片，如果设置为True则无法自定义选择图片
        :param save_dir: 图片的默认保存路径，仅在web端生效
        :param upload_dir: 图片的默认上传路径，仅在web端生效
        """
        super().__init__()
        self.only_show = only_show
        self.save_dir = save_dir
        self.upload_dir = upload_dir
        self.alignment = ft.Alignment(0, 0)
        self.width = 300
        self.height = 400
        self.border = ft.border.all(1, ft.colors.SECONDARY)
        self.border_radius = 5
        self.ink = True
        self.on_hover = self.container_hover_event
        if not self.only_show:
            self.on_click = self.container_click_event
        else:
            self.on_click = lambda _: ...

        self._init_widget()

    def _init_widget(self):
        """初始化组件"""
        self.txt = ft.Text('空空如也~' if self.only_show else '➕点击选择图片', size=16)
        self.content = self.txt

        self.my_image = ft.Image(filter_quality=ft.FilterQuality.MEDIUM)
        self.remove_btn = ft.IconButton(ft.icons.CLOSE, left=0, top=0, icon_size=16, tooltip='取消图像显示',
                                        style=ft.ButtonStyle(color={'hovered': 'primary', '': 'secondary'}),
                                        on_click=self.remove_btn_click_event)
        self.save_btn = ft.IconButton(ft.icons.DOWNLOAD, icon_size=16, bottom=0, right=0, tooltip='保存至本地',
                                      style=ft.ButtonStyle(color={'hovered': 'primary', '': 'secondary'}),
                                      on_click=self.save_btn_click_event)
        self.view_btn = ft.IconButton(ft.icons.REMOVE_RED_EYE, icon_size=16, bottom=0, left=0, tooltip='查看图像',
                                      style=ft.ButtonStyle(color={'hovered': 'primary', '': 'secondary'}),
                                      on_click=self.view_btn_click_event)
        self.image_stack = ft.Stack([self.my_image, self.remove_btn, self.save_btn, self.view_btn],
                                    fit=ft.StackFit.EXPAND, alignment=ft.Alignment(0, 0))

    def container_click_event(self, e: ft.ControlEvent):
        """图片查看器被点击的事件"""
        self.remove_btn.visible = False
        self.save_btn.visible = False
        self.view_btn.visible = False

        dialog = ft.FilePicker(on_result=self.pick_files_finished, on_upload=self.upload_file_event)
        self.page.overlay.append(dialog)
        self.page.update()
        dialog.pick_files('选择图片', allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])

    def container_hover_event(self, e: ft.ControlEvent):
        """鼠标进入或退出图片查看器的事件"""
        if self.content == self.txt:
            return

        if e.data == 'true':
            self.remove_btn.visible = True
            self.save_btn.visible = True
            self.view_btn.visible = True
        else:
            self.remove_btn.visible = False
            self.save_btn.visible = False
            self.view_btn.visible = False
        self.image_stack.update()

    def pick_files_finished(self, e: ft.FilePickerResultEvent):
        """文件选择对话框关闭时触发的事件"""
        if e.files is None:
            self.page.overlay.remove(e.control)
            self.page.update()
            return

        if self.page.web:
            self.my_image.data = f'{self.upload_dir}/{e.files[0].name}'
            upload_way = ft.FilePickerUploadFile(e.files[0].name, self.page.get_upload_url(e.files[0].name, 600))
            e.control.upload([upload_way])
            return

        img_obj = e.files[0]
        self.my_image.src = img_obj.path
        self.my_image.data = img_obj.path
        if self.content == self.txt:
            self.content = self.image_stack

        self.page.overlay.remove(e.control)
        self.page.update()

    def upload_file_event(self, e: ft.FilePickerUploadEvent):
        """文件上传事件"""
        if e.progress == 1:
            with open(self.my_image.data, 'rb') as f:
                img_data = f.read()
            img_b64 = b64encode(img_data).decode('utf-8')
            self.my_image.src_base64 = img_b64
            if self.content == self.txt:
                self.content = self.image_stack

            self.page.overlay.remove(e.control)
            self.page.update()

    def remove_btn_click_event(self, e: ft.ControlEvent):
        """关闭图像按钮的点击事件"""
        self.my_image.src = None
        self.my_image.src_base64 = None
        self.my_image.data = None
        self.content = self.txt
        self.update()

    def save_btn_click_event(self, e: ft.ControlEvent):
        """保存图像按钮的点击事件，如果通过浏览器打开，将保存到设定的save_dir目录下"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        if self.page.web:
            img_data = b64decode(self.my_image.src_base64)
            img_name = os.path.split(self.my_image.data)[1]
            with open(f'{self.save_dir}/{img_name}', 'wb') as f:
                f.write(img_data)
            return

        dialog = ft.FilePicker(on_result=self.save_file_finished)
        self.page.overlay.append(dialog)
        self.page.update()

        img_name = os.path.split(self.my_image.data)[-1]
        li = img_name.rsplit('.', 1)
        img_format = 'jpg' if len(li) == 1 else li[1]
        dialog.save_file('保存图片', file_name=img_name, allowed_extensions=[img_format])

    def save_file_finished(self, e: ft.FilePickerResultEvent):
        """保存文件对话框关闭时触发的事件"""
        save_path = e.path
        if save_path:
            if '.' not in os.path.split(save_path)[1]:
                save_path = f'{save_path}.{e.control.allowed_extensions[0]}'
            if self.my_image.data != save_path:
                with open(self.my_image.data, 'rb') as f, open(save_path, 'wb') as f2:
                    f2.write(f.read())

        self.page.overlay.remove(e.control)
        self.page.update()

    def view_btn_click_event(self, e: ft.ControlEvent):
        """查看图像按钮的点击事件"""
        window_width, window_height = self.page.width, self.page.height
        img = Image.open(self.my_image.data)
        img_width, img_height = img.width, img.height
        fw, fh = window_width / img_width, window_height / img_height
        if fw > fh:
            dialog_height = window_height * 0.8
            dialog_width = img_width / img_height * dialog_height
        else:
            dialog_width = window_width * 0.8
            dialog_height = img_width / img_height * dialog_width

        dialog_content = ft.Image(filter_quality=ft.FilterQuality.MEDIUM)
        interactive_viewer = ft.InteractiveViewer(max_scale=10, width=dialog_width, height=dialog_height,
                                                  content=dialog_content, pan_enabled=True)
        if self.page.web:
            with open(self.my_image.data, 'rb') as f:
                img_data = f.read()
            img_b64 = b64encode(img_data).decode('utf-8')
            dialog_content.src_base64 = img_b64
        else:
            dialog_content.src = self.my_image.data
        dialog = ft.AlertDialog(content=interactive_viewer, shape=ft.RoundedRectangleBorder(),
                                open=True, content_padding=0, actions_padding=0, inset_padding=0, modal=False,
                                on_dismiss=self.dialog_close_event)
        self.page.overlay.append(dialog)
        self.page.update()

    def dialog_close_event(self, e: ft.ControlEvent):
        """图像显示窗口关闭的事件"""
        self.page.overlay.remove(e.control)
        self.page.update()
