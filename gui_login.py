"""
登录界面
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from network_client import NetworkClient
from ui_theme import (
    PRIMARY_COLOR,
    PRIMARY_DARK,
    SUCCESS_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    DANGER_COLOR,
)

class LoginWindow:
    """登录窗口"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("图书管理系统 - 登录")
        # 更宽的窗口，适配背景图和居中卡片
        self.root.geometry("900x520")
        self.root.resizable(False, False)
        
        # 居中显示
        self.center_window()
        
        # 网络客户端
        self.client = NetworkClient()
        self.current_user = None

        # 加载背景图：自动从 assets 目录下选择一张 image*.png
        self.bg_image = None
        self._load_background_image()

        self.create_widgets()

    def _load_background_image(self):
        """从 assets 目录自动加载一张 PNG 背景图（优化：避免大图片阻塞）"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(base_dir, "assets")
            # 按优先级选择：image.png, image copy.png, image copy 2.png, image copy 3.png
            candidates = [
                "image.png",
                "image copy.png",
                "image copy 2.png",
                "image copy 3.png",
            ]
            for name in candidates:
                path = os.path.join(assets_dir, name)
                if os.path.exists(path):
                    # 检查文件大小，如果太大（>10MB）则跳过，避免阻塞
                    file_size = os.path.getsize(path)
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        print(f"警告: 图片文件 {name} 太大 ({file_size / 1024 / 1024:.2f}MB)，跳过加载")
                        continue
                    try:
                        # 尝试加载图片，设置超时保护
                        self.bg_image = tk.PhotoImage(file=path)
                        # 如果图片尺寸太大，也跳过（避免内存问题）
                        if self.bg_image.width() > 2000 or self.bg_image.height() > 2000:
                            print(f"警告: 图片 {name} 尺寸太大，跳过加载")
                            self.bg_image = None
                            continue
                        break
                    except Exception as e:
                        print(f"加载图片 {name} 失败: {e}")
                        self.bg_image = None
                        continue
        except Exception as e:
            print(f"加载背景图时出错: {e}")
            self.bg_image = None

        if self.bg_image is None:
            # 如果没有任何图片，不报错，使用纯色背景
            self.root.configure(bg=PRIMARY_COLOR)
    
    def center_window(self):
        """窗口居中（优化：避免在初始化时阻塞）"""
        # 延迟居中，避免在初始化时阻塞
        self.root.after(100, self._do_center)
    
    def _do_center(self):
        """执行窗口居中"""
        try:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
        except Exception:
            # 如果居中失败，使用默认位置
            pass
    
    def create_widgets(self):
        """创建界面组件（蓝天背景 + 居中卡片风格）"""
        # 使用 Canvas 放背景图和文字
        self.canvas = tk.Canvas(self.root, highlightthickness=0, borderwidth=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绘制背景图 / 纯色背景
        if self.bg_image is not None:
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        else:
            self.canvas.configure(bg=PRIMARY_COLOR)

        # 半透明卡片无法直接实现，这里用白色圆角效果的近似：白底 + 边距
        card_frame = tk.Frame(
            self.root,
            bg="white",
            bd=0,
            highlightthickness=0
        )
        # 把卡片放到 Canvas 中央
        self.canvas.create_window(
            450, 290,
            window=card_frame,
            width=480,
            height=300
        )

        # 卡片内：标题
        title_label = tk.Label(
            card_frame,
            text="账号登录",
            font=("微软雅黑", 18, "bold"),
            bg="white",
            fg=TEXT_PRIMARY,
            pady=10
        )
        title_label.pack(pady=(10, 5))

        # 连接状态与按钮（放在卡片顶端右上角一行）
        status_row = tk.Frame(card_frame, bg="white")
        status_row.pack(fill=tk.X, padx=30, pady=(0, 5))

        self.status_label = tk.Label(
            status_row,
            text="未连接",
            fg=DANGER_COLOR,
            bg="white",
            font=("微软雅黑", 10)
        )
        self.status_label.pack(side=tk.LEFT)

        connect_btn = tk.Button(
            status_row,
            text="连接服务器",
            command=self.connect_server,
            font=("微软雅黑", 9),
            bg=SUCCESS_COLOR,
            fg="white",
            bd=0,
            padx=14,
            pady=4,
            activebackground="#43A047",
            activeforeground="white",
            cursor="hand2"
        )
        connect_btn.pack(side=tk.RIGHT)

        # 表单区域
        form_frame = tk.Frame(card_frame, bg="white")
        form_frame.pack(fill=tk.X, padx=40, pady=(10, 10))

        # 用户名
        tk.Label(
            form_frame,
            text="账号",
            font=("微软雅黑", 11),
            bg="white",
            fg=TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w", pady=(5, 3))

        self.username_entry = tk.Entry(
            form_frame,
            font=("微软雅黑", 11),
            width=26,
            bd=0,
            highlightthickness=1,
            highlightbackground="#E0E0E0",
            highlightcolor=PRIMARY_COLOR,
            relief="flat"
        )
        self.username_entry.grid(row=1, column=0, sticky="we", pady=(0, 10))

        # 密码
        tk.Label(
            form_frame,
            text="密码",
            font=("微软雅黑", 11),
            bg="white",
            fg=TEXT_PRIMARY
        ).grid(row=2, column=0, sticky="w", pady=(5, 3))

        self.password_entry = tk.Entry(
            form_frame,
            font=("微软雅黑", 11),
            width=26,
            show="*",
            bd=0,
            highlightthickness=1,
            highlightbackground="#E0E0E0",
            highlightcolor=PRIMARY_COLOR,
            relief="flat"
        )
        self.password_entry.grid(row=3, column=0, sticky="we", pady=(0, 5))

        # “没有账号? 注册” 行
        register_row = tk.Frame(card_frame, bg="white")
        register_row.pack(fill=tk.X, padx=40, pady=(5, 5))

        tk.Label(
            register_row,
            text="没有账号请",
            font=("微软雅黑", 10),
            bg="white",
            fg=TEXT_SECONDARY,
        ).pack(side=tk.LEFT)

        register_link = tk.Label(
            register_row,
            text="注册",
            font=("微软雅黑", 10, "underline"),
            bg="white",
            fg=PRIMARY_COLOR,
            cursor="hand2",
        )
        register_link.pack(side=tk.LEFT)
        register_link.bind("<Button-1>", lambda e: self.show_register())

        # 按钮区域（仅大号登录按钮，居左）
        btn_frame = tk.Frame(card_frame, bg="white")
        btn_frame.pack(fill=tk.X, padx=40, pady=(5, 15))

        login_btn = tk.Button(
            btn_frame,
            text="登   录",
            command=self.login,
            font=("微软雅黑", 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            bd=0,
            padx=30,
            pady=6,
            width=8,
            activebackground=PRIMARY_DARK,
            activeforeground="white",
            cursor="hand2",
        )
        login_btn.pack(side=tk.LEFT)

        # 游客登录按钮（弱化成文字链接风格，靠右）
        guest_btn = tk.Button(
            btn_frame,
            text="游客登录",
            command=self.enter_guest_mode,
            font=("微软雅黑", 9),
            bg="white",
            fg=TEXT_SECONDARY,
            bd=0,
            activebackground="white",
            activeforeground=TEXT_PRIMARY,
            cursor="hand2",
        )
        guest_btn.pack(side=tk.RIGHT)

        # 绑定回车键
        self.password_entry.bind('<Return>', lambda e: self.login())
    
    def connect_server(self):
        """连接服务器"""
        if self.client.connect():
            self.status_label.config(text="已连接", fg="green")
            messagebox.showinfo("成功", "已连接到服务器")
        else:
            self.status_label.config(text="连接失败", fg="red")
            messagebox.showerror("错误", "无法连接到服务器，请确认服务器已启动")
    
    def login(self):
        """登录"""
        if not self.client.connected:
            messagebox.showwarning("警告", "请先连接到服务器")
            return
        
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("警告", "请输入用户名和密码")
            return
        
        user = self.client.login(username, password)
        if user:
            self.current_user = user
            self.root.destroy()
            # 根据角色打开不同的界面
            self.open_main_window()
        else:
            messagebox.showerror("错误", "用户名或密码错误")
    
    def show_register(self):
        """显示注册窗口"""
        if not self.client.connected:
            messagebox.showwarning("警告", "请先连接到服务器")
            return
        
        register_window = RegisterWindow(self.root, self.client)
        self.root.wait_window(register_window.window)
    
    def enter_guest_mode(self):
        """进入游客模式"""
        if not self.client.connected:
            messagebox.showwarning("警告", "请先连接到服务器")
            return
        
        # 创建游客用户对象
        guest_user = {
            'id': 0,
            'username': 'guest',
            'name': '游客',
            'role': 'guest'
        }
        self.current_user = guest_user
        self.root.destroy()
        # 打开游客模式主界面
        self.open_main_window()
    
    def open_main_window(self):
        """打开主界面"""
        from gui_main import MainWindow
        main_window = MainWindow(self.client, self.current_user)
        main_window.run()

class RegisterWindow:
    """注册窗口"""
    
    def __init__(self, parent, client):
        self.client = client
        self.window = tk.Toplevel(parent)
        self.window.title("用户注册")
        self.window.geometry("400x430")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建注册界面"""
        # 标题
        tk.Label(
            self.window,
            text="用户注册",
            font=("微软雅黑", 16, "bold"),
            pady=15
        ).pack()
        
        # 表单框架
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=10)
        
        # 用户名
        tk.Label(form_frame, text="用户名:", font=("微软雅黑", 10)).grid(
            row=0, column=0, padx=10, pady=8, sticky="e"
        )
        self.username_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20)
        self.username_entry.grid(row=0, column=1, padx=10, pady=8)
        
        # 密码
        tk.Label(form_frame, text="密码:", font=("微软雅黑", 10)).grid(
            row=1, column=0, padx=10, pady=8, sticky="e"
        )
        self.password_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8)
        
        # 姓名
        tk.Label(form_frame, text="姓名:", font=("微软雅黑", 10)).grid(
            row=2, column=0, padx=10, pady=8, sticky="e"
        )
        self.name_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20)
        self.name_entry.grid(row=2, column=1, padx=10, pady=8)
        
        # 邮箱
        tk.Label(form_frame, text="邮箱:", font=("微软雅黑", 10)).grid(
            row=3, column=0, padx=10, pady=8, sticky="e"
        )
        self.email_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20)
        self.email_entry.grid(row=3, column=1, padx=10, pady=8)
        
        # 电话
        tk.Label(form_frame, text="电话:", font=("微软雅黑", 10)).grid(
            row=4, column=0, padx=10, pady=8, sticky="e"
        )
        self.phone_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20)
        self.phone_entry.grid(row=4, column=1, padx=10, pady=8)

        # 年龄
        tk.Label(form_frame, text="年龄:", font=("微软雅黑", 10)).grid(
            row=5, column=0, padx=10, pady=8, sticky="e"
        )
        self.age_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20)
        self.age_entry.grid(row=5, column=1, padx=10, pady=8)
        
        # 按钮
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="注册",
            command=self.register,
            font=("微软雅黑", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="取消",
            command=self.window.destroy,
            font=("微软雅黑", 10),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def register(self):
        """执行注册"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        age_str = self.age_entry.get().strip()
        age_value = None
        if age_str:
            if not age_str.isdigit():
                messagebox.showwarning("警告", "年龄必须是0-150之间的整数")
                return
            age_value = int(age_str)
            if age_value < 0 or age_value > 150:
                messagebox.showwarning("警告", "年龄必须是0-150之间的整数")
                return
        
        if not username or not password or not name:
            messagebox.showwarning("警告", "用户名、密码和姓名不能为空")
            return
        
        # 新注册用户默认为普通用户角色
        role = "user"
        
        if self.client.register(username, password, role, name, email, phone, age_value):
            messagebox.showinfo("成功", "注册成功，请登录")
            self.window.destroy()
        else:
            messagebox.showerror("错误", "注册失败，用户名可能已存在")

def main():
    """主函数"""
    app = LoginWindow()
    app.root.mainloop()

if __name__ == "__main__":
    main()

