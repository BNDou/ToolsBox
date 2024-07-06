'''
Author: BNDou
Date: 2024-07-07 05:53:05
LastEditTime: 2024-07-07 05:54:41
FilePath: \ToolsBox\showCaptcha\index.py
Description: 
'''
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def captcha():
    return render_template('captcha.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')