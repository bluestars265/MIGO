# server_controller.py
import subprocess
import threading

class ServerController:
    def __init__(self, output_callback, status_callback):
        """
        :param output_callback: 处理输出行的函数，接受一个字符串参数
        :param status_callback: 更新状态栏的函数，接受一个字符串参数
        """
        self.process = None
        self.running = False
        self.output_listeners = []
        self.output_callback = output_callback
        self.status_callback = status_callback

    def start(self, java, jar):
        """启动服务器进程"""
        cmd = [java, "-jar", jar]
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.output_callback(f"服务器启动：{' '.join(cmd)}\n")
            self.running = True
            self.status_callback("服务器运行中")
            threading.Thread(target=self._read_output, daemon=True).start()
            return True
        except Exception as e:
            self.output_callback(f"启动失败：{e}\n")
            return False

    def stop(self):
        """停止服务器进程"""
        if self.process:
            self.process.terminate()
            self.process = None
            self.output_callback("服务器已停止\n")
            self.running = False
            self.output_listeners.clear()
            self.status_callback("已停止")

    def send_command(self, cmd):
        """发送指令到服务器"""
        if not self.process:
            self.output_callback("服务器未运行\n")
            return
        if cmd:
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()
            self.output_callback(f"> {cmd}\n")

    def add_listener(self, listener):
        """添加输出监听器（用于地图列表等）"""
        self.output_listeners.append(listener)

    def remove_listener(self, listener):
        if listener in self.output_listeners:
            self.output_listeners.remove(listener)

    def _read_output(self):
        """后台读取服务器输出"""
        while self.running and self.process:
            line = self.process.stdout.readline()
            if line:
                # 通过回调在主线程处理输出
                self.output_callback(line)
                # 调用监听器
                remaining = []
                for listener in self.output_listeners:
                    if not listener(line):
                        remaining.append(listener)
                self.output_listeners = remaining
            else:
                break
        if self.process:
            self.process = None
            self.running = False
            self.status_callback("已停止")

    def exit_gracefully(self, timeout=5):
        """发送 exit 并等待进程结束"""
        if self.process and self.running:
            self.running = False
            self.send_command("exit")
            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.process.terminate()