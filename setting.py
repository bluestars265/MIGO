# setting.py
import tkinter as tk
import json
import os
from tkinter import messagebox
from button_style2 import create_gradient_button  # 你的样式按钮

def show_settings(parent, settings, save_callback):
    # 加载语言文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lang_path = os.path.join(script_dir, "language.json")
    with open(lang_path, "r", encoding="utf-8") as f:
        lgag = json.load(f)

    # 创建设置窗口
    win = tk.Toplevel(parent, bg=settings["color"]["windows_bg"])
    win.title(lgag["language"][lgag["user_choice"]]["setting"])
    win.geometry("650x400")  # 高度增加以适应 grid 布局
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()

    # 配置 grid 列权重
    win.columnconfigure(0, weight=0)  # 标签列
    win.columnconfigure(1, weight=1)  # 输入框列
    win.columnconfigure(2, weight=0)  # 按钮列

    row = 0
    # ------------------ Java 路径 ------------------
    tk.Label(win, text=lgag["language"][lgag["user_choice"]]["java_exe_path"],
             bg=settings["color"]["windows_bg"], fg='black').grid(row=row, column=0, sticky='w', padx=10, pady=8)
    java_var = tk.StringVar(value=settings["java"].get("java_path", ""))
    java_entry = tk.Entry(win, textvariable=java_var, width=50,
                          bg=settings["color"]["entry"])
    java_entry.grid(row=row, column=1, padx=5, pady=8, sticky='ew')

    def save_java():
        settings["java"]["java_path"] = java_var.get().strip()
        save_callback()
        messagebox.showinfo("提示", "Java路径已保存", parent=win)

    btn_java = create_gradient_button(win, text=lgag["language"][lgag["user_choice"]]["apply"],
                                      command=save_java, width=80, height=30)
    btn_java.grid(row=row, column=2, padx=10, pady=8)
    row += 1

    # ------------------ 服务器 jar 路径 ------------------
    tk.Label(win, text=lgag["language"][lgag["user_choice"]]["server_jar_path"],
             bg=settings["color"]["windows_bg"], fg='black').grid(row=row, column=0, sticky='w', padx=10, pady=8)
    jar_var = tk.StringVar(value=settings["java"].get("jar_path", ""))
    jar_entry = tk.Entry(win, textvariable=jar_var, width=50,
                         bg=settings["color"]["entry"])
    jar_entry.grid(row=row, column=1, padx=5, pady=8, sticky='ew')

    def save_jar():
        settings["java"]["jar_path"] = jar_var.get().strip()
        save_callback()
        messagebox.showinfo("提示", "服务器jar路径已保存", parent=win)

    btn_jar = create_gradient_button(win, text=lgag["language"][lgag["user_choice"]]["apply"],
                                     command=save_jar, width=80, height=30)
    btn_jar.grid(row=row, column=2, padx=10, pady=8)
    row += 1

    # ------------------ 窗口背景色 ------------------
    tk.Label(win, text=lgag["language"][lgag["user_choice"]]["windows_bg_color"],
             bg=settings["color"]["windows_bg"], fg='black').grid(row=row, column=0, sticky='w', padx=10, pady=8)
    wds_bg = tk.StringVar(value=settings["color"].get("windows_bg", ""))
    wds_entry = tk.Entry(win, textvariable=wds_bg, width=50,
                         bg=settings["color"]["entry"])
    wds_entry.grid(row=row, column=1, padx=5, pady=8, sticky='ew')

    def save_wds_bg():
        settings["color"]["windows_bg"] = wds_bg.get().strip()
        save_callback()
        messagebox.showinfo("提示", "窗口背景色已保存", parent=win)

    btn_wds_bg = create_gradient_button(win, text=lgag["language"][lgag["user_choice"]]["apply"],
                                        command=save_wds_bg, width=80, height=30)
    btn_wds_bg.grid(row=row, column=2, padx=10, pady=8)
    row += 1

    # ------------------ 终端背景色（对应 settings.json 中的 "terminal"） ------------------
    tk.Label(win, text=lgag["language"][lgag["user_choice"]]["terminal_bg_color"],
             bg=settings["color"]["windows_bg"], fg='black').grid(row=row, column=0, sticky='w', padx=10, pady=8)
    term_bg = tk.StringVar(value=settings["color"].get("terminal", ""))
    term_bg_entry = tk.Entry(win, textvariable=term_bg, width=50,
                             bg=settings["color"]["entry"])
    term_bg_entry.grid(row=row, column=1, padx=5, pady=8, sticky='ew')

    def save_term_bg():
        settings["color"]["terminal"] = term_bg.get().strip()
        save_callback()
        messagebox.showinfo("提示", "终端背景色已保存", parent=win)

    btn_term_bg = create_gradient_button(win, text=lgag["language"][lgag["user_choice"]]["apply"],
                                         command=save_term_bg, width=80, height=30)
    btn_term_bg.grid(row=row, column=2, padx=10, pady=8)
    row += 1

    # ------------------ 终端字体颜色（对应 settings.json 中的 "text"） ------------------
    tk.Label(win, text=lgag["language"][lgag["user_choice"]]["terminal_font_color"],
             bg=settings["color"]["windows_bg"], fg='black').grid(row=row, column=0, sticky='w', padx=10, pady=8)
    term_fg = tk.StringVar(value=settings["color"].get("text", ""))
    term_fg_entry = tk.Entry(win, textvariable=term_fg, width=50,
                             bg=settings["color"]["entry"])
    term_fg_entry.grid(row=row, column=1, padx=5, pady=8, sticky='ew')

    def save_term_fg():
        settings["color"]["text"] = term_fg.get().strip()
        save_callback()
        messagebox.showinfo("提示", "终端字体颜色已保存", parent=win)

    btn_term_fg = create_gradient_button(win, text=lgag["language"][lgag["user_choice"]]["apply"],
                                         command=save_term_fg, width=80, height=30)
    btn_term_fg.grid(row=row, column=2, padx=10, pady=8)
    row += 1

    # ------------------ 输入框颜色（对应 settings.json 中的 "entry"） ------------------
    tk.Label(win, text=lgag["language"][lgag["user_choice"]]["entry_color"],
             bg=settings["color"]["windows_bg"], fg='black').grid(row=row, column=0, sticky='w', padx=10, pady=8)
    entry_bg = tk.StringVar(value=settings["color"].get("entry", ""))
    entry_bg_entry = tk.Entry(win, textvariable=entry_bg, width=50,
                             bg=settings["color"]["entry"])
    entry_bg_entry.grid(row=row, column=1, padx=5, pady=8, sticky='ew')

    def save_entry_bg():
        settings["color"]["entry"] = entry_bg.get().strip()
        save_callback()
        messagebox.showinfo("提示", "输入框背景色已保存", parent=win)

    btn_entry_bg = create_gradient_button(win, text=lgag["language"][lgag["user_choice"]]["apply"],
                                         command=save_entry_bg, width=80, height=30)
    btn_entry_bg.grid(row=row, column=2, padx=10, pady=8)
    row += 1


    # ------------------ 关闭按钮（跨列居中） ------------------
    btn_close = create_gradient_button(win, text=lgag["language"][lgag["user_choice"]]["close"],
                                       command=win.destroy, width=80, height=30)
    btn_close.grid(row=row, column=0, columnspan=3, pady=20)