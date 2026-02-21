# ui_main.py
import tkinter as tk
from tkinter import scrolledtext
import json
import os
import setting
import map_list
from button_style2 import create_gradient_button
from server_controller import ServerController

# 获取脚本所在目录，用于构建绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(SCRIPT_DIR, "settings.json")

class MindustryLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("MIGO 1.0")
        self.root.geometry("960x540")
        self.root.minsize(800, 500)

        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        self.settings = self.load_settings()
        self.controller = ServerController(
            output_callback=self.append_output,
            status_callback=self.update_status
        )

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_language(self):
        lang_path = os.path.join(SCRIPT_DIR, "language.json")
        with open(lang_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_settings(self):
        """加载设置，若文件不存在则返回默认配置"""
        default_settings = {
            "java": {"java_path": "", "jar_path": ""},
            "color": {
                "windows_bg": "#9e95f1",
                "entry": "#9ec3f6",
                "terminal": "#272f38",
                "text": "#9ec3f6",
                "top_frame_bg": "#9ec3f6"   # 补充缺失的键，避免 KeyError
            }
        }
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载 settings.json 失败: {e}，使用默认配置")
        return default_settings

    def save_settings(self):
        """保存设置到文件"""
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存 settings.json 失败: {e}")

    def update_status(self, text):
        self.status_var.set(text)

    def create_widgets(self):
        # 主容器
        main_frame = tk.Frame(self.root, bg=self.settings["color"]["windows_bg"], padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部按钮区域（使用 get 提供默认值，防止键缺失）
        top_frame_bg = self.settings["color"].get("windows_bg", "#9ec3f6")
        top_frame = tk.Frame(main_frame, bg=top_frame_bg)
        top_frame.pack(fill=tk.X, pady=(0,10))

        lgag = self.load_language()

        self.start_btn = create_gradient_button(top_frame, text=lgag["language"][lgag["user_choice"]]["start_server"],
                                                command=self.start_server,
                                                width=120, height=35)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = create_gradient_button(top_frame, text=lgag["language"][lgag["user_choice"]]["stop_server"],
                                               command=self.stop_server,
                                               width=120, height=35)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.config(state=tk.DISABLED)

        self.setting_btn = create_gradient_button(top_frame, text=lgag["language"][lgag["user_choice"]]["setting"],
                                                  command=self.open_settings,
                                                  width=120, height=35)
        self.setting_btn.pack(side=tk.LEFT, padx=5)

        self.map_list_btn = create_gradient_button(top_frame, text=lgag["language"][lgag["user_choice"]]["map_list"],
                                                   command=self.show_map_list,
                                                   width=120, height=35)
        self.map_list_btn.pack(side=tk.LEFT, padx=5)

        self.game_stop_btn = create_gradient_button(top_frame, text=lgag["language"][lgag["user_choice"]]["stop_game"],
                                                   command=self.stop_game,
                                                   width=120, height=35)
        self.game_stop_btn.pack(side=tk.LEFT, padx=5)

        self.game_start_btn = create_gradient_button(top_frame, text=lgag["language"][lgag["user_choice"]]["start_game"],
                                                   command=self.start_game,
                                                   width=120, height=35)
        self.game_start_btn.pack(side=tk.LEFT, padx=5)

        # 指令输入区域
        cmd_frame = tk.Frame(main_frame, bg=self.settings["color"].get("entry", "#9ec3f6"))
        cmd_frame.pack(fill=tk.X, pady=5)

        self.cmd_entry = tk.Entry(cmd_frame, font=('微软雅黑', 10), bg=self.settings["color"].get("entry", "#c1dcfc"))
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        self.send_btn = create_gradient_button(cmd_frame, text=lgag["language"][lgag["user_choice"]]["enter_command"],
                                               command=self.send_command,
                                               width=100, height=30)
        self.send_btn.pack(side=tk.LEFT)

        # 输出区域
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        self.output_area = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD,
            font=('Consolas', 10), background=self.settings["color"].get("terminal", "#1e1e1e"), foreground=self.settings["color"].get("text", "#9cc5f8"),
            insertbackground='white', borderwidth=1, relief=tk.SUNKEN
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = tk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W, bg=self.settings["color"].get("windows_bg", "#9cc5f8"))
        status_bar.pack(fill=tk.X, pady=(5,0))

    def open_settings(self):
        setting.show_settings(self.root, self.settings, self.save_settings)

    def show_map_list(self):
        if self.controller.process is None:
            self.append_output("错误：服务器未运行，无法获取地图列表\n")
            return
        map_list.show_map_list(self, self.controller.process,
                               self.send_command,
                               self.controller.add_listener,
                               self.controller.remove_listener)

    def start_server(self):
        java = self.settings["java"].get("java_path") or "java"
        jar = self.settings["java"].get("jar_path")
        if not jar:
            self.append_output("错误：未设置服务器jar路径\n")
            return

        if self.controller.start(java, jar):
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.root.after(2000, lambda: self.send_command("host"))

    def stop_server(self):
        self.controller.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def stop_game(self):
        if self.controller.process is None:
            self.append_output("服务器未运行\n")
            return
        self.root.after(20, lambda: self.send_command("pause on"))

    def start_game(self):
        if self.controller.process is None:
            self.append_output("服务器未运行\n")
            return
        self.root.after(20, lambda: self.send_command("pause off"))

    def send_command(self, cmd=None):
        if cmd is None:
            cmd = self.cmd_entry.get()
            if cmd:
                self.controller.send_command(cmd)
                self.cmd_entry.delete(0, tk.END)
        else:
            self.controller.send_command(cmd)

    def append_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def on_closing(self):
        self.controller.exit_gracefully()
        self.root.destroy()