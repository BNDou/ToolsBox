# -*- coding: utf-8 -*-
'''
Author       : BNDou
Date         : 2024/3/19 0:41
File         : SpeedServerClientUpdate/SpeedClientUpdate.py
Description  :
'''
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
    print("读取配置文件...")
    conf = configparser.ConfigParser()
    conf.read(inipath, encoding="utf-8")
    # 获取配置文件中的IP地址
    ServerInfo1_IP = conf.get('ServerInfo1', 'IP')
    ServerInfo1_Domain = conf.get('ServerInfo1', 'Domain')
    print(f'IP={ServerInfo1_IP}\nDomain={ServerInfo1_Domain}')

    domain = ''  # 填写域名地址

    print("\n1、IP开始获取")
    # 获取域名对应的IP地址
    myIp = socket.getaddrinfo(domain, 'http')[0][4][0]

    print("\n2、检查IP是否与配置文件中的IP相同")

    # 比较IP地址是否相同
    if any(s == myIp for s in [str(ServerInfo1_IP), str(ServerInfo1_Domain)]):
        print("IP相同，无需更新！\n【请手动关闭,或5秒后自动关闭】")
    else:
        print(f"最新IP={myIp}\nIP不同，需要更新\n\n3、修改IP到DirSvrInfo1.ini配置文件中")
        # 修改 ip 配置信息
        conf.set('ServerInfo1', 'IP', myIp)
        conf.set('ServerInfo1', 'Domain', domain)

        print("\n4、保存更新DirSvrInfo1.ini配置文件")
        # 保存修改后的配置信息到 ini 文件
        conf.write(open(inipath, "r+", encoding="utf-8"))  # r+模式
        print("\n更新完成！\n【请手动关闭,或5秒后自动关闭】")

    time.sleep(5)
