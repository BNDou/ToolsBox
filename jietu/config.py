'''
配置文件 - 存储项目的所有可配置项
Author: BNDou
Date: 2024-06-26 01:09:33
LastEditTime: 2024-12-31 20:45:21
FilePath: \ToolsBox\jietu\config.py
Description: 智能截图工具的配置文件，包含服务器配置、截图配置和缓存配置
'''

import os

class Config:
    """配置类
    包含所有项目配置项，使用类属性方式定义，方便其他模块导入使用
    """
    
    # Web服务器配置
    # HOST = "127.0.0.1"  # 服务器监听地址，本地使用localhost
    HOST = "192.168.31.120"  # 服务器监听地址，本地使用localhost
    PORT = 27018        # 服务器端口号，避免与常用端口冲突
    DEBUG = False       # 调试模式开关，生产环境应设为False

    # 截图文件配置
    SCREENSHOT_DIR = os.path.join(os.path.expanduser('~'), 'Pictures', 'Screenshots')  # 截图保存目录，默认在用户图片文件夹下
    DEFAULT_FORMAT = 'PNG'   # 默认图片格式，PNG支持透明度
    DEFAULT_QUALITY = 100     # 默认图片质量（1-100），仅对JPEG格式有效
    
    # 支持的图片格式
    ALLOWED_FORMATS = [
        'PNG',   # 无损压缩，支持透明度
        'JPEG'   # 有损压缩，文件更小
    ]
    
    # 缓存配置
    MAX_CACHE_SIZE = 50     # 最大缓存截图数量，超过此数量将清理最早的截图
    CACHE_EXPIRE_DAYS = 7    # 缓存过期天数，超过此天数的截图将被自动清理 