# -*- encoding: utf-8 -*-

import logging
import time

import colorlog


def log_setting(logger_flag, log_path):
    """
    Func: 配置log的输出和格式
    """
    try:
        logger = logging.getLogger(f'{logger_flag}')
        logger.setLevel(logging.DEBUG)

        datefmt = "%Y-%m-%d %H:%M:%S"

        # 保存到日志文件中的log
        log_file = f'{log_path}/{logger_flag}-{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')

        #  无需使用颜色来标记日志级别，而是直接用文字标明日志级别
        file_log_format = '%(asctime)s.%(msecs)03d\t\t%(filename)s:%(lineno)d\t\t%(funcName)s\t\t【%(levelname)s】%(message)s'
        file_formatter = logging.Formatter(file_log_format, datefmt=datefmt)

        # 设置保存到日志文件的日志格式
        file_handler.setFormatter(file_formatter)

        # 输出到控制台上的日志
        control_handler = logging.StreamHandler()

        # 在控制台中，不同级别的日志显示的颜色不同，通过 colorlog 模块实现
        control_log_format = '%(log_color)s%(asctime)s.%(msecs)03d\t\t%(filename)s:%(lineno)d\t\t%(funcName)s\t\t%(message)s'
        control_formatter = colorlog.ColoredFormatter(control_log_format, datefmt=datefmt)

        # 设置输出到控制台的日志格式
        control_handler.setFormatter(control_formatter)

        # 分别添加两个日志控制器
        logger.addHandler(control_handler)
        logger.addHandler(file_handler)

        return logger
    except Exception as e:
        print('日志记录器设置失败，请检查！')
        print(e)
