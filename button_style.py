# button_style.py
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

class GradientButton:
    def __init__(self, parent, text, command, width=120, height=30):
        self.parent = parent
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        # 默认渐变颜色
        self.normal_bottom = (135, 206, 235)  # 天蓝色
        self.normal_top    = (255, 255, 255)  # 白色
        self.pressed_bottom = (255, 215, 0)   # 金色
        self.pressed_top    = (255, 255, 224) # 浅金色
        self.border_color = (64, 64, 64)      # 深灰色边框
        self.border_width = 3
        self.radius = min(width, height) // 6
        self.btn = None
        self.normal_image = None
        self.pressed_image = None
        self._command = command

    def _parse_color(self, color):
        """将颜色参数转换为RGB元组，支持HEX字符串或RGB元组"""
        if isinstance(color, tuple) and len(color) == 3:
            return color
        elif isinstance(color, str) and color.startswith('#'):
            color = color.lstrip('#')
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        else:
            raise ValueError("颜色必须是RGB元组或HEX字符串")

    def _create_rounded_image(self, bottom_color, top_color):
        """生成带圆角和边框的渐变图像（RGBA格式）"""
        width, height = self.width, self.height
        border_color = self.border_color
        border_width = self.border_width
        radius = self.radius

        # 1. 创建 RGB 基础图像，先用边框色填充
        rgb_img = Image.new('RGB', (width, height), color=border_color)
        draw = ImageDraw.Draw(rgb_img)

        # 2. 绘制整个按钮的圆角背景（深灰色边框区域）
        draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=radius, fill=border_color)

        # 3. 计算内部渐变区域（向内偏移 border_width）
        inner_x1 = border_width
        inner_y1 = border_width
        inner_x2 = width - border_width - 1
        inner_y2 = height - border_width - 1
        inner_width = inner_x2 - inner_x1 + 1
        inner_height = inner_y2 - inner_y1 + 1
        inner_radius = max(0, radius - border_width)

        if inner_width > 0 and inner_height > 0:
            # 创建临时图像用于内部渐变
            inner_img = Image.new('RGB', (inner_width, inner_height))
            inner_draw = ImageDraw.Draw(inner_img)

            # 绘制垂直渐变（从下到上）
            for y in range(inner_height):
                ratio = y / (inner_height - 1) if inner_height > 1 else 0
                r = int(bottom_color[0] * (1 - ratio) + top_color[0] * ratio)
                g = int(bottom_color[1] * (1 - ratio) + top_color[1] * ratio)
                b = int(bottom_color[2] * (1 - ratio) + top_color[2] * ratio)
                inner_draw.line([(0, y), (inner_width-1, y)], fill=(r, g, b))

            # 为内部图像创建圆角 Alpha 蒙版
            inner_alpha = Image.new('L', (inner_width, inner_height), 0)
            inner_alpha_draw = ImageDraw.Draw(inner_alpha)
            inner_alpha_draw.rounded_rectangle(
                [(0, 0), (inner_width-1, inner_height-1)],
                radius=inner_radius, fill=255
            )

            inner_rgba = inner_img.convert('RGBA')
            inner_rgba.putalpha(inner_alpha)

            rgb_img.paste(inner_rgba, (inner_x1, inner_y1), inner_rgba)

        # 4. 创建整体 Alpha 通道
        alpha = Image.new('L', (width, height), 0)
        alpha_draw = ImageDraw.Draw(alpha)
        alpha_draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=radius, fill=255)

        rgb_img.putalpha(alpha)

        return ImageTk.PhotoImage(rgb_img)

    def create_button(self):
        # 生成普通状态和按下状态的图像
        self.normal_image = self._create_rounded_image(self.normal_bottom, self.normal_top)
        self.pressed_image = self._create_rounded_image(self.pressed_bottom, self.pressed_top)

        # 创建按钮
        self.btn = tk.Button(
            self.parent,
            text=self.text,
            image=self.normal_image,
            compound='center',
            command=None,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0
        )
        self.btn.normal_image = self.normal_image
        self.btn.pressed_image = self.pressed_image
        self.btn._command = self.command

        def on_press(event):
            if self.btn['state'] != tk.DISABLED:
                self.btn.config(image=self.pressed_image)

        def on_release(event):
            if self.btn['state'] != tk.DISABLED:
                self.btn.config(image=self.normal_image)
                if self.btn._command:
                    self.btn._command()

        self.btn.bind('<ButtonPress-1>', on_press)
        self.btn.bind('<ButtonRelease-1>', on_release)

        return self.btn

    def update_button_color(self, color):
        """更新普通状态颜色（设置底部颜色，顶部颜色保持白色）"""
        self.normal_bottom = self._parse_color(color)
        self.normal_top = (255, 255, 255)  # 顶部固定白色
        self.normal_image = self._create_rounded_image(self.normal_bottom, self.normal_top)
        if self.btn:
            self.btn.normal_image = self.normal_image
            self.btn.config(image=self.normal_image)

    def update_button_down_color(self, color):
        """更新按下状态颜色（设置底部颜色，顶部颜色保持浅金色）"""
        self.pressed_bottom = self._parse_color(color)
        self.pressed_top = (255, 255, 224)  # 顶部固定浅金色
        self.pressed_image = self._create_rounded_image(self.pressed_bottom, self.pressed_top)
        if self.btn:
            self.btn.pressed_image = self.pressed_image

# 保持向后兼容的函数
def create_gradient_button(parent, text, command, width=120, height=30):
    button = GradientButton(parent, text, command, width, height)
    return button.create_button()