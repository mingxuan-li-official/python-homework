"""
全局界面主题配置：颜色和简单样式常量
"""
import tkinter as tk
from tkinter import ttk

# 基础色（按需求调整）
# 天蓝：常规操作按钮
PRIMARY_COLOR = "#5FB0FF"
# 天蓝加深
PRIMARY_DARK = "#3B82F6"
# 青蓝：查询/切换类按钮
QUERY_COLOR = "#00ACC1"
# 橙红：删除/退出等危险操作
DANGER_COLOR = "#FF7043"
# 其他保留
ACCENT_COLOR = "#42A5F5"
WARNING_COLOR = "#FB8C00"
SUCCESS_COLOR = "#43A047"
# 更灰的背景
NEUTRAL_BG = "#E5E7EB"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#333333"
TEXT_SECONDARY = "#757575"


def _darken_color(color):
    """将颜色变深10%"""
    if color.startswith("#"):
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        rgb = tuple(max(0, int(c * 0.9)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    return color


def create_rounded_button(parent, text="", command=None, bg="#5FB0FF", fg="white", 
                         font=("微软雅黑", 10), padx=20, pady=10, radius=8, 
                         activebackground=None, activeforeground=None, cursor="hand2", 
                         anchor="center", **kwargs):
    """
    创建圆角按钮的辅助函数
    
    使用Canvas绘制圆角矩形实现真正的圆角效果
    
    Args:
        parent: 父容器
        text: 按钮文字
        command: 点击回调函数
        bg: 背景颜色
        fg: 文字颜色
        font: 字体
        padx: 水平内边距
        pady: 垂直内边距
        radius: 圆角半径
        activebackground: 激活时的背景颜色
        activeforeground: 激活时的文字颜色
        cursor: 鼠标样式
    """
    # 获取父容器背景色
    try:
        parent_bg = parent.cget("bg")
    except:
        parent_bg = "white"
    
    # 计算按钮尺寸
    temp_label = tk.Label(parent, text=text, font=font)
    temp_label.update()
    text_width = temp_label.winfo_reqwidth()
    text_height = temp_label.winfo_reqheight()
    temp_label.destroy()
    
    # 如果anchor是w（左对齐），按钮宽度应该填满父容器
    if anchor == "w" or anchor == "west":
        width = 200  # 默认宽度，实际会通过pack的fill=tk.X来调整
    else:
        width = text_width + padx * 2
    
    height = text_height + pady * 2
    
    # 创建Canvas作为按钮
    button = tk.Canvas(parent, width=width, height=height, 
                       highlightthickness=0, bd=0, bg=parent_bg)
    
    # 存储按钮属性
    button._text = text
    button._command = command
    button._bg_color = bg
    button._fg_color = fg
    button._font = font
    button._radius = radius
    button._active_bg = activebackground or _darken_color(bg)
    button._active_fg = activeforeground or fg
    button._is_pressed = False
    button._anchor = anchor
    
    def _draw_rounded_rect(canvas, x1, y1, x2, y2, r, fill_color, outline_color=None):
        """绘制圆角矩形"""
        if outline_color is None:
            outline_color = fill_color
        
        # 绘制主体矩形
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill_color, outline=outline_color, width=0)
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill_color, outline=outline_color, width=0)
        
        # 绘制四个圆角
        canvas.create_oval(x1, y1, x1 + r * 2, y1 + r * 2, fill=fill_color, outline=outline_color, width=0)
        canvas.create_oval(x2 - r * 2, y1, x2, y1 + r * 2, fill=fill_color, outline=outline_color, width=0)
        canvas.create_oval(x1, y2 - r * 2, x1 + r * 2, y2, fill=fill_color, outline=outline_color, width=0)
        canvas.create_oval(x2 - r * 2, y2 - r * 2, x2, y2, fill=fill_color, outline=outline_color, width=0)
    
    def _draw_button(is_active=False):
        """绘制按钮"""
        button.delete("all")
        
        bg_color = button._active_bg if is_active else button._bg_color
        fg_color = button._active_fg if is_active else button._fg_color
        
        # 绘制圆角矩形
        w = button.winfo_width() or width
        h = button.winfo_height() or height
        
        # 确保宽度至少为1
        if w < 1:
            w = width
        
        _draw_rounded_rect(button, 0, 0, w, h, radius, bg_color)
        
        # 绘制文字（支持anchor参数）
        if button._anchor == "w" or button._anchor == "west":
            text_x = padx
            text_anchor = "w"
        elif button._anchor == "e" or button._anchor == "east":
            text_x = w - padx
            text_anchor = "e"
        else:
            text_x = w // 2
            text_anchor = "center"
        
        button.create_text(text_x, h // 2, text=button._text, 
                          fill=fg_color, font=button._font, anchor=text_anchor)
    
    # 绑定配置更新事件，以便在pack后重新绘制
    def _on_configure(event):
        _draw_button()
    
    button.bind("<Configure>", _on_configure)
    
    def _on_click(event):
        """点击事件"""
        button._is_pressed = True
        _draw_button(is_active=True)
    
    def _on_release(event):
        """释放事件"""
        if button._is_pressed:
            button._is_pressed = False
            _draw_button(is_active=False)
            if button._command:
                button._command()
    
    def _on_enter(event):
        """鼠标进入"""
        if not button._is_pressed:
            _draw_button(is_active=True)
    
    def _on_leave(event):
        """鼠标离开"""
        button._is_pressed = False
        _draw_button(is_active=False)
    
    # 绑定事件
    button.bind("<Button-1>", _on_click)
    button.bind("<ButtonRelease-1>", _on_release)
    button.bind("<Enter>", _on_enter)
    button.bind("<Leave>", _on_leave)
    button.bind("<Motion>", lambda e: button.config(cursor=cursor))
    
    # 初始绘制
    _draw_button()
    
    return button
