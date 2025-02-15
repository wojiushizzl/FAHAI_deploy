<h1 align="center"> Flet-GUI-basic</h1>

## ✨简介
本项目主要提供一个Flet GUI + Yolo  的跨平台视觉识别应用
```
平台测试：
√ Windows 10&11
√ Navdia Jetson Linux
√ Raspberry Pi 4&5 Linux
√ MacOS
```

## 📢近期更新
- 2025-02-15 发布软件**0.1.0**版本

## 💻下载安装
推荐使用[**Python>=3.8**](https://www.python.org/)，补丁版本越高越好。在终端输入以下指令按回车

```bash
pip install -r requirements.txt
```

## 🐍在Python中使用
项目启动文件为根目录中的main.py

打开终端，确保当前路径处于项目的根目录，输入以下指令按回车键启动。注意，在**Windows**系统中命令为python，在**Linux**系统中命令为python3
```bash
python main.py
```
如需以web端启动，打开终端，输入以下命令，默认地址127.0.0.1，默认端口5200
```bash
python main.py --web
```
查看web端启动的所有配置参数及帮助信息，输入以下命令
```bash
python main.py --help
```

## 🧩项目结构
```
Flet-GUI-basic/
├── assets/             # 静态资源文件
├── common/             # 项目经常用到的功能
│   └── app_setting.py      # 项目设置
├── custom_requests/    # 自定义的网络请求功能
├── custom_widgets/     # 自定义的通用小组件，方便与其它项目集成
├── user_data/          # 存储应用使用数据，可随时删除
├── utils/              # 辅助功能
├── widgets/            # 功能界面
│   └── main_window.py      # 项目主界面
│   └── main_window_widgets.py    # 主界面的组件，如标题栏、侧边栏、左右抽屉组件
│   └── home_window.py      # 首页界面
│   └── setting_window.py   # 设置界面
├── main.py             # 项目启动文件
├── requirements.txt    # 项目依赖环境
```


## 📝代办清单
### 简化UI界面，去除不必要功能
- 去除登录界面
- 去除消息通知界面
- 去除音乐播放功能
- 去除广告卡片
- 去除消息卡片




