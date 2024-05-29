'''
Author       : BNDou
Date         : 2024/4/1 21:15
File         : chuangkou
Description  : 
'''
import win32process
from pywinauto import Desktop
from pywinauto.keyboard import SendKeys
from pywinauto.mouse import click
import win32gui
import win32con

# 获取进程句柄
hwnd = win32gui.FindWindow(None, "QQSpeedServer")

# 获取进程 ID
_, pid = win32process.GetWindowThreadProcessId(hwnd)

# 获取输入/输出/错误管道
stdin, stdout, stderr = Desktop(backend="uia").window(process=pid).get_controls("Stdin", "Stdout", "Stderr")

# 模拟键盘输入
SendKeys("zx", with_spaces=True)

# 模拟鼠标点击
click(coords=(100, 100))

# # 获取输入/输出/错误管道
# stdin = process.stdin
# stdout = process.stdout
# stderr = process.stderr
#
# # 读取输出和错误
# output, error = stdout.read(), stderr.read()
#
# # 打印输出和错误
# print(output.decode('gbk'))
# print(error.decode('gbk'))


# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QLineEdit, QVBoxLayout
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import Qt
#
# class MyApp(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#     def initUI(self):
#         self.setGeometry(300, 300, 400, 300)
#         self.setWindowTitle('Calculator')
#
#         self.text_edit = QTextEdit(self)
#         self.text_edit.setReadOnly(True)
#         self.text_edit.setStyleSheet("QTextEdit { background-color: black; color: white; }")
#         self.text_edit.resize(200, 150)
#         self.text_edit.move(100, 50)
#
#         self.input1 = QLineEdit(self)
#         self.input1.resize(50, 20)
#         self.input1.move(100, 100)
#
#         self.input2 = QLineEdit(self)
#         self.input2.resize(50, 20)
#         self.input2.move(200, 100)
#
#         self.button = QPushButton('Calculate', self)
#         self.button.clicked.connect(self.calculate)
#         self.button.resize(self.button.sizeHint())
#         self.button.move(150, 150)
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.text_edit)
#         layout.addWidget(self.input1)
#         layout.addWidget(self.input2)
#         layout.addWidget(self.button)
#
#         self.setLayout(layout)
#
#     def calculate(self):
#         try:
#             a = int(self.input1.text())
#             b = int(self.input2.text())
#             result = a + b
#             self.text_edit.setHtml(f"{a} + {b} = {result}")
#         except ValueError:
#             self.text_edit.setHtml("<font color='red'>Error</font>")
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = MyApp()
#     ex.show()
#     sys.exit(app.exec_())
