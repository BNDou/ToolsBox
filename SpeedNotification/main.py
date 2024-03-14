import json
import locale
import os.path
import sys
from datetime import datetime

import requests

if __name__ == '__main__':
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    # 读取json文件内容,返回字典格式
    with open(os.path.join(base_dir, "data.json"), 'r', encoding='utf8') as f:
        json_data = json.load(f)

    # 读取文件夹路径
    filePath = json_data["filePath"] + "\\出货记录文本.txt"
    # print(filePath)

    # 读取文本内容
    with open(filePath, 'r', encoding='ansi') as file:
        txt = file.read()

    # 设置语言环境，获取今日日期
    locale.setlocale(locale.LC_CTYPE, 'Chinese')
    time = datetime.now().timetuple()
    today = str(time.tm_year) + "年" + str(time.tm_mon) + "月" + str(time.tm_mday) + "日"
    # 通知内容
    content = txt[txt.find("[" + today + "]"):-1]
    # print(content)

    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    data = {
        "appToken": "AT_XQGRg1wEOkgJnJ99fBT8EDmJpeIy4wnE",
        "content": content,
        "summary": "出货通知",
        "contentType": 1,
        "topicIds": [24731],
        "verifyPay": "false"
    }

    # 如果推送内容content为空，就不推送
    if content:
        response = requests.post(url, headers=headers, json=data)
        # response.encoding = "utf-8"
        # print(response.json())
