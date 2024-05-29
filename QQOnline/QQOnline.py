'''
Author: BNDou
Date: 2024-05-29 21:14:48
LastEditTime: 2024-05-30 02:24:18
FilePath: \ToolsBox\QQOnline\QQOnline.py
Description: 
'''
import os
import os.path
import time

import win32api as api
import pyautogui
import psutil
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template

app = Flask(__name__)
scheduler = BackgroundScheduler()


@app.route('/')
def index():
    '''
    主页
    '''
    return render_template('index.html')


@app.route('/get_online_info', methods=['POST'])
def get_online_info():
    '''
    获取在线QQ号
    '''
    log = getTaskProcess()
    return render_template('index.html', data=log)


@app.route('/quit', methods=['POST'])
def quit():
    '''
    退出登录
    '''
    proc_log = []
    for proc in psutil.process_iter():
        if proc.name() == "QQ.exe":
            if os.name == 'nt':  # Windows系统
                if "--from-multiple-login" in proc.cmdline():
                    proc_log.append(
                        f"✔️进程id：{proc.pid} QQ号：{proc.cmdline()[-1]} 退出登录")
                    cmd = f'taskkill /pid {str(proc.pid)} /f'
                    try:
                        os.system(cmd)
                    except Exception as e:
                        proc_log.append(e)
    return render_template(
        'index.html',
        data=(proc_log if len(proc_log) > 0 else ["❌未发现可退出登录的QQ号"]))


@app.route('/open_qq', methods=['POST'])
def open_qq():
    '''
    打开QQ
    '''
    qq = "C:\Program Files\Tencent\QQNT\QQ.exe"
    api.ShellExecute(0, "open", qq, None, None, 1)
    time.sleep(3)
    return render_template('index.html', data=["✔️打开QQ"])


@app.route('/click_dropdown', methods=['POST'])
def click_dropdown():
    '''
    点击下拉列表
    '''
    try:
        login = pyautogui.locateOnScreen("templates\login.png")
        Center = pyautogui.center(login)
        pyautogui.click(Center.x + 30, Center.y - 70)
        return render_template('index.html', data=["✔️点击下拉列表"])
    except Exception as e:
        return render_template('index.html', data=["❌ERROR:未找到下拉按钮"])


@app.route('/select_account', methods=['POST'])
def select_account():
    '''
    选择登录的账号
    '''
    try:
        login = pyautogui.locateOnScreen("templates\login.png")
        Center = pyautogui.center(login)
        pyautogui.click(Center.x, Center.y - 200)
        time.sleep(1)
        pyautogui.click(Center.x + 80, Center.y - 200)
        return render_template('index.html', data=["✔️选择登录的账号"])
    except Exception as e:
        return render_template('index.html', data=["❌ERROR:未找到账号头像"])


@app.route('/click_login', methods=['POST'])
def click_login():
    '''
    点击登录
    '''
    try:
        login = pyautogui.locateOnScreen("templates\login.png")
        pyautogui.click(pyautogui.center(login))
        time.sleep(20)
        return render_template('index.html', data=["✔️点击登录"])
    except Exception as e:
        return render_template('index.html', data=["❌ERROR:未找到登录按钮"])


def getTaskProcess():
    '''
    获取任务进程
    '''
    proc_log = []
    for proc in psutil.process_iter():
        if proc.name() == "QQ.exe":
            if os.name == "nt":  # Windows系统
                if "--from-multiple-login" in proc.cmdline():
                    proc_log.append(
                        f"✔️进程id：{proc.pid} QQ号：{proc.cmdline()[-1]} 在线中······"
                    )
    return proc_log if len(proc_log) > 0 else ["❌未发现在线的QQ号"]


if __name__ == '__main__':
    app.run(host="192.168.31.120", port=1314, debug=False)
