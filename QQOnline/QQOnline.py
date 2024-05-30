'''
Author: BNDou
Date: 2024-05-29 21:14:48
LastEditTime: 2024-05-30 16:34:58
FilePath: \ToolsBox\QQOnline\QQOnline.py
Description: 
'''
import os
import os.path
import subprocess
import time

import win32api as api
import pyautogui
import psutil
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, render_template

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
                        f"✅ 进程id: {proc.pid} QQ号: {proc.cmdline()[-1]} 退出登录")
                    cmd = f'taskkill /pid {str(proc.pid)} /f'
                    try:
                        os.system(cmd)
                        time.sleep(1)
                    except Exception as e:
                        proc_log.append(e)
    return render_template(
        'index.html',
        data=(proc_log if len(proc_log) > 0 else ["❌ 未发现可退出登录的QQ号"]))


@app.route('/login', methods=['POST'])
def login():
    '''
    点击登录
    '''
    qq_number = request.form.get('qqNumberInput')
    login_cmd = (
        '"C:\Program Files\Tencent\QQNT\QQ.exe" '
        '"C:\Program Files\Tencent\QQNT\resources\app\versions\9.9.10\application\background.js" '
        '--from-multiple-login ' + qq_number)
    try:
        p = subprocess.Popen(login_cmd, shell=True)

        while p.poll() is None:
            time.sleep(8)
            for proc in psutil.process_iter():
                if proc.name() == "QQ.exe":
                    if os.name == "nt":  # Windows系统
                        if qq_number in proc.cmdline():
                            return render_template(
                                'index.html', data=[f"✅ 进程ID: {proc.pid} QQ号: {qq_number} 登录成功"])
            pass
        return render_template('index.html', data=[f"❌ {qq_number} 登录失败"])
    except Exception as e:
        return render_template('index.html', data=[f"❌ {qq_number} 登录失败: {e}"])


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
                        f"✅ 进程id: {proc.pid} QQ号: {proc.cmdline()[-1]} 在线中······")
    return proc_log if len(proc_log) > 0 else ["❌ 未发现在线的QQ号"]


if __name__ == '__main__':
    app.run(host="192.168.31.120", port=1314, debug=False)
    # app.run(host="127.0.0.1", port=1314, debug=True)
