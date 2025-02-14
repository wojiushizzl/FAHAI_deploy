import flet as ft
import time


class LoginDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page):
        """用户登录界面"""
        super().__init__()
        self.page = page
        self.modal = True
        self.open = True
        self.title_padding = ft.Padding(40, 24, 40, 4)
        self.content_padding = ft.Padding(40, 0, 40, 0)

        self._init_widgets()
        self.page.overlay.append(self)
        self.page.update()

    def _init_widgets(self):
        """初始化组件"""
        close_btn = ft.IconButton(icon=ft.icons.CLOSE, icon_size=28, icon_color=ft.colors.SECONDARY,
                                  style=ft.ButtonStyle(bgcolor={'hovered': 'red400'}), tooltip='关闭',
                                  on_click=self.dialog_close)
        self.title_label = ft.Text('用户登录', color=ft.colors.PRIMARY, weight=ft.FontWeight.BOLD, expand=1)
        self.title = ft.Row([self.title_label, close_btn])

        input_width = 360
        self.user_input = ft.TextField(prefix_icon=ft.icons.PERSON, hint_text='请输入用户名', width=input_width,
                                       helper_text=' ', autofocus=True,
                                       input_filter=ft.InputFilter(regex_string=r'^[\w\.@\-]{0,20}$'),
                                       on_focus=self.on_focus_event, on_submit=lambda _: self.pwd_input.focus())
        self.pwd_input = ft.TextField(password=True, can_reveal_password=True, prefix_icon=ft.icons.LOCK,
                                      hint_text='请输入密码', max_length=20, width=input_width,
                                      input_filter=ft.InputFilter(regex_string=r'^[\w\.@\-]{0,20}$'),
                                      on_focus=self.on_focus_event, on_submit=self.login_event)
        self.confirmation_input = ft.TextField(hint_text='请再次输入密码', password=True, can_reveal_password=True,
                                               width=input_width, counter_text=' ',
                                               prefix_icon=ft.icons.VERIFIED_USER, visible=False,
                                               on_focus=self.on_focus_event, on_blur=self.confirmation_input_blur_event)
        self.contact_input = ft.TextField(hint_text='请输入用户绑定的邮箱或电话', prefix_icon=ft.icons.CONTACT_EMERGENCY,
                                          input_filter=ft.InputFilter(regex_string=r'^[\w\.@\-]{0,50}$'), visible=False,
                                          on_focus=self.on_focus_event, helper_text=' ', width=input_width)
        self.verify_input = ft.TextField(hint_text='请输入验证码', prefix_icon=ft.icons.KEY, width=240, helper_text=' ',
                                         input_filter=ft.InputFilter(regex_string=r'^\w{0,8}$'),
                                         on_focus=self.on_focus_event)
        verify_btn = ft.FilledTonalButton(content=ft.Text('发送验证码', size=12), on_click=self.send_verifycode_btn_clicked)
        self.verify_row = ft.Row([self.verify_input, ft.Container(verify_btn, padding=ft.Padding(0, 0, 0, 16))],
                                 visible=False, alignment=ft.MainAxisAlignment.START, width=input_width)

        self.main_btn = ft.ElevatedButton(content=ft.Text('登录', size=18), width=180, height=45, on_click=self.login_event)
        self.register_btn = ft.TextButton(content=ft.Text('创建新的用户', color=ft.colors.SECONDARY), on_click=self.change_register_page)
        self.reset_btn = ft.TextButton(content=ft.Text('忘记密码', color=ft.colors.TERTIARY), on_click=self.change_reset_page)
        self.back_btn = ft.FilledButton('切换至用户登录', on_click=self.back_btn_clicked)
        self.bottom_row = ft.Row([self.register_btn, self.reset_btn], width=input_width, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        right_column = ft.Column([ft.Column(expand=1), self.user_input, self.pwd_input, self.confirmation_input,
                                  self.contact_input, self.verify_row, ft.Column(), self.main_btn, ft.Column(expand=2), self.bottom_row],
                                 horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)

        icon = ft.Icon(ft.icons.PERSON, size=160, color=ft.colors.ON_PRIMARY)
        container = ft.Container(icon, shape=ft.BoxShape.CIRCLE,
                                 shadow=ft.BoxShadow(blur_radius=4, color=ft.colors.SECONDARY),
                                 gradient=ft.RadialGradient(center=ft.Alignment(0, -1), radius=1, colors=[ft.colors.PRIMARY, ft.colors.SECONDARY]))
        status_show = ft.Container()
        label = ft.Text('')
        self.status_show_row = ft.Row([status_show, label])
        text_style = ft.TextStyle(color=ft.colors.PRIMARY, weight=ft.FontWeight.BOLD)
        text_spans = [ft.TextSpan('用户协议', style=text_style, on_click=lambda _: ...),
                      ft.TextSpan('和'),
                      ft.TextSpan('隐私政策', style=text_style, on_click=lambda _: ...)]
        label = ft.Text('登录或完成注册即代表您\n同意', spans=text_spans, size=12)
        left_column = ft.Column([ft.Column(expand=1), container, self.status_show_row, ft.Column(expand=1), label],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=24)

        divider = ft.VerticalDivider(width=1)
        row = ft.Row([left_column, divider, right_column], spacing=32)
        self.content = ft.Container(row, width=584, height=400)

    def dialog_close(self, e: ft.ControlEvent):
        """登录界面关闭触发的事件"""
        self.open = False
        self.page.update()
        self.page.overlay.remove(self)

    def change_register_page(self, e: ft.ControlEvent):
        """切换到用户注册界面"""
        self.clear_helper_error_text()
        self.title_label.value = '用户注册'
        self.main_btn.content.value = '注册'
        self.main_btn.on_click = self.register_event
        self.main_btn.disabled = False

        self.bottom_row.controls[0] = self.back_btn
        self.bottom_row.controls[1] = self.reset_btn

        self.user_input.visible = True
        self.user_input.on_submit = None
        self.pwd_input.visible = True
        self.pwd_input.on_submit = None
        self.confirmation_input.visible = True
        self.contact_input.visible = False
        self.verify_row.visible = False
        self.update()
        self.back_btn.focus()

    def change_reset_page(self, e: ft.ControlEvent):
        """切换到密码重置第一个界面"""
        self.clear_helper_error_text()
        self.title_label.value = '密码重置'
        self.main_btn.content.value = '下一步'
        self.main_btn.on_click = self.reset_next_event
        self.main_btn.disabled = True

        self.bottom_row.controls[0] = self.register_btn
        self.bottom_row.controls[1] = self.back_btn

        self.user_input.visible = True
        self.user_input.on_submit = None
        self.pwd_input.visible = False
        self.pwd_input.on_submit = None
        self.confirmation_input.visible = False
        self.contact_input.visible = True
        self.verify_row.visible = True
        self.update()
        self.back_btn.focus()

    def back_btn_clicked(self, e: ft.ControlEvent):
        """返回登录界面按钮被点击的事件"""
        self.clear_helper_error_text()
        self.title_label.value = '用户登录'
        self.main_btn.content.value = '登录'
        self.main_btn.on_click = self.login_event
        self.main_btn.disabled = False

        self.bottom_row.controls[0] = self.register_btn
        self.bottom_row.controls[1] = self.reset_btn

        self.user_input.visible = True
        self.user_input.on_submit = lambda _: self.pwd_input.focus()
        self.user_input.focus()
        self.pwd_input.visible = True
        self.pwd_input.on_submit = self.login_event
        self.confirmation_input.visible = False
        self.contact_input.visible = False
        self.verify_row.visible = False
        self.update()

    def send_verifycode_btn_clicked(self, e: ft.ControlEvent):
        """发送验证码按钮被点击触发的事件"""
        self.main_btn.disabled = False
        self.main_btn.update()

    @staticmethod
    def on_focus_event(e: ft.ControlEvent):
        """输入框控件获取焦点的事件"""
        e.control.error_text = ''
        e.control.update()

    def confirmation_input_blur_event(self, e: ft.ControlEvent):
        """"密码确认输入框失去焦点的触发事件"""
        pwd = self.pwd_input.value
        pwd2 = self.confirmation_input.value
        if not pwd or not pwd2:
            return
        if pwd != pwd2:
            self.confirmation_input.error_text = '密码输入不一致'
            self.confirmation_input.update()

    def clear_helper_error_text(self):
        """清除输入框的帮助或错误提示信息"""
        self.user_input.error_text = ''
        self.pwd_input.error_text = ''
        self.confirmation_input.error_text = ''
        self.contact_input.error_text = ''
        self.verify_input.error_text = ''

    def login_event(self, e: ft.ControlEvent):
        """用户登录事件"""
        self.clear_helper_error_text()
        user = self.user_input.value
        pwd = self.pwd_input.value

        if len(user) < 4:
            self.user_input.error_text = '用户名称过短'
            self.update()
            return
        if len(pwd) < 6:
            self.pwd_input.error_text = '密码长度过短'
            self.update()
            return

        self.status_show_row.controls[0] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.status_show_row.controls[1].value = '登录确认中，请稍候'
        self.status_show_row.controls[1].color = ft.colors.PRIMARY
        self.update()
        time.sleep(0.5)

        if (user == 'lasifea' or user == 'mein') and pwd == '123456':
            self.status_show_row.controls[0] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
            self.status_show_row.controls[1].value = '登陆成功！'
            self.status_show_row.controls[1].color = ft.colors.PRIMARY
            self.status_show_row.update()
            time.sleep(1)
            self.dialog_close(...)
        else:
            self.status_show_row.controls[0] = ft.Icon(ft.icons.ERROR, size=20, color=ft.colors.ERROR)
            self.status_show_row.controls[1].value = '用户名或密码错误'
            self.status_show_row.controls[1].color = ft.colors.ERROR
            self.status_show_row.update()

    def register_event(self, e: ft.ControlEvent):
        """用户注册事件"""
        self.clear_helper_error_text()
        user = self.user_input.value
        pwd = self.pwd_input.value
        pwd2 = self.confirmation_input.value

        if len(user) < 4:
            self.user_input.error_text = '用户名称过短'
            self.update()
            return
        if len(pwd) < 6:
            self.pwd_input.error_text = '密码长度过短'
            self.update()
            return
        if pwd != pwd2:
            self.confirmation_input.error_text = '密码输入不一致'
            self.update()
            return

        self.status_show_row.controls[0] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.status_show_row.controls[1].value = '操作确认中，请稍候'
        self.status_show_row.controls[1].color = ft.colors.PRIMARY
        self.update()
        time.sleep(0.5)

        self.status_show_row.controls[0] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
        self.status_show_row.controls[1].value = '注册成功！'
        self.status_show_row.controls[1].color = ft.colors.PRIMARY
        self.status_show_row.update()
        time.sleep(1.5)
        self.pwd_input.value = ''
        self.confirmation_input.value = ''
        self.back_btn_clicked(...)

    def reset_next_event(self, e: ft.ControlEvent):
        """切换到密码重置第二个界面"""
        self.clear_helper_error_text()
        user = self.user_input.value
        contact_way = self.contact_input.value
        verifycode = self.verify_input.value

        if len(user) < 4:
            self.user_input.error_text = '用户名称过短'
            self.update()
            return

        self.main_btn.content.value = '重置'
        self.main_btn.on_click = self.reset_final_event

        self.user_input.visible = False
        self.pwd_input.visible = True
        self.confirmation_input.visible = True
        self.contact_input.visible = False
        self.verify_row.visible = False
        self.update()

    def reset_final_event(self, e: ft.ControlEvent):
        """密码重置事件"""
        self.clear_helper_error_text()
        pwd = self.pwd_input.value
        pwd2 = self.confirmation_input.value

        if len(pwd) < 6:
            self.pwd_input.error_text = '密码长度过短'
            self.update()
            return
        if pwd != pwd2:
            self.confirmation_input.error_text = '密码输入不一致'
            self.update()
            return

        self.status_show_row.controls[0] = ft.ProgressRing(width=16, height=16, stroke_width=2)
        self.status_show_row.controls[1].value = '操作确认中，请稍候'
        self.status_show_row.controls[1].color = ft.colors.PRIMARY
        self.update()
        time.sleep(0.5)

        self.status_show_row.controls[0] = ft.Icon(ft.icons.CHECK_CIRCLE, size=20)
        self.status_show_row.controls[1].value = '密码重置成功！'
        self.status_show_row.controls[1].color = ft.colors.PRIMARY
        self.status_show_row.update()
        time.sleep(1.5)
        self.pwd_input.value = ''
        self.confirmation_input.value = ''
        self.back_btn_clicked(...)
