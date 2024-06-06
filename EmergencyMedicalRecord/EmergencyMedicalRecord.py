'''
Author: BNDou
Date: 2024-06-07 00:10:13
LastEditTime: 2024-06-07 07:43:12
FilePath: \ToolsBox\EmergencyMedicalRecord\EmergencyMedicalRecord.py
Description: 
'''
import os
from tkinter import filedialog
from openpyxl import load_workbook
import pandas as pd
import tkinter as tk
from tkinter import END, Button, Entry, Label, Tk, messagebox, ttk

# # 读取 Excel 文件，一个包含法定节假日的列表
# curpath = os.path.dirname(os.path.realpath(sys.argv[0]))
# # 文件路径（组合、相对路径）
# file_path = os.path.join(curpath, "急诊病历登记.xlsx")


def calculate_days(date1, date2):
    '''
    计算两个日期之间的天数
    date1: 出院日期
    date2: 送报病历日期
    return: 两个日期之间的天数
    '''
    jjr = pd.read_excel(file_path_label.cget("text"), sheet_name="节假日")
    # 提取节假日列表
    holidays = jjr["节假日"].tolist()
    # 计算两个日期之间的天数
    days = (date1 - date2).days
    while date1 > date2:
        if date1 in holidays:
            days -= 1
        date1 -= pd.Timedelta(days=1)
    return days


def append_row(file_path, sheet_name, data):
    workbook = load_workbook(file_path)
    sheet = workbook[sheet_name]
    # 整行追加写入 Excel
    sheet.append(data)
    workbook.save(file_path)


def onEnter(event):
    '''
    回车键事件
    '''
    submit_data()


def submit_data():
    '''
    录入数据
    '''
    # 获取输入
    file_path = file_path_label.cget("text")
    emergency_number = emergency_number_entry.get()
    patient_name = patient_name_entry.get()
    gender = gender_entry.get()
    phone = phone_entry.get()
    diagnosis = diagnosis_entry.get()
    discharge_date = discharge_date_entry.get()
    report_date = report_date_entry.get()

    # 检查输入是否有效
    if not file_path:
        messagebox.showerror("错误", "请选择急诊表格文件")
        return
    elif not emergency_number or not patient_name or not gender or not phone or not diagnosis or not discharge_date or not report_date:
        messagebox.showerror("错误", "请填写所有项目")
        return
    elif not gender in ["0", "1"]:
        messagebox.showerror("错误", "“性别” 格式错误！\n请输入 0 或 1，分别代表 “男” 和 “女")
        return
    elif not len(phone_entry.get()) == 11:  # 检查手机号是否有效
        messagebox.showerror("错误", "“手机号” 格式错误")
        return
    elif discharge_date > report_date:  # 检查出院日期和送报病历日期填写是否有效
        messagebox.showerror("错误", "“出院日期” 要在 “送报日期” 之前")
        return
    try:
        report_date = pd.to_datetime(report_date)
        discharge_date = pd.to_datetime(discharge_date)
        days = calculate_days(report_date, discharge_date)
    except ValueError:
        messagebox.showerror("错误", "“出院日期” 和 “送报日期” 格式错误")
        return

    if gender == "0":
        gender = "男"
    elif gender == "1":
        gender = "女"

    # 录入数据
    input_data = [
        emergency_number,
        patient_name,
        gender,
        int(phone),
        diagnosis,
        discharge_date.strftime('%Y-%m-%d'),
        report_date.strftime('%Y-%m-%d'),
        int(days),
    ]
    print(input_data)
    print(radio_button_var.get())
    # 写入 Excel
    if radio_button_var.get() == "单":
        append_row(file_path, "单", input_data)
    elif radio_button_var.get() == "留":
        append_row(file_path, "留", input_data)
    elif radio_button_var.get() == "重":
        append_row(file_path, "重", input_data)
    # 提示成功
    messagebox.showinfo("成功", "数据录入成功")


def select_file():
    '''
    选择 Excel 文件
    '''
    file_path = filedialog.askopenfilename(filetypes=[("Excel files",
                                                       "*.xlsx;*.xls")])
    file_path_label.config(text=os.path.abspath(file_path))


def center_window(window, width, height):
    '''
    窗口居中
    '''
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry(f"{width}x{height}+{int(x)}+{int(y)}")


root = Tk()
center_window(root, 350, 350)
root.title("急诊病历登记 APP")

select_file_button = tk.Button(root, text="选择文件", command=select_file)
select_file_button.grid(row=0, column=0, padx=5, pady=5)

file_path_label = tk.Label(root, text="", fg="red", wraplength=200)
file_path_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

Label(root, text="急诊号:").grid(row=1, column=0, padx=5, pady=5)
Label(root, text="患者姓名:").grid(row=2, column=0, padx=5, pady=5)
Label(root, text="性别\n(0-男,1-女):").grid(row=3, column=0, padx=5, pady=5)
Label(root, text="手机号(11位):").grid(row=4, column=0, padx=5, pady=5)
Label(root, text="诊断:").grid(row=5, column=0, padx=5, pady=5)
Label(root, text="出院日期\n(格式:20230101):").grid(row=6, column=0, padx=5, pady=5)
Label(root, text="送报日期\n(格式:20230101):").grid(row=7, column=0, padx=5, pady=5)

# 创建输入框
emergency_number_entry = Entry(root)
patient_name_entry = Entry(root)
gender_entry = Entry(root)
phone_entry = Entry(root)
diagnosis_entry = Entry(root)
discharge_date_entry = Entry(root)
report_date_entry = Entry(root)

# 将输入框添加到布局中
emergency_number_entry.grid(row=1, column=1, padx=5, pady=5)
patient_name_entry.grid(row=2, column=1, padx=5, pady=5)
gender_entry.grid(row=3, column=1, padx=5, pady=5)
phone_entry.grid(row=4, column=1, padx=5, pady=5)
diagnosis_entry.grid(row=5, column=1, padx=5, pady=5)
discharge_date_entry.grid(row=6, column=1, padx=5, pady=5)
report_date_entry.grid(row=7, column=1, padx=5, pady=5)

# 创建单选按钮
radio_button_var = tk.StringVar()
radio_button_var.set("单")  # 设置默认选项为“单”

radio_button1 = ttk.Radiobutton(root,
                                text="单",
                                variable=radio_button_var,
                                value="单")
radio_button1.grid(row=1, column=2, padx=5, pady=5)

radio_button2 = ttk.Radiobutton(root,
                                text="留",
                                variable=radio_button_var,
                                value="留")
radio_button2.grid(row=2, column=2, padx=5, pady=5)

radio_button3 = ttk.Radiobutton(root,
                                text="重",
                                variable=radio_button_var,
                                value="重")
radio_button3.grid(row=3, column=2, padx=5, pady=5)

calculate_button = Button(root, text="录入", command=submit_data)
root.bind("<Return>", onEnter)
calculate_button.grid(row=4, column=2, rowspan=4, padx=5, pady=5)

gender_entry.bind(
    "<KeyRelease>", lambda event: gender_entry.delete(0, END) if
    not gender_entry.get().isdigit() or len(gender_entry.get()) > 1 else None)
phone_entry.bind(
    "<KeyRelease>",
    lambda event: phone_entry.delete(0, END) if not phone_entry.get().isdigit(
    ) or len(phone_entry.get()) > 11 else None)

root.mainloop()
