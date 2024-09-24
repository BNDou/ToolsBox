'''
Author: BNDou
Date: 2024-06-26 01:09:33
LastEditTime: 2024-09-25 03:23:21
FilePath: \ToolsBox\jjietu\jietu.py
Description: 
'''
import base64
from time import sleep
import pyautogui
import win32gui
import win32con
import win32com.client
import pythoncom
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request

app = Flask(__name__)
scheduler = BackgroundScheduler()
hwnd_map = {}


@app.route('/')
def index():
    # 获取所有窗口
    win32gui.EnumWindows(get_all_hwnd, None)
    return render_template('index.html', hwnd_map=hwnd_map)


@app.route('/get_data', methods=['POST'])
def get_data():
    # 获取所有窗口
    win32gui.EnumWindows(get_all_hwnd, None)
    # 获取下拉列表的值
    hwnd = request.form.get('hwnd-list')
    # print(hwnd)
    if hwnd: # 截取指定窗口
        get_target_window(hwnd)
    else: # 截取全屏
        img = pyautogui.screenshot(region=None)
        img.save('C:/Users/服务器/Pictures/jietu.png')
    image_path = 'C:/Users/服务器/Pictures/jietu.png'
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read())
    return render_template('index.html', hwnd_map=hwnd_map, img_base64=str(image_base64)[2:-1])


def get_all_hwnd(hwnd, mouse):
    if (win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd)
            and win32gui.IsWindowVisible(hwnd)
            and win32gui.GetWindowText(hwnd)):
        hwnd_map.update({hwnd: win32gui.GetWindowText(hwnd)})


def get_target_window(target_index):
    # 线程初始化
    pythoncom.CoInitialize()
    win32gui.BringWindowToTop(target_index)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    # 被其他窗口遮挡，调用后放到最前面
    win32gui.SetForegroundWindow(target_index)
    # 解决被最小化的情况
    win32gui.ShowWindow(target_index, win32con.SW_RESTORE)
    # 返回坐标值
    (x1, y1, x2, y2) = win32gui.GetWindowRect(target_index)
    # 释放资源
    pythoncom.CoUninitialize()
    sleep(0.5)
    screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
    screenshot.save("C:/Users/服务器/Pictures/jietu.png")
    # screenshot.save("jietu.png")


if __name__ == '__main__':
    app.run(host="192.168.31.120", port=27018, debug=False)
    # app.run(host="127.0.0.1", port=27018, debug=True)
