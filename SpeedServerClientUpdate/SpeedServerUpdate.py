# -*- coding: utf-8 -*-
import os.path
import socket
import sys
import time

import psutil as p
import requests
import yaml

if __name__ == "__main__":
    log = ""
    # 初始化配置文件路径
    # 当前文件路径
    curpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    # 配置文件路径（组合、相对路径）
    inipath = os.path.join(curpath, "config.yml")
    log += f'当前配置文件地址： {inipath}\n'
    # 数据读取
    log += "读取配置文件...\n"
    with open('config.yml', 'r', encoding='gbk') as f:
        config = yaml.safe_load(f)
    ServerIP = config['Server']['IP']
    QQServerIP = config['QQServer']['IP']
    log += f'ServerIP={ServerIP}\nQQServerIP={QQServerIP}\n\n'

    log += "1、开始获取最新IP\n"
    domain = ''  # 填写域名地址
    myIP = socket.getaddrinfo(domain, 'http')[0][4][0]
    log += f'最新IP={myIP}\n'

    if any(s != myIP for s in [str(ServerIP), str(QQServerIP)]):
        # myIP != ServerIP and myIP != QQServerIP:
        log += "2、修改IP到config.yml配置文件中\n"
        # 修改 ip 配置信息
        config['Server'].update({'IP': myIP})
        config['QQServer'].update({'IP': myIP})

        log += "3、保存更新config.yml配置文件\n"
        # 保存修改后的配置信息到 yml 文件
        with open('config.yml', 'w') as f:
            yaml.safe_dump(config, f, allow_unicode=True)

        # 退出服务进程
        for proc in p.process_iter():
            # print(“pid-%d,name:%s” % (proc.pid,proc.name()))
            if proc.name() == "服务端.exe":
                if os.name == 'nt':  # Windows系统
                    cmd = f'taskkill /pid {str(proc.pid)} /f'
                    try:
                        log += "退出服务\n"
                        os.system(cmd)
                    except Exception as e:
                        log += e
                    break
        # 重启服务
        log += "启动服务\n"
        os.system(os.path.join(curpath, "服务端.exe"))

        log += "更新完成！\n"

        # 通知内容
        url = "https://wxpusher.zjiecode.com/api/send/message"
        headers = {"Content-Type": "application/json"}
        data = {
            "appToken": "AT_XQGRg1wEOkgJnJ99fBT8EDmJpeIy4wnE",
            "content": f'config.yml文件IP更新为【{myIP}】\n\nlog出输：\n{log}',
            "summary": "服务端更新",
            "contentType": 1,
            "topicIds": [27124],
            "verifyPay": "false"
        }
        response = requests.post(url, headers=headers, json=data)
        # response.encoding = "utf-8"
        # print(response.json())
    else:
        log += "IP相同无需更新配置，请退出！\n"

    # 5秒后自动关闭
    print(log + "【5秒后自动关闭】")
    time.sleep(5)
