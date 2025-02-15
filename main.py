import os

app_dir = os.path.dirname(__file__)
os.chdir(app_dir)
os.environ['APP_DIR'] = app_dir
print(app_dir)

import flet as ft
from widgets.main_window import MainWindow
from common.app_setting import Setting
from argparse import ArgumentParser


def main():
    """软件启动主函数"""
    font_color = '\033[1;32m'
    parse = ArgumentParser(description=f'\033[1;36m{Setting.title}\33[0m')
    parse.add_argument('--web', action='store_true', help=f'{font_color}使用浏览器后台启动\33[0m')
    parse.add_argument('--host', default='localhost', metavar='',
                       help=f'{font_color}设置可以访问的IP地址，默认为localhost，仅在本地运行，如需开放给其它用户使用，指定参数为0.0.0.0\33[0m')
    parse.add_argument('-p', '--port', type=int, default=5200, metavar='', help=f'{font_color}设置后台启动的端口号，默认端口5200\33[0m')
    args = parse.parse_args()

    if args.web:
        assert 1024 < args.port <= 65535, '端口号必须在(1024, 65535]之间'
        host = '0.0.0.0' if args.host == '0.0.0.0' else '127.0.0.1'
        os.environ['FLET_SECRET_KEY'] = 'zzl'
        ft.app(MainWindow, name=Setting.title, view=ft.AppView.WEB_BROWSER, port=args.port, host=host,
               use_color_emoji=True, web_renderer=ft.WebRenderer.CANVAS_KIT, upload_dir=Setting.upload_dir,
               assets_dir=f'{app_dir}/assets')
    else:
        ft.app(MainWindow, name=Setting.title, assets_dir=f'{app_dir}/assets')


if __name__ == '__main__':
    main()
