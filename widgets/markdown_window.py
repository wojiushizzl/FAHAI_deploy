import flet as ft


class MarkdownWindow(ft.Container):
    def __init__(self):
        """markdown文件窗口"""
        super().__init__()
        self.expand = 1
        self.alignment = ft.Alignment(-1, -1)
        self.padding = ft.Padding(10, 10, 82, 30)

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        with open('README.md', 'r', encoding='utf-8') as f:
            md_content = f.read()

        markdown = ft.Markdown(md_content, selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                               auto_follow_links=True)
        self.content = ft.Column([markdown], scroll=ft.ScrollMode.AUTO)

