# map_list.py
import tkinter as tk
from tkinter import messagebox
import re
from button_style2 import create_gradient_button  # 导入样式按钮
import os
import json
def show_map_list(main_window, process, send_cmd, add_listener, remove_listener):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    SETTINGS_PATH = os.path.join(SCRIPT_DIR, "settings.json")
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)

    win = tk.Toplevel(main_window.root, bg=settings["color"]["windows_bg"])
    win.title("地图列表")
    win.geometry("400x400")
    win.transient(main_window.root)
    win.grab_set()

    # 提示标签：水平填充以消除左侧白边
    label = tk.Label(win, text="正在获取地图列表...", bg=settings["color"]["windows_bg"], font=('微软雅黑', 12))
    label.pack(pady=5, fill='x')

    # 带滚动条的 Canvas，背景色与窗口一致
    canvas = tk.Canvas(win, borderwidth=0, bg=settings["color"]["windows_bg"])
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview, bg=settings["color"]["windows_bg"])
    scrollable_frame = tk.Frame(canvas, bg=settings["color"]["windows_bg"])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # 创建内部窗口并保存ID，用于动态调整宽度
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def _configure_canvas(event):
        # 将内部frame的宽度设置为Canvas的宽度
        canvas.itemconfig(frame_id, width=event.width)

    canvas.bind('<Configure>', _configure_canvas)

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    map_names = []
    collecting = True

    def parse_line(line):
        # 精确匹配地图行：时间戳后至少两个空格，地图名后跟 ": Default / 数字x数字" 或 ": Custom / 数字x数字"
        match = re.search(r'\[\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}\] \[I\]\s{2,}([^:]+): (?:Default|Custom) / \d+x\d+', line)
        if match:
            map_name = match.group(1).strip()
            map_names.append(map_name)
        # 地图目录行作为结束标记
        if "Map directory:" in line:
            return True
        return False

    def listener(line):
        nonlocal collecting
        if not collecting:
            return False
        if not win.winfo_exists():
            return True  # 窗口已关闭，移除监听器
        ret = parse_line(line)
        if ret:
            collecting = False
            win.after(0, update_ui)
            return True
        return False

    def update_ui():
        label.config(text="地图列表：")
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        for name in map_names:
            frame = tk.Frame(scrollable_frame, bg=settings["color"]["entry"])
            frame.pack(fill=tk.X, padx=0, pady=2)

            # 地图名标签：去掉固定宽度，填充剩余空间
            lbl = tk.Label(frame, text=name, anchor="w", bg=settings["color"]["entry"], padx=5)
            lbl.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))

            # 按钮宽度固定
            btn = create_gradient_button(frame, text="切换", command=lambda n=name: switch_map(n), width=60, height=25)
            btn.pack(side=tk.RIGHT, padx=5)

    def switch_map(map_name):
        send_cmd(f"nextmap {map_name}")
        send_cmd("gameover")
        messagebox.showinfo("切换", f"已发送切换至地图 {map_name} 指令", parent=win)

    # 注册监听器
    add_listener(listener)

    def on_close():
        remove_listener(listener)
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)

    # 发送指令
    send_cmd("maps all")

    # 超时处理
    win.after(5000, lambda: check_timeout())

    def check_timeout():
        nonlocal collecting
        if collecting and win.winfo_exists():
            collecting = False
            label.config(text="获取地图列表超时，请检查服务器输出")
            if map_names:
                update_ui()
            remove_listener(listener)