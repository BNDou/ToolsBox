# -*- coding: utf-8 -*-
import configparser
import os.path
import socket
import sys
import time

if __name__ == "__main__":
    # 初始化配置文件路径
    # 当前文件路径
    curpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    # 配置文件路径（组合、相对路径）
    inipath = os.path.join(curpath, "DirSvrInfo1.ini")
    print("\n当前配置文件地址：", inipath)
    # 数据读取
    conf = configparser.ConfigParser()
    conf.read(inipath, encoding="utf-8")
    # domain = conf.get(conf.sections()[0], 'domain')
    domain = ''  # 填写域名地址

    print("\n1、IP开始获取")
    myIp = socket.getaddrinfo(domain, 'http')[0][4][0]
    print("最新IP=" + myIp)

    print("\n2、修改IP到DirSvrInfo1.ini配置文件中")
    # 修改 ip 配置信息
    conf.set('ServerInfo1', 'IP', myIp)
    conf.set('ServerInfo1', 'Domain', domain)

    print("\n3、保存更新DirSvrInfo1.ini配置文件")
    # 保存修改后的配置信息到 ini 文件
    conf.write(open(inipath, "r+", encoding="utf-8"))  # r+模式

    print("\n更新完成！\n【请手动关闭,或5秒后自动关闭】")
    time.sleep(5)
