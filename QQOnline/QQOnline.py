'''
Author: BNDou
Date: 2024-05-29 21:14:48
LastEditTime: 2024-06-02 09:37:51
FilePath: \ToolsBox\QQOnline\QQOnline.py
Description: 
'''
import json
import os
import os.path
import subprocess
import time

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
    return render_template('index.html', version=version)


@app.route('/get_online_info', methods=['POST'])
def get_online_info():
    '''
    获取在线QQ号
    '''
    log = getTaskProcess()
    return render_template('index.html', version=version, data=log)


@app.route('/exit_all', methods=['POST'])
def exit_all():
    '''
    退出全部账号
    '''
    log, proc_log = [], []
    # 判断是否为管理员权限
    adminAccount = request.form.get('adminAccount')
    adminPassword = request.form.get('adminPassword')
    if not is_Owner("Administrator", adminAccount, adminPassword):
        return render_template('index.html',
                               version=version,
                               data=["❌ 非管理员用户，无权退出全部QQ登录！"])
    else:
        log.append(f"✅ 管理员用户: {adminAccount} 申请退出全部QQ登录！")

    # 获取QQ进程
    for proc in psutil.process_iter():
        if proc.name() == "QQ.exe":
            if os.name == 'nt':  # Windows系统
                if "--from-multiple-login" in proc.cmdline():
                    proc_log.append(
                        f"✅ QQ号: {proc.cmdline()[-1]} 进程id: {proc.pid} 退出登录")
                    # 杀死进程
                    cmd = f'taskkill /pid {str(proc.pid)} /f'
                    try:
                        os.system(cmd)
                        time.sleep(1)
                    except Exception as e:
                        proc_log.append(e)
    return render_template('index.html',
                           version=version,
                           data=((log + proc_log) if len(proc_log) > 0 else
                                 (log + ["❌ 未发现可退出登录的QQ号"])))


@app.route('/exit_qq', methods=['POST'])
def exit_qq():
    '''
    退出指定QQ
    '''
    log, proc_log = [], []
    # 判断是否为QQ号主人权限
    qqAccount = request.form.get('qqAccount')
    qqPassword = request.form.get('qqPassword')
    if not is_Owner("QQOnline", qqAccount, qqPassword):
        return render_template('index.html',
                               version=version,
                               data=[f"❌ QQ号: {qqAccount} 非号主无权限退出登录！"])
    else:
        log.append(f"✅ QQ号: {qqAccount} 号主申请退出登录！")

    # 获取QQ进程
    for proc in psutil.process_iter():
        if proc.name() == "QQ.exe":
            if os.name == 'nt':  # Windows系统
                if all(value in proc.cmdline()
                       for value in ["--from-multiple-login", qqAccount]):
                    proc_log.append(
                        f"✅ QQ号: {proc.cmdline()[-1]} 进程id: {proc.pid} 退出登录")
                    # 杀死进程
                    cmd = f'taskkill /pid {str(proc.pid)} /f'
                    try:
                        os.system(cmd)
                        time.sleep(1)
                    except Exception as e:
                        proc_log.append(e)
    return render_template('index.html',
                           version=version,
                           data=((log + proc_log) if len(proc_log) > 0 else
                                 (log + ["❌ 未发现该QQ号在线！"])))


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
                                'index.html',
                                version=version,
                                data=[
                                    f"✅ QQ号: {qq_number} 进程ID: {proc.pid} 登录成功"
                                ])
            pass
        return render_template('index.html',
                               version=version,
                               data=[f"❌ {qq_number} 登录失败"])
    except Exception as e:
        return render_template('index.html',
                               version=version,
                               data=[f"❌ {qq_number} 登录失败: {e}"])


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
                        f"✅ QQ号: {proc.cmdline()[-1]} 进程id: {proc.pid} 在线中······"
                    )
    return proc_log if len(proc_log) > 0 else ["❌ 未发现在线的QQ号"]


def is_Owner(role, account, password):
    '''
    判断是否为所属者
    
    :param role: 角色
    :param account: 用户名
    :param password: 密码
    :return: 是否为所属者
    '''
    # 获取当前脚本的绝对路径，获取配置文件的路径
    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "templates", "config.json")
    # 读取配置文件
    with open(config_file_path, encoding="utf-8") as f:
        config = json.loads(f.read())
    datas = config.get(role)

    # 判断用户名和密码是否在 角色 所属下
    for data in datas:
        if account == data['user'] and password == data['pwd']:
            return True
    return False


def version():
    '''
    获取版本信息
    '''
    global version
    # 获取当前脚本的绝对路径，获取配置文件的路径
    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "templates", "config.json")
    # 读取配置文件
    with open(config_file_path, encoding="utf-8") as f:
        config = json.loads(f.read())
    version = config.get('version')


if __name__ == '__main__':
    version()
    # app.run(host="192.168.31.120", port=1314, debug=False)
    app.run(host="127.0.0.1", port=1314, debug=True)
