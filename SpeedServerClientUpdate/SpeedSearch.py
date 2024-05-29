'''
Author: BNDou
Date: 2024-03-27 00:05:06
LastEditTime: 2024-04-17 13:29:17
FilePath: \ToolsBox\SpeedServerClientUpdate\SpeedSearch.py
Description: 
'''
import os
import os.path
import socket
import subprocess
from datetime import datetime
from threading import Thread

import psutil
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template

app = Flask(__name__)
scheduler = BackgroundScheduler()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_data', methods=['POST'])
def get_data():
    log = update()
    return render_template('index.html', data=log)


@app.route('/restart', methods=['POST'])
def restart():
    log = []
    # 退出服务进程
    proc_log = taskkill()
    # 重启服务
    try:
        subprocess.Popen("服务端.exe", shell=True)
        log.extend([proc_log, "重启服务!"])
    except Exception as e:
        log.extend([proc_log, f"重启服务失败：{e}"])
    return render_template('index.html', data=log)


def taskkill():
    '''退出服务进程'''
    proc_log = ""
    for proc in psutil.process_iter():
        # print(“pid-%d,name:%s” % (proc.pid,proc.name()))
        if proc.name() == "服务端.exe":
            if os.name == 'nt':  # Windows系统
                running = True
                proc_log = f"进程id：{proc.pid} 进程名：{proc.name()} 服务在运行"
                cmd = f'taskkill /pid {str(proc.pid)} /f'
                try:
                    os.system(cmd)
                except Exception as e:
                    log += e
                break
    return proc_log


def update():
    '''更新文件'''
    print(f'【{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}】监测IP')
    log = []
    # 数据读取
    with open('config.yml', 'r', encoding='gbk') as f:
        config = yaml.safe_load(f)
    ServerIP = config['Server']['IP']
    QQServerIP = config['QQServer']['IP']
    log.append(f"配置文件中ServerIP={ServerIP}")
    log.append(f"配置文件中QQServerIP={QQServerIP}")

    domain = 'bndou.top'  # 填写域名地址
    myIP = socket.getaddrinfo(domain, 'http')[0][4][0]
    log.append(f'最新IP={myIP}')

    proc_log = "”服务端.exe“服务未运行！！"
    running = False
    if any(s != myIP for s in [str(ServerIP), str(QQServerIP)]):
        # 修改 ip 配置信息
        config['Server'].update({'IP': myIP})
        config['QQServer'].update({'IP': myIP})

        # 保存修改后的配置信息到 yml 文件
        with open('config.yml', 'w') as f:
            yaml.safe_dump(config, f, allow_unicode=True)

        log.append("更新完成！")

        # 通知内容
        url = "https://wxpusher.zjiecode.com/api/send/message"
        headers = {"Content-Type": "application/json"}
        data = {
            "appToken": "AT_XQGRg1wEOkgJnJ99fBT8EDmJpeIy4wnE",
            "content": f'config.yml文件IP更新为【{myIP}】\n\nlog输出：\n{log}',
            "summary": "服务端更新",
            "contentType": 1,
            "topicIds": [27124],
            "verifyPay": "false"
        }
        response = requests.post(url, headers=headers, json=data)

        # 退出服务进程
        proc_log = taskkill()
        # 重启服务
        try:
            subprocess.Popen("服务端.exe", shell=True)
            log.extend([proc_log, "重启服务!"])
        except Exception as e:
            log.extend([proc_log, f"重启服务失败：{e}"])
    else:
        for proc in psutil.process_iter():
            if proc.name() == "服务端.exe":
                if os.name == 'nt':  # Windows系统
                    running = True
                    proc_log = f"进程id：{proc.pid} 进程名：{proc.name()} 服务在运行"
        if not running:
            try:
                subprocess.Popen("服务端.exe", shell=True)
                log.extend([proc_log, "重启服务!"])
            except Exception as e:
                log.extend([proc_log, f"重启服务失败：{e}"])
        log.extend([proc_log, "IP相同无需更新配置！"])

    return log


if __name__ == '__main__':
    update()
    # 创建一个线程来运行定时任务
    scheduler.add_job(update, 'interval', minutes=5)
    scheduler.start()

    app.run(host="192.168.31.120", port=27017, debug=False)
