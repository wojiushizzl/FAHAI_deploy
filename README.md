<h1 align="center"> FAHAI_DEPLOY</h1>

## ✨简介
本项目主要提供一个Flet GUI + Yolo  的跨平台视觉识别应用
```
平台测试：
√ Windows 10&11
√ Navdia Jetson Orin NX Linux
√ Raspberry Pi 4&5 Linux
√ MacOS
```
## 📸软件截图
<img width="720" alt="5" src="">







## 📢近期更新
```bash
- 2025-02-15 发布软件**0.1.0**版本
```

## 💻下载安装
推荐使用[**Python>=3.8**](https://www.python.org/)

```bash
pip install -r requirements.txt
```

在NVIDIA Jetson 设备上安装需要安装特定版本torch 及 torch vision
https://docs.ultralytics.com/zh/guides/nvidia-jetson/#install-ultralytics-package   


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

