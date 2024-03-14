import os.path
import socket
import sys

import requests
import yaml

if __name__ == "__main__":
    # 初始化配置文件路径
    # 当前文件路径
    curpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    # 配置文件路径（组合、相对路径）
    inipath = os.path.join(curpath, "config.yml")
    print("当前地址：", inipath)
    # 数据读取
    with open('config.yml', 'r', encoding='gbk') as f:
        config = yaml.safe_load(f)
    ServerIP = config['Server']['IP']
    QQServerIP = config['QQServer']['IP']

    print("1、IP开始获取")
    domain = '域名'
    myIP = socket.getaddrinfo(domain, 'http')[0][4][0]
    print(f'获取到IP={myIP}')

    if any(s != myIP for s in [str(ServerIP),str(QQServerIP)]):
        # myIP != ServerIP and myIP != QQServerIP:
        print("2、修改IP到config.yml配置文件中")
        # 修改 ip 配置信息
        config['Server'].update({'IP': myIP})
        config['QQServer'].update({'IP': myIP})

        print("3、保存更新config.yml配置文件")
        # 保存修改后的配置信息到 yml 文件
        with open('config.yml', 'w') as f:
            yaml.safe_dump(config, f, allow_unicode=True)

        print("更新完成，请关闭！")

        # 通知内容
        url = "https://wxpusher.zjiecode.com/api/send/message"
        headers = {"Content-Type": "application/json"}
        data = {
            "appToken": "AT_XQGRg1wEOkgJnJ99fBT8EDmJpeIy4wnE",
            "content": "config.yml文件IP更新为【" + myIP + "】",
            "summary": "服务端更新",
            "contentType": 1,
            "topicIds": [27124],
            "verifyPay": "false"
        }
        response = requests.post(url, headers=headers, json=data)
        # response.encoding = "utf-8"
        # print(response.json())
    else:
        print("无需更新IP配置，请退出！")
