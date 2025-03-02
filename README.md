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
<img width="720" alt="5" src="https://github.com/wojiushizzl/FAHAI_deploy/blob/main/assets/images/homepage.png">

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

## ⏰其他

Install nvidia-jetpack
```bash
$ sudo apt upgrade
$ sudo apt update
$ sudo apt dist-upgrade
$ sudo reboot
$ sudo apt install nvidia-jetpack 
```
Install jtop
```bash	
$ sudo apt install python3-pip
$ sudo -H pip3 install -U jetson-stats
$ sudo reboot
```
Install VSCode  
[Download arm64 version "code_1.87.2-1709911730_arm64.deb"](https://code.visualstudio.com/docs/?dv=linuxarm64_deb)
```bash
#Install
$ sudo dpkg -i code_1.87.2-1709911730_arm64.deb # edit aglin with your download version
```
Install label-studio  
[Label studio github](https://github.com/HumanSignal/label-studio?tab=readme-ov-file)

```bash
#Install with conda
conda create --name label-studio
conda activate label-studio
conda install psycopg2
pip install label-studio

#run 
label-studio
```
Install Sunlogin 
[Download the Kylin Arm64 version   ](https://sunlogin.oray.com/download/linux?type=personal&ici=sunlogin_navigation) 
	
**SunloginClient_11.0.1.44968_kylin_arm.deb**

```bash
#install 
$ sudo dpkg -i SunloginClient_11.0.1.44968_kylin_arm.deb 

#start
$ /usr/local/sunlogin/bin/sunloginclient

#uninstall
$ sudo dpkg -r sunloginclient

#Set Sunlogin start with sys starting
open app "startup application"
add command "/usr/local/sunlogin/bin/sunloginclient"

```
Install HIK vision MVS 
https://www.hikrobotics.com/cn/machinevision/service/download/?module=0

Install Archiconda instead of miniconda
reference https://blog.csdn.net/gls_nuaa/article/details/135630629

```bash
wget https://github.com/Archiconda/build-tools/releases/download/0.2.3/Archiconda3-0.2.3-Linux-aarch64.sh

#install
$ bash Archiconda3-0.2.3-Linux-aarch64.sh

#restart Terminal, check 
$ conda 

#change conda source
$ conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
$ conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge 
$ conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/
$ conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/

#create conda env 
$ conda create -n yolov8 python=3.8

#activate env
$ conda activate yolov8

#remove env
$ conda remove -n yolov8 --all

#pip change source
$ pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```