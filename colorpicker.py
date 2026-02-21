import tkinter as tk
from tkinter import font
from PIL import Image, ImageDraw, ImageTk
import colorsys

class ColorPicker(tk.Frame):
    """调色盘组件，包含色相条、饱和度/亮度平面及颜色预览块。"""

    def __init__(self, master, initial_color='#ff0000', scale=1.0,
                 on_color_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.scale = scale
        self.on_color_change = on_color_change

        self.hue = 0.0
        self.saturation = 1.0
        self.value = 1.0

        # 基础尺寸（未缩放）
        base_palette = 200
        base_bar_width = 200
        base_bar_height = 30
        base_display_width = 90
        base_display_height = 35
        gap = 5

        # 缩放后尺寸
        self.palette_width = int(base_palette * scale)
        self.palette_height = int(base_palette * scale)
        self.bar_width = int(base_bar_width * scale)
        self.bar_height = int(base_bar_height * scale)
        self.display_width = int(base_display_width * scale)
        self.display_height = int(base_display_height * scale)
        self.gap = int(gap * scale)

        # 整体框架尺寸
        total_width = self.palette_width + self.display_width + 3 * self.gap
        total_height = self.palette_height + self.bar_height + 3 * self.gap
        self.config(width=total_width, height=total_height)
        self.grid_propagate(False)

        # 创建字体（微软雅黑，按比例缩放）
        self.label_font = font.Font(family='Microsoft YaHei', size=int(10 * scale))

        self._create_palette()
        self._create_hue_bar()
        self._create_displays()

        self.set_color(initial_color)

    # ------------------------------------------------------------------
    def _create_palette(self):
        self.canvas_palette = tk.Canvas(self, width=self.palette_width,
                                        height=self.palette_height,
                                        highlightthickness=1,
                                        highlightbackground='gray')
        self.canvas_palette.place(x=self.gap, y=self.gap)
        self.canvas_palette.bind('<Button-1>', self._on_palette_click)
        self.canvas_palette.bind('<B1-Motion>', self._on_palette_drag)

        marker_size = 5 * self.scale
        self.palette_marker = self.canvas_palette.create_oval(
            0, 0, marker_size, marker_size,
            outline='white', width=2)

    def _create_hue_bar(self):
        y = self.gap + self.palette_height + self.gap
        self.canvas_hue = tk.Canvas(self, width=self.bar_width,
                                    height=self.bar_height,
                                    highlightthickness=1,
                                    highlightbackground='gray')
        self.canvas_hue.place(x=self.gap, y=y)
        self.canvas_hue.bind('<Button-1>', self._on_hue_click)
        self.canvas_hue.bind('<B1-Motion>', self._on_hue_drag)

        self.hue_marker = self.canvas_hue.create_line(
            0, 0, 0, self.bar_height, fill='white', width=3)

    def _create_displays(self):
        x = self.gap + self.palette_width + self.gap
        y = self.gap

        # R 标签
        self.r_label = tk.Label(self, text='R:', anchor='w',
                                relief='solid', borderwidth=1,
                                font=self.label_font, bg='lightgray')
        self.r_label.place(x=x, y=y,
                           width=self.display_width,
                           height=self.display_height)
        y += self.display_height + self.gap

        # G 标签
        self.g_label = tk.Label(self, text='G:', anchor='w',
                                relief='solid', borderwidth=1,
                                font=self.label_font, bg='lightgray')
        self.g_label.place(x=x, y=y,
                           width=self.display_width,
                           height=self.display_height)
        y += self.display_height + self.gap

        # B 标签
        self.b_label = tk.Label(self, text='B:', anchor='w',
                                relief='solid', borderwidth=1,
                                font=self.label_font, bg='lightgray')
        self.b_label.place(x=x, y=y,
                           width=self.display_width,
                           height=self.display_height)
        y += self.display_height + self.gap

        # HEX 标签
        self.hex_label = tk.Label(self, text='HEX:', anchor='w',
                                  relief='solid', borderwidth=1,
                                  font=self.label_font, bg='lightgray')
        self.hex_label.place(x=x, y=y,
                             width=self.display_width,
                             height=self.display_height)
        y += self.display_height + self.gap

        # 颜色预览块（无文字，背景动态变化）
        self.color_preview = tk.Label(self, text='', anchor='center',
                                      relief='solid', borderwidth=2,
                                      font=self.label_font, bg='#ffffff')
        self.color_preview.place(x=x, y=y,
                                 width=self.display_width,
                                 height=self.display_height)

    # ------------------------------------------------------------------
    def _on_hue_click(self, event):
        self._update_hue_from_event(event)
        self._update_palette_image()
        self._update_color()

    def _on_hue_drag(self, event):
        self._update_hue_from_event(event)
        self._update_palette_image()
        self._update_color()

    def _update_hue_from_event(self, event):
        x = max(0, min(event.x, self.bar_width - 1))
        self.hue = (x / (self.bar_width - 1)) * 360.0
        self.canvas_hue.coords(self.hue_marker, x, 0, x, self.bar_height)

    def _on_palette_click(self, event):
        self._update_sv_from_event(event)
        self._update_color()

    def _on_palette_drag(self, event):
        self._update_sv_from_event(event)
        self._update_color()

    def _update_sv_from_event(self, event):
        x = max(0, min(event.x, self.palette_width - 1))
        y = max(0, min(event.y, self.palette_height - 1))
        self.saturation = x / (self.palette_width - 1)
        self.value = 1.0 - (y / (self.palette_height - 1))

        marker_size = 5 * self.scale
        self.canvas_palette.coords(
            self.palette_marker,
            x - marker_size/2, y - marker_size/2,
            x + marker_size/2, y + marker_size/2
        )

    # ------------------------------------------------------------------
    def _update_color(self):
        r, g, b = self.get_rgb()
        hex_str = self.get_hex()

        self.r_label.config(text=f'R:{r}')
        self.g_label.config(text=f'G:{g}')
        self.b_label.config(text=f'B:{b}')
        self.hex_label.config(text=f'HEX: {hex_str}')

        # 预览块只改变背景色
        fg = 'white' if (r*0.299 + g*0.587 + b*0.114) < 140 else 'black'
        self.color_preview.config(bg=hex_str, fg=fg)

        if self.on_color_change:
            self.on_color_change(hex_str)

    def _update_palette_image(self):
        img = Image.new('RGB', (self.palette_width, self.palette_height))
        draw = ImageDraw.Draw(img)
        for x in range(self.palette_width):
            s = x / (self.palette_width - 1)
            for y in range(self.palette_height):
                v = 1.0 - (y / (self.palette_height - 1))
                r, g, b = colorsys.hsv_to_rgb(self.hue/360.0, s, v)
                draw.point((x, y), fill=(int(r*255), int(g*255), int(b*255)))
        self.palette_image = ImageTk.PhotoImage(img)
        self.canvas_palette.create_image(0, 0, image=self.palette_image, anchor='nw')

    def _update_hue_bar_image(self):
        img = Image.new('RGB', (self.bar_width, self.bar_height))
        draw = ImageDraw.Draw(img)
        for x in range(self.bar_width):
            hue = (x / (self.bar_width - 1)) * 360.0
            r, g, b = colorsys.hsv_to_rgb(hue/360.0, 1.0, 1.0)
            draw.rectangle([x, 0, x+1, self.bar_height],
                           fill=(int(r*255), int(g*255), int(b*255)))
        self.hue_bar_image = ImageTk.PhotoImage(img)
        self.canvas_hue.create_image(0, 0, image=self.hue_bar_image, anchor='nw')

    # ------------------------------------------------------------------
    def get_rgb(self):
        r, g, b = colorsys.hsv_to_rgb(self.hue/360.0, self.saturation, self.value)
        return (int(r*255), int(g*255), int(b*255))

    def get_hex(self):
        return '#{:02x}{:02x}{:02x}'.format(*self.get_rgb())

    def get_hsv(self):
        return (self.hue, self.saturation, self.value)

    def set_color(self, color):
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

        r, g, b = [x/255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        self.hue = h * 360.0
        self.saturation = s
        self.value = v

        self._update_hue_bar_image()
        self._update_palette_image()
        self._update_color()
        self._sync_markers()

    def _sync_markers(self):
        x_hue = int((self.hue / 360.0) * (self.bar_width - 1))
        self.canvas_hue.coords(self.hue_marker, x_hue, 0, x_hue, self.bar_height)

        x_s = int(self.saturation * (self.palette_width - 1))
        y_v = int((1.0 - self.value) * (self.palette_height - 1))
        marker_size = 5 * self.scale
        self.canvas_palette.coords(
            self.palette_marker,
            x_s - marker_size/2, y_v - marker_size/2,
            x_s + marker_size/2, y_v + marker_size/2
        )

# ----------------------------------------------------------------------
if __name__ == '__main__':
    root = tk.Tk()
    root.title("ColorPicker")
    picker = ColorPicker(root, initial_color='#3a6ea5', scale=1.0,
                         on_color_change=lambda c: print("Color:", c))
    picker.pack(padx=5, pady=5)
    root.mainloop()