"""
color_picker.py
一个可复用的Tkinter调色盘组件，支持HSV颜色空间选择，实时显示RGB和HEX值。
依赖：Pillow (PIL)
"""

import tkinter as tk
from tkinter import font
from PIL import Image, ImageDraw, ImageTk
import colorsys

class ColorPicker(tk.Frame):
    """
    调色盘组件，包含色相条、饱和度/亮度平面以及颜色展示框。
    可嵌入任何Tkinter容器，支持缩放。
    """

    def __init__(self, master, initial_color='#ff0000', scale=1.0, on_color_change=None, **kwargs):
        """
        初始化调色盘。

        :param master: 父容器
        :param initial_color: 初始颜色，支持十六进制字符串（如"#ff0000"）或RGB元组（如(255,0,0)）
        :param scale: 缩放因子，默认为1.0（原始尺寸：总宽度350，总高度280）
        :param on_color_change: 颜色改变时的回调函数，接受一个参数（当前颜色的十六进制字符串）
        :param kwargs: 传递给tk.Frame的其他参数
        """
        super().__init__(master, **kwargs)

        self.scale = scale
        self.on_color_change = on_color_change

        # 颜色空间变量
        self.hue = 0.0          # 0-360
        self.saturation = 1.0   # 0-1
        self.value = 1.0        # 0-1

        # 计算缩放后的尺寸
        self.palette_width = int(220 * scale)
        self.palette_height = int(220 * scale)
        self.bar_width = int(350 * scale)
        self.bar_height = int(40 * scale)
        self.display_width = int(120 * scale)
        self.display_height = int(50 * scale)

        # 设置整体Frame的大小（可选，便于布局）
        self.config(width=int(350 * scale), height=int(280 * scale))
        self.grid_propagate(False)  # 防止子组件改变Frame大小

        # 创建子组件
        self._create_palette()      # 饱和度/亮度平面
        self._create_hue_bar()      # 色相条
        self._create_displays()     # RGB和HEX展示框

        # 设置初始颜色
        self.set_color(initial_color)

    # ----------------------------------------------------------------------
    # 组件创建
    # ----------------------------------------------------------------------
    def _create_palette(self):
        """创建饱和度/亮度选择画布"""
        self.canvas_palette = tk.Canvas(
            self,
            width=self.palette_width,
            height=self.palette_height,
            highlightthickness=1,
            highlightbackground='gray'
        )
        self.canvas_palette.place(x=0, y=0)
        # 绑定鼠标事件
        self.canvas_palette.bind('<Button-1>', self._on_palette_click)
        self.canvas_palette.bind('<B1-Motion>', self._on_palette_drag)
        # 创建一个标记点（用于显示当前选择的位置）
        self.palette_marker = self.canvas_palette.create_oval(
            0, 0, 5*self.scale, 5*self.scale,
            outline='white', width=2
        )

    def _create_hue_bar(self):
        """创建色相选择条画布"""
        self.canvas_hue = tk.Canvas(
            self,
            width=self.bar_width,
            height=self.bar_height,
            highlightthickness=1,
            highlightbackground='gray'
        )
        self.canvas_hue.place(x=0, y=int(240 * self.scale))
        # 绑定鼠标事件
        self.canvas_hue.bind('<Button-1>', self._on_hue_click)
        self.canvas_hue.bind('<B1-Motion>', self._on_hue_drag)
        # 创建一个标记线
        self.hue_marker = self.canvas_hue.create_line(
            0, 0, 0, self.bar_height,
            fill='white', width=3
        )

    def _create_displays(self):
        """创建RGB和HEX展示框"""
        x_offset = int(230 * self.scale)

        # RGB展示框
        self.rgb_label = tk.Label(
            self,
            width=int(120 * self.scale / 10),  # 字符宽度近似
            height=int(50 * self.scale / 20),
            relief='solid',
            borderwidth=1,
            text='RGB:',
            anchor='w',
            font=font.Font(size=int(10 * self.scale))
        )
        self.rgb_label.place(x=x_offset, y=0, width=self.display_width, height=self.display_height)

        # HEX展示框
        self.hex_label = tk.Label(
            self,
            width=int(120 * self.scale / 10),
            height=int(50 * self.scale / 20),
            relief='solid',
            borderwidth=1,
            text='HEX:',
            anchor='w',
            font=font.Font(size=int(10 * self.scale))
        )
        self.hex_label.place(x=x_offset, y=int(85 * self.scale), width=self.display_width, height=self.display_height)

    # ----------------------------------------------------------------------
    # 事件处理
    # ----------------------------------------------------------------------
    def _on_hue_click(self, event):
        """点击色相条"""
        self._update_hue_from_event(event)
        self._update_palette_image()   # 色相改变，需重新绘制调色板
        self._update_color()

    def _on_hue_drag(self, event):
        """拖拽色相条"""
        self._update_hue_from_event(event)
        self._update_palette_image()
        self._update_color()

    def _update_hue_from_event(self, event):
        """根据事件坐标更新色相值"""
        x = max(0, min(event.x, self.bar_width - 1))
        # 色相范围0-360，线性映射到画布宽度
        self.hue = (x / (self.bar_width - 1)) * 360.0
        # 移动标记线
        self.canvas_hue.coords(self.hue_marker, x, 0, x, self.bar_height)

    def _on_palette_click(self, event):
        """点击调色板"""
        self._update_sv_from_event(event)
        self._update_color()

    def _on_palette_drag(self, event):
        """拖拽调色板"""
        self._update_sv_from_event(event)
        self._update_color()

    def _update_sv_from_event(self, event):
        """根据事件坐标更新饱和度和亮度"""
        x = max(0, min(event.x, self.palette_width - 1))
        y = max(0, min(event.y, self.palette_height - 1))
        # 饱和度从左到右增加
        self.saturation = x / (self.palette_width - 1)
        # 亮度从上到下增加（顶部最亮，底部最暗）
        self.value = 1.0 - (y / (self.palette_height - 1))

        # 移动标记点（圆圈中心）
        marker_size = 5 * self.scale
        self.canvas_palette.coords(
            self.palette_marker,
            x - marker_size/2, y - marker_size/2,
            x + marker_size/2, y + marker_size/2
        )

    # ----------------------------------------------------------------------
    # 颜色更新与绘图
    # ----------------------------------------------------------------------
    def _update_color(self):
        """更新颜色展示，触发回调"""
        rgb = self.get_rgb()
        hex_str = self.get_hex()

        # 更新展示标签背景和文本
        bg_color = hex_str
        fg_color = 'white' if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) < 140 else 'black'
        self.rgb_label.config(
            text=f'RGB: {rgb[0]},{rgb[1]},{rgb[2]}',
            bg=bg_color,
            fg=fg_color
        )
        self.hex_label.config(
            text=f'HEX: {hex_str}',
            bg=bg_color,
            fg=fg_color
        )

        # 调用回调
        if self.on_color_change:
            self.on_color_change(hex_str)

    def _update_palette_image(self):
        """根据当前色相重新绘制调色板图像"""
        # 生成PIL图像
        img = Image.new('RGB', (self.palette_width, self.palette_height))
        draw = ImageDraw.Draw(img)

        # 逐像素绘制（可优化，但220x220可接受）
        for x in range(self.palette_width):
            s = x / (self.palette_width - 1)
            for y in range(self.palette_height):
                v = 1.0 - (y / (self.palette_height - 1))  # 亮度从上到下递增
                # HSV转RGB
                r, g, b = colorsys.hsv_to_rgb(self.hue/360.0, s, v)
                draw.point((x, y), fill=(int(r*255), int(g*255), int(b*255)))

        # 转换为Tkinter图像
        self.palette_image = ImageTk.PhotoImage(img)
        self.canvas_palette.create_image(0, 0, image=self.palette_image, anchor='nw')

    def _update_hue_bar_image(self):
        """绘制色相条图像（只需一次，因为色相条不依赖当前颜色）"""
        img = Image.new('RGB', (self.bar_width, self.bar_height))
        draw = ImageDraw.Draw(img)
        for x in range(self.bar_width):
            hue = (x / (self.bar_width - 1)) * 360.0
            r, g, b = colorsys.hsv_to_rgb(hue/360.0, 1.0, 1.0)
            draw.rectangle([x, 0, x+1, self.bar_height], fill=(int(r*255), int(g*255), int(b*255)))
        self.hue_bar_image = ImageTk.PhotoImage(img)
        self.canvas_hue.create_image(0, 0, image=self.hue_bar_image, anchor='nw')

    # ----------------------------------------------------------------------
    # 公共方法
    # ----------------------------------------------------------------------
    def get_rgb(self):
        """获取当前颜色的RGB元组（0-255）"""
        r, g, b = colorsys.hsv_to_rgb(self.hue/360.0, self.saturation, self.value)
        return (int(r*255), int(g*255), int(b*255))

    def get_hex(self):
        """获取当前颜色的十六进制字符串（如"#ff0000"）"""
        rgb = self.get_rgb()
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    def get_hsv(self):
        """获取当前颜色的HSV元组（h:0-360, s:0-1, v:0-1）"""
        return (self.hue, self.saturation, self.value)

    def set_color(self, color):
        """
        设置当前颜色。支持十六进制字符串或RGB元组。
        :param color: 如"#ff0000" 或 (255,0,0)
        """
        if isinstance(color, str):
            if color.startswith('#'):
                color = color.lstrip('#')
                rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            else:
                raise ValueError("Unsupported color string format")
        elif isinstance(color, (tuple, list)) and len(color) == 3:
            rgb = tuple(color)
        else:
            raise TypeError("color must be a hex string or RGB tuple")

        # RGB转HSV
        r, g, b = [x/255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        self.hue = h * 360.0
        self.saturation = s
        self.value = v

        # 更新界面
        self._update_hue_bar_image()          # 绘制色相条（只需一次，但set_color后可能首次显示）
        self._update_palette_image()           # 调色板图像依赖色相，需更新
        self._update_color()

        # 同步标记位置
        self._sync_markers()

    def _sync_markers(self):
        """根据当前h,s,v更新标记位置"""
        # 色相条标记
        x_hue = int((self.hue / 360.0) * (self.bar_width - 1))
        self.canvas_hue.coords(self.hue_marker, x_hue, 0, x_hue, self.bar_height)

        # 调色板标记
        x_s = int(self.saturation * (self.palette_width - 1))
        y_v = int((1.0 - self.value) * (self.palette_height - 1))
        marker_size = 5 * self.scale
        self.canvas_palette.coords(
            self.palette_marker,
            x_s - marker_size/2, y_v - marker_size/2,
            x_s + marker_size/2, y_v + marker_size/2
        )


# --------------------------------------------------------------------------
# 使用示例
# --------------------------------------------------------------------------
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Color Picker Demo")

    # 创建调色盘（缩放1.5倍）
    picker = ColorPicker(root, initial_color='#3a6ea5', scale=1.5,
                         on_color_change=lambda c: print("颜色改变:", c))
    picker.pack(padx=10, pady=10)

    # 添加一个标签显示当前颜色
    label = tk.Label(root, text="当前颜色")
    label.pack()

    root.mainloop()