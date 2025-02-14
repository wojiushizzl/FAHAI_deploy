import flet as ft


class DataOverviewWindow(ft.Container):
    def __init__(self):
        """数据概览窗口"""
        super().__init__()
        self.expand = True

        self._init_widgets()

    def _init_widgets(self):
        """初始化组件"""
        json_data = {'Python': [23.84, 9.98], 'C++': [10.82, 0.81], 'Java': [9.72, 1.73], 'C': [9.1, -2.34],
                     'C#': [4.87, -2.43], 'JavaScript': [4.61, 1.72], 'Go': [2.17, 1.14], 'SQL': [1.99, 0.37],
                     'VB': [1.96, 0.14], 'Fortran': [1.79, 0.72], 'Others': [29.13, -11.84]}
        max_y = max(json_data[i][0] for i in json_data) // 5 * 5 + 5
        bottom_axis_labels, bar_groups = [], []
        for idx, i in enumerate(json_data):
            bottom_axis_label = ft.ChartAxisLabel(value=idx, label=ft.Text(i))
            bottom_axis_labels.append(bottom_axis_label)

            if json_data[i][1] > 0:
                tooltip = f'{json_data[i][0]}%\n对比去年+{json_data[i][1]}%'
                bar_rod2 = ft.BarChartRod(from_y=json_data[i][0] - json_data[i][1], to_y=json_data[i][0],
                                          color=ft.colors.GREEN_300, tooltip=None, width=24, border_radius=1)
            else:
                tooltip = f'{json_data[i][0]}%\n对比去年{json_data[i][1]}%'
                bar_rod2 = ft.BarChartRod(from_y=json_data[i][0] + json_data[i][1], to_y=json_data[i][0],
                                          color=ft.colors.RED_300, tooltip=None, width=24, border_radius=1)
            bar_rods = [ft.BarChartRod(from_y=0, to_y=json_data[i][0], tooltip=None, width=24, border_radius=1),
                        bar_rod2]
            bar_group = ft.BarChartGroup(x=idx, bar_rods=bar_rods, group_vertically=True)
            bar_groups.append(bar_group)

        self.bar_chart = ft.BarChart(
            max_y=max_y, expand=2, interactive=True,
            left_axis=ft.ChartAxis(labels_size=40, title_size=20, title=ft.Text('流行度（%）', color=ft.colors.TERTIARY)),
            top_axis=ft.ChartAxis(title=ft.Text('2024-12 TIOBE编程社区指数', size=20, color=ft.colors.PRIMARY),
                                  title_size=48, show_labels=False),
            bottom_axis=ft.ChartAxis(labels=bottom_axis_labels, title_size=48, title=ft.Text('编程语言', color=ft.colors.TERTIARY)),
            bar_groups=bar_groups,
            border=ft.border.all(1, ft.colors.SECONDARY),
            horizontal_grid_lines=ft.ChartGridLines(color=ft.colors.GREY_300, width=1, dash_pattern=[3, 3]),
            tooltip_bgcolor=ft.colors.with_opacity(0.5, ft.colors.GREY_300),
        )

        self.txt_box = ft.Text('Hi，很高兴遇见你！这是与您相伴的第1天，我为您整理出一些数据，希望能帮到您。', expand=1,
                               size=24, color=ft.colors.PRIMARY)

        pie_selection_colors = [ft.colors.PRIMARY, ft.colors.PURPLE, ft.colors.RED, ft.colors.ORANGE, ft.colors.YELLOW,
                                ft.colors.GREEN, ft.colors.CYAN, ft.colors.BLUE_GREY, ft.colors.PINK, ft.colors.GREY,
                                ft.colors.LIGHT_GREEN]
        color_palettes = []
        pie_sections = []

        for idx, i in enumerate(json_data):
            color_palette = ft.Container(
                ft.Row([ft.Container(bgcolor=pie_selection_colors[idx], width=12, height=12, border_radius=2), ft.Text(i)],
                       spacing=5, run_spacing=0),
                width=92)
            color_palettes.append(color_palette)
            pie_section = ft.PieChartSection(json_data[i][0], title=f'{json_data[i][0]}%', radius=80, title_position=1,
                                             color=pie_selection_colors[idx])
            pie_sections.append(pie_section)

        palette_container = ft.Container(ft.Row(color_palettes, wrap=True))
        self.pie_chart = ft.PieChart(sections=pie_sections, center_space_radius=40,
                                     on_chart_event=self.pie_chart_event)
        bottom_right_container = ft.Container(ft.Column(
            [palette_container, self.pie_chart], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.END, spacing=0, scroll=ft.ScrollMode.AUTO), expand=2)
        right_container = ft.Container(ft.Column([self.txt_box, bottom_right_container], spacing=0), expand=1,
                                       padding=ft.Padding(30, 40, 70, 40))
        self.content = ft.Row([self.bar_chart, right_container], spacing=0)

    def pie_chart_event(self, e: ft.PieChartEvent):
        """饼图触发事件"""
        normal_border = ft.BorderSide(0, ft.colors.SURFACE)
        hovered_border = ft.BorderSide(6, ft.colors.SURFACE)
        normal_radius = 80
        hovered_radius = 90
        for idx, i in enumerate(self.pie_chart.sections):
            if idx == e.section_index:
                i.border_side = hovered_border
                i.radius = hovered_radius
            else:
                i.border_side = normal_border
                i.radius = normal_radius
        self.pie_chart.update()
