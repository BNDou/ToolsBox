'''
Author: BNDou
Date: 2024-06-26 01:09:33
LastEditTime: 2024-06-26 21:47:44
FilePath: \ToolsBox\jjietu\jietu.py
Description: 
'''
import base64
import pyautogui
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template

app = Flask(__name__)
scheduler = BackgroundScheduler()


@app.route('/')
def index():
    img = pyautogui.screenshot(region=None)  # x,y,w,h
    img.save('C:/Users/服务器/Pictures/jietu.png')
    image_path = 'C:/Users/服务器/Pictures/jietu.png'
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read())
    return render_template('index.html', img_base64=str(image_base64)[2:-1])


@app.route('/get_data', methods=['POST'])
def get_data():
    img = pyautogui.screenshot(region=None)  # x,y,w,h
    img.save('C:/Users/服务器/Pictures/jietu.png')
    image_path = 'C:/Users/服务器/Pictures/jietu.png'
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read())
    return render_template('index.html', img_base64=str(image_base64)[2:-1])


if __name__ == '__main__':
    app.run(host="192.168.31.120", port=27018, debug=False)
    # app.run(host="127.0.0.1", port=27018, debug=True)
