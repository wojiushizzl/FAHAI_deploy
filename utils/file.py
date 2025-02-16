import os
import re
from logging import FileHandler, Logger, StreamHandler, Formatter
from time import strftime
from typing import Union, Iterable


def create_logger(logger_name: str = 'FAHAI-AI-VISION',
                  level: Union[int, str] = 20,
                  log_dir: str = 'logs',
                  console_show: bool = False) -> Logger:
    """
    创建日志对象
    :param logger_name: 日志对象名称
    :param level: 日志等级，推荐使用整数，默认20，NOTSET=0，DEBUG=10，INFO=20，WARNING=30，ERROR=40，CRITICAL=50
    :param log_dir: 日志文件夹路径
    :param console_show: 是否在窗口展示信息
    :return: 日志对象
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger = Logger(logger_name, level)
    logger.propagate = False

    today = strftime('%Y-%m-%d')
    file_handler = FileHandler(f'{log_dir}/{today}.log', encoding='utf-8')
    log_format = Formatter('%(asctime)s - %(name)s - %(levelname)s    %(message)s')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    if console_show:
        stream_handler = StreamHandler()
        stream_handler.setFormatter(log_format)
        logger.addHandler(stream_handler)
    return logger


def clear_logger(log_limit: int = 30, log_dir: str = 'logs'):
    """
    清除过旧的日志文件
    :param log_limit: 日志文件最大保留数量
    :param log_dir: 日志文件夹路径
    :return:
    """
    if not os.path.exists(log_dir):
        return
    log_files = os.listdir(log_dir)
    if len(log_files) <= log_limit:
        return

    log_dic = {os.path.getctime(logger_path := os.path.join(log_dir, i)): logger_path for i in log_files}
    tsp_li = sorted(log_dic, reverse=True)
    for tsp in tsp_li[log_limit:]:
        os.remove(log_dic[tsp])


def clear_project_annotation(project_dir: str,
                             save_dir_suffix: str = '_bak',
                             exclude_dirs: Iterable[str] = ('user_data', 'logs', '__pycache__', 'assets')):
    """
    清除项目下的所有py文件注释
    :param project_dir: 项目目录
    :param save_dir_suffix: 设置清除注释后的项目文件名后缀，
    :param exclude_dirs: 目录中包含这些词将跳过操作
    :return:
    """
    if not os.path.exists(project_dir) or os.path.isfile(project_dir):
        return
    save_dir = f'{project_dir}{save_dir_suffix}'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    pattern = '[^= ] +""".*?"""'
    pattern2 = "[^= ] +'''.*?'''"
    for current_dir, dirs, files in os.walk(project_dir):
        flag = False
        for i in exclude_dirs:
            if i in current_dir:
                flag = True
                break
        if flag:
            continue

        for i in files:
            if not i.endswith('.py'):
                continue
            py_path = f'{current_dir}/{i}'
            with open(py_path, 'r', encoding='utf-8') as f:
                lines = []
                while line_data := f.readline():
                    if not line_data.strip() or line_data.strip().startswith('#'):
                        continue
                    lines.append(line_data)

            data = ''.join(lines)
            data = re.sub(pattern, '', data, flags=re.S)
            data = re.sub(pattern2, '', data, flags=re.S)
            save_path = py_path.replace(project_dir, save_dir)

            py_save_dir = os.path.split(save_path)[0]
            if not os.path.exists(py_save_dir):
                os.makedirs(py_save_dir)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(data)
