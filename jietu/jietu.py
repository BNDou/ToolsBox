'''
Author: BNDou
Date: 2024-06-26 01:09:33
LastEditTime: 2024-12-31 20:45:21
FilePath: \ToolsBox\jietu\jietu.py
Description: 智能截图工具 - 支持全屏和窗口截图，提供Web界面操作
'''

# 导入所需的库
import base64                                      # 用于图片base64编码
import os                                         # 用于文件和目录操作
import logging                                    # 用于日志记录
from time import sleep                            # 用于延时操作
from datetime import datetime, timedelta          # 用于时间戳生成和时间计算
from PIL import Image                             # 用于图片处理
import pyautogui                                  # 用于屏幕截图
import win32gui                                   # 用于Windows窗口操作
import win32con                                   # 用于Windows常量定义
import win32com.client                            # 用于Windows COM组件
import pythoncom                                  # 用于COM线程支持
from apscheduler.schedulers.background import BackgroundScheduler  # 用于后台任务调度
from flask import Flask, render_template, request, jsonify         # Web框架
from config import Config                         # 导入配置文件

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
scheduler = BackgroundScheduler()                 # 创建后台任务调度器
hwnd_map = {}                                    # 存储窗口句柄和标题的映射

# 确保截图保存目录存在
os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)

def clean_old_screenshots():
    """清理过期的截图文件
    1. 清理超过最大数量限制的旧截图
    2. 清理超过过期天数的截图
    """
    try:
        # 获取所有截图文件
        screenshots = []
        for filename in os.listdir(Config.SCREENSHOT_DIR):
            if filename.startswith('screenshot_') and (filename.endswith('.png') or filename.endswith('.jpeg')):
                filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
                create_time = datetime.fromtimestamp(os.path.getctime(filepath))
                screenshots.append((filepath, create_time))
        
        # 按创建时间排序
        screenshots.sort(key=lambda x: x[1], reverse=True)
        
        # 清理超过数量限制的文件
        if len(screenshots) > Config.MAX_CACHE_SIZE:
            for filepath, _ in screenshots[Config.MAX_CACHE_SIZE:]:
                try:
                    os.remove(filepath)
                    logger.info(f"Removed old screenshot: {filepath}")
                except Exception as e:
                    logger.error(f"Error removing file {filepath}: {str(e)}")
        
        # 清理过期文件
        expire_date = datetime.now() - timedelta(days=Config.CACHE_EXPIRE_DAYS)
        for filepath, create_time in screenshots:
            if create_time < expire_date:
                try:
                    os.remove(filepath)
                    logger.info(f"Removed expired screenshot: {filepath}")
                except Exception as e:
                    logger.error(f"Error removing expired file {filepath}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in clean_old_screenshots: {str(e)}")

# 添加定时清理任务
scheduler.add_job(clean_old_screenshots, 'interval', hours=1)  # 每小时清理一次
scheduler.start()

@app.route('/')
def index():
    """主页路由
    获取所有可用窗口并显示主页
    """
    try:
        win32gui.EnumWindows(get_all_hwnd, None)  # 枚举所有窗口
        return render_template('index.html', hwnd_map=hwnd_map)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/get_data', methods=['POST'])
def get_data():
    """处理截图请求
    接收前端参数并执行截图操作
    """
    try:
        # 更新窗口列表
        win32gui.EnumWindows(get_all_hwnd, None)
        
        # 获取前端参数
        hwnd = request.form.get('hwnd-list')          # 窗口句柄
        quality = int(request.form.get('quality', 95)) # 图片质量
        format = request.form.get('format', 'PNG')     # 图片格式
        
        # 生成文件名和路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.{format.lower()}"
        filepath = os.path.join(Config.SCREENSHOT_DIR, filename)

        # 执行截图
        if hwnd:
            # 截取指定窗口
            get_target_window(hwnd, filepath, format, quality)
        else:
            # 全屏截图
            img = pyautogui.screenshot(region=None)
            img.save(filepath, format=format, quality=quality)

        # 清理旧截图
        clean_old_screenshots()

        # 读取图片并转为base64
        with open(filepath, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # 返回成功响应
        return jsonify({
            'status': 'success',
            'image': image_base64,
            'filename': filename
        })
    except Exception as e:
        logger.error(f"Error in get_data route: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/get_history')
def get_history():
    """获取历史截图列表
    返回所有历史截图的信息，包括文件名、创建时间等
    """
    try:
        screenshots = []
        for filename in os.listdir(Config.SCREENSHOT_DIR):
            if filename.startswith('screenshot_') and (filename.endswith('.png') or filename.endswith('.jpeg')):
                filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
                create_time = datetime.fromtimestamp(os.path.getctime(filepath))
                # 读取图片并转为base64
                with open(filepath, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                screenshots.append({
                    'filename': filename,
                    'create_time': create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'image': image_base64
                })
        
        # 按创建时间倒序排序
        screenshots.sort(key=lambda x: x['create_time'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'screenshots': screenshots
        })
    except Exception as e:
        logger.error(f"Error in get_history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/delete_screenshot', methods=['POST'])
def delete_screenshot():
    """删除指定的历史截图
    
    Args:
        filename: 要删除的文件名
    """
    try:
        filename = request.form.get('filename')
        if not filename:
            raise ValueError('文件名不能为空')
            
        filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
        
        # 检查文件是否存在且在截图目录中
        if not os.path.exists(filepath) or not filename.startswith('screenshot_'):
            raise ValueError('文件不存在或不是有效的截图文件')
            
        # 删除文件
        os.remove(filepath)
        logger.info(f"Deleted screenshot: {filename}")
        
        return jsonify({
            'status': 'success',
            'message': '删除成功'
        })
    except Exception as e:
        logger.error(f"Error in delete_screenshot: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

def get_all_hwnd(hwnd, mouse):
    """获取所有可用窗口
    将窗口句柄和标题存储到hwnd_map中
    
    Args:
        hwnd: 窗口句柄
        mouse: 鼠标参数（未使用）
    """
    try:
        if (win32gui.IsWindow(hwnd) and 
            win32gui.IsWindowEnabled(hwnd) and
            win32gui.IsWindowVisible(hwnd) and
            win32gui.GetWindowText(hwnd)):
            hwnd_map.update({hwnd: win32gui.GetWindowText(hwnd)})
    except Exception as e:
        logger.error(f"Error in get_all_hwnd: {str(e)}")

def get_target_window(target_index, filepath, format='PNG', quality=95):
    """截取指定窗口
    
    Args:
        target_index: 目标窗口句柄
        filepath: 保存路径
        format: 图片格式，默认PNG
        quality: 图片质量，默认95
    """
    try:
        # 初始化COM
        pythoncom.CoInitialize()
        
        # 将窗口置顶
        win32gui.BringWindowToTop(target_index)
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        
        # 设置窗口状态
        win32gui.SetForegroundWindow(target_index)
        win32gui.ShowWindow(target_index, win32con.SW_RESTORE)
        
        # 获取窗口位置
        x1, y1, x2, y2 = win32gui.GetWindowRect(target_index)
        sleep(0.5)  # 等待窗口完全显示
        
        # 截图
        screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        
        # 图片格式处理
        if format.upper() == 'JPEG':
            # JPEG不支持透明通道，需要处理
            if screenshot.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', screenshot.size, (255, 255, 255))
                background.paste(screenshot, mask=screenshot.split()[-1])
                screenshot = background
        
        # 保存图片
        screenshot.save(filepath, format=format, quality=quality)
    except Exception as e:
        logger.error(f"Error in get_target_window: {str(e)}")
        raise
    finally:
        # 释放COM
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    # 启动Flask应用
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
