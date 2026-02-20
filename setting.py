# setting.py
import tkinter as tk
from tkinter import messagebox  # 正确导入 messagebox
from button_style2 import create_gradient_button  # 导入样式按钮

def show_settings(parent, settings, save_callback):
    """打开设置窗口"""
    win = tk.Toplevel(parent,bg="#9e95f1")
    win.bg = "#9e95f1"
    win.title("设置")
    win.geometry("600x250")
    win.resizable(False, False)
    win.transient(parent)  # 置顶于父窗口
    win.grab_set()         # 模态窗口

    # Java路径
    tk.Label(win, text="Java (exe) 路径", bg=win.bg).place(x=20, y=20)
    java_var = tk.StringVar(value=settings.get("java_path", ""))
    java_entry = tk.Entry(win, textvariable=java_var, width=60,bg="#c1dcfc")
    java_entry.place(x=20, y=45)

    def save_java():
        settings["java_path"] = java_var.get().strip()
        save_callback()
        messagebox.showinfo("提示", "Java路径已保存", parent=win)

    # 替换为样式按钮
    btn_java = create_gradient_button(win, text="确定", command=save_java, width=80, height=30)
    btn_java.place(x=510, y=40)

    # 服务器jar路径
    tk.Label(win, text="服务器jar路径", bg=win.bg).place(x=20, y=90)
    jar_var = tk.StringVar(value=settings.get("jar_path", ""))
    jar_entry = tk.Entry(win, textvariable=jar_var, width=60,bg="#c1dcfc")
    jar_entry.place(x=20, y=115)

    def save_jar():
        settings["jar_path"] = jar_var.get().strip()
        save_callback()
        messagebox.showinfo("提示", "服务器jar路径已保存", parent=win)

    btn_jar = create_gradient_button(win, text="确定", command=save_jar, width=80, height=30)
    btn_jar.place(x=510, y=110)

    # 关闭按钮
    btn_close = create_gradient_button(win, text="关闭", command=win.destroy, width=80, height=30)
    btn_close.place(x=260, y=180)