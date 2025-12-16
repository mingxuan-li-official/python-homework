"""
普通用户界面（会员/普通用户）
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from ui_theme import (
    PRIMARY_COLOR,
    PRIMARY_DARK,
    WARNING_COLOR,
    SUCCESS_COLOR,
    DANGER_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    NEUTRAL_BG,
    CARD_BG,
    QUERY_COLOR,
)

class UserWindow:
    """普通用户窗口"""
    
    def __init__(self, root, client, user):
        self.root = root
        self.client = client
        self.user = user

        # 统一背景色 + 侧边栏布局
        self.root.configure(bg=NEUTRAL_BG)
        self._build_layout()
        self._init_styles()
        self.create_widgets()
        self.refresh_books()
        self.refresh_my_borrows()
        self.load_user_info()

    def _init_styles(self):
        """统一设置列表风格"""
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="white",
            foreground=TEXT_PRIMARY,
            fieldbackground="white",
            rowheight=26,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#eef1f6",
            foreground=TEXT_PRIMARY,
            font=("微软雅黑", 10, "bold"),
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", "#e0e6ef")])

    def _build_layout(self):
        """构建侧边栏 + 顶部栏 + 内容卡片"""
        container = tk.Frame(self.root, bg=NEUTRAL_BG)
        container.pack(fill=tk.BOTH, expand=True)

        # 左侧导航
        self.sidebar = tk.Frame(container, bg="#1f2d3d", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        tk.Label(
            self.sidebar,
            text="图书借阅中心",
            bg="#1f2d3d",
            fg="white",
            font=("微软雅黑", 12, "bold"),
            pady=16,
        ).pack(fill=tk.X)

        tk.Button(
            self.sidebar,
            text="图书浏览",
            command=lambda: self._switch_tab(0),
            anchor="w",
            padx=24,
            pady=10,
            relief="flat",
            bg="#243447",
            fg="white",
            activebackground="#30455e",
            activeforeground="white",
            bd=0,
            font=("微软雅黑", 10),
            cursor="hand2",
        ).pack(fill=tk.X, pady=(0, 2))
        tk.Button(
            self.sidebar,
            text="我的借阅",
            command=lambda: self._switch_tab(1),
            anchor="w",
            padx=24,
            pady=10,
            relief="flat",
            bg="#243447",
            fg="white",
            activebackground="#30455e",
            activeforeground="white",
            bd=0,
            font=("微软雅黑", 10),
            cursor="hand2",
        ).pack(fill=tk.X, pady=(0, 2))

        # 右侧主体
        main_area = tk.Frame(container, bg=NEUTRAL_BG)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 顶部栏
        header = tk.Frame(main_area, bg="white", height=54)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        role_text = "会员" if self.user["role"] == "member" else "普通用户"
        tk.Label(
            header,
            text=f"{role_text}: {self.user['name']}",
            font=("微软雅黑", 11, "bold"),
            bg="white",
            fg=TEXT_PRIMARY,
        ).pack(side=tk.LEFT, padx=18)
        tk.Button(
            header,
            text="个人信息",
            command=self.show_user_info,
            font=("微软雅黑", 10),
            bg=PRIMARY_DARK,
            fg="white",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            header,
            text="退出登录",
            command=self.logout,
            font=("微软雅黑", 10),
            bg=DANGER_COLOR,
            fg="white",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=14)

        # 主内容卡片
        self.main_card = tk.Frame(main_area, bg=CARD_BG, bd=0)
        self.main_card.pack(fill=tk.BOTH, expand=True, padx=22, pady=16)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建Notebook（标签页）
        self.notebook = ttk.Notebook(self.main_card)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # 图书浏览标签页
        books_frame = tk.Frame(self.notebook)
        self.notebook.add(books_frame, text="图书浏览")
        self.create_books_tab(books_frame)
        
        # 我的借阅标签页
        borrows_frame = tk.Frame(self.notebook)
        self.notebook.add(borrows_frame, text="我的借阅")
        self.create_borrows_tab(borrows_frame)
        
    def _switch_tab(self, index: int):
        try:
            self.notebook.select(index)
        except Exception:
            pass
    
    def create_books_tab(self, parent):
        """创建图书浏览标签页"""
        # 搜索框架
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="搜索:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("微软雅黑", 10), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_books())
        
        tk.Button(
            search_frame,
            text="搜索",
            command=self.search_books,
            font=("微软雅黑", 10),
            bg=QUERY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="刷新",
            command=self.refresh_books,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # 图书列表
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "书名", "作者", "ISBN", "分类", "出版社", "可借数量", "状态")
        self.books_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        
        self.books_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.books_tree.bind("<Double-1>", self.on_book_double_click)
        
        # 操作按钮
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="查看详情",
            command=self.view_book_detail,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="借阅",
            command=self.borrow_book,
            font=("微软雅黑", 10),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def create_borrows_tab(self, parent):
        """创建我的借阅标签页"""
        # 筛选框架
        filter_frame = tk.Frame(parent)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(filter_frame, text="状态筛选:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="all")
        status_options = [("全部", "all"), ("借阅中", "borrowed"), ("已归还", "returned")]
        for text, value in status_options:
            tk.Radiobutton(filter_frame, text=text, variable=self.status_var,
                          value=value, font=("微软雅黑", 10),
                          command=self.refresh_my_borrows).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="刷新",
            command=self.refresh_my_borrows,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
        
        # 借阅记录列表
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "书名", "作者", "ISBN", "借阅日期", "应还日期", "归还日期", "状态")
        self.borrows_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.borrows_tree.heading(col, text=col)
            self.borrows_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.borrows_tree.yview)
        self.borrows_tree.configure(yscrollcommand=scrollbar.set)
        
        self.borrows_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 操作按钮
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="归还",
            command=self.return_book,
            font=("微软雅黑", 10),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    
    def refresh_books(self):
        """刷新图书列表"""
        # 清空现有数据
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        # 获取所有图书
        books = self.client.search_books()
        for book in books:
            self.books_tree.insert("", tk.END, values=(
                book['id'],
                book['title'],
                book['author'],
                book.get('isbn', ''),
                book.get('category', ''),
                book.get('publisher', ''),
                book.get('available_copies', 0),
                book.get('status', 'available')
            ))
    
    def search_books(self):
        """搜索图书"""
        keyword = self.search_entry.get().strip()
        books = self.client.search_books(keyword=keyword)
        
        # 清空现有数据
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        # 显示搜索结果
        for book in books:
            self.books_tree.insert("", tk.END, values=(
                book['id'],
                book['title'],
                book['author'],
                book.get('isbn', ''),
                book.get('category', ''),
                book.get('publisher', ''),
                book.get('available_copies', 0),
                book.get('status', 'available')
            ))
    
    def on_book_double_click(self, event):
        """双击图书事件"""
        self.view_book_detail()
    
    def view_book_detail(self):
        """查看图书详情"""
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要查看的图书")
            return
        
        item = self.books_tree.item(selection[0])
        book_id = item['values'][0]
        
        book = self.client.get_book(book_id)
        if book:
            detail_window = BookDetailWindow(self.root, book)
    
    def borrow_book(self):
        """借阅图书"""
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要借阅的图书")
            return
        
        item = self.books_tree.item(selection[0])
        book_id = item['values'][0]
        available = item['values'][6]
        
        if available <= 0:
            messagebox.showwarning("警告", "该图书暂无可借副本")
            return
        
        if not messagebox.askyesno("确认", "确定要借阅这本图书吗？"):
            return
        
        success, message = self.client.borrow_book(self.user['id'], book_id)
        if success:
            messagebox.showinfo("成功", message)
            self.refresh_books()
            self.refresh_my_borrows()
        else:
            messagebox.showerror("错误", message)
    
    def refresh_my_borrows(self):
        """刷新我的借阅记录"""
        # 清空现有数据
        for item in self.borrows_tree.get_children():
            self.borrows_tree.delete(item)
        
        # 获取借阅记录
        status = self.status_var.get()
        status = None if status == "all" else status
        borrows = self.client.get_my_borrows(self.user['id'], status)
        
        for borrow in borrows:
            # 检查是否逾期
            status_text = borrow.get('status', '')
            if status_text == 'borrowed':
                try:
                    due_date = datetime.strptime(borrow.get('due_date', ''), '%Y-%m-%d').date()
                    if due_date < date.today():
                        status_text = 'overdue'
                except:
                    pass
            
            self.borrows_tree.insert("", tk.END, values=(
                borrow['id'],
                borrow.get('title', ''),
                borrow.get('author', ''),
                borrow.get('isbn', ''),
                borrow.get('borrow_date', ''),
                borrow.get('due_date', ''),
                borrow.get('return_date', '') or '未归还',
                status_text
            ))
    
    def return_book(self):
        """归还图书"""
        selection = self.borrows_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要归还的图书")
            return
        
        item = self.borrows_tree.item(selection[0])
        record_id = item['values'][0]
        status = item['values'][7]
        
        if status == 'returned':
            messagebox.showwarning("警告", "该图书已归还")
            return
        
        if not messagebox.askyesno("确认", "确定要归还这本图书吗？"):
            return
        
        if self.client.return_book(record_id):
            messagebox.showinfo("成功", "归还成功")
            self.refresh_my_borrows()
            self.refresh_books()
        else:
            messagebox.showerror("错误", "归还失败")
    
    def show_user_info(self):
        """显示个人信息窗口"""
        UserInfoWindow(self.root, self.client, self.user)
    
    def load_user_info(self):
        """加载用户信息"""
        user_info = self.client.get_user_info(self.user['id'])
        if user_info:
            self.user.update(user_info)
    
    
    def logout(self):
        """退出登录"""
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            # 保存客户端连接状态
            client = self.client
            self.root.destroy()
            # 重新打开登录窗口
            from gui_login import LoginWindow
            login_window = LoginWindow()
            # 如果之前已连接，自动连接
            if client.connected:
                login_window.client = client
                login_window.status_label.config(text="已连接", fg="green")
            login_window.root.mainloop()

class BookDetailWindow:
    """图书详情窗口"""
    
    def __init__(self, parent, book):
        self.window = tk.Toplevel(parent)
        self.window.title("图书详情")
        self.window.geometry("540x420")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.configure(bg=NEUTRAL_BG)
        
        self.create_widgets(book)
    
    def create_widgets(self, book):
        """创建详情界面"""
        # 卡片背景
        card = tk.Frame(self.window, bg=CARD_BG, bd=0, relief="flat")
        card.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        header = tk.Frame(card, bg=CARD_BG)
        header.pack(fill=tk.X, pady=(6, 10))
        tk.Label(
            header,
            text="图书详情",
            font=("微软雅黑", 14, "bold"),
            fg=TEXT_PRIMARY,
            bg=CARD_BG,
        ).pack(side=tk.LEFT)

        grid = tk.Frame(card, bg=CARD_BG)
        grid.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        rows = [
            ("书名", book.get("title", "")),
            ("作者", book.get("author", "")),
            ("ISBN", book.get("isbn", "无")),
            ("分类", book.get("category", "无")),
            ("出版社", book.get("publisher", "无")),
            ("出版日期", book.get("publish_date", "无")),
            ("总数量", f"{book.get('total_copies', 0)} 册"),
            ("可借数量", f"{book.get('available_copies', 0)} 册"),
            ("状态", book.get("status", "available")),
        ]

        for idx, (label, value) in enumerate(rows):
            tk.Label(
                grid,
                text=f"{label}：",
                font=("微软雅黑", 11, "bold"),
                fg=TEXT_PRIMARY,
                bg=CARD_BG,
                anchor="e",
                width=10,
            ).grid(row=idx, column=0, sticky="e", pady=4, padx=(0, 8))
            tk.Label(
                grid,
                text=value,
                font=("微软雅黑", 11),
                fg=TEXT_SECONDARY,
                bg=CARD_BG,
                anchor="w",
                wraplength=340,
                justify="left",
            ).grid(row=idx, column=1, sticky="w", pady=4, padx=(0, 4))

        tk.Button(
            card,
            text="关闭",
            command=self.window.destroy,
            font=("微软雅黑", 10, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
        ).pack(pady=12)

class UserInfoWindow:
    """个人信息窗口"""
    
    def __init__(self, parent, client, user):
        self.client = client
        self.user = user
        self.window = tk.Toplevel(parent)
        self.window.title("个人信息")
        self.window.geometry("420x420")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """创建界面"""
        form_frame = tk.Frame(self.window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 用户名（只读）
        tk.Label(form_frame, text="用户名:", font=("微软雅黑", 10)).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        self.username_label = tk.Label(form_frame, text="", font=("微软雅黑", 10), fg="gray")
        self.username_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # 姓名
        tk.Label(form_frame, text="姓名:", font=("微软雅黑", 10)).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.name_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=25)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # 角色（只读）
        tk.Label(form_frame, text="角色:", font=("微软雅黑", 10)).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.role_label = tk.Label(form_frame, text="", font=("微软雅黑", 10), fg="gray")
        self.role_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # 年龄
        tk.Label(form_frame, text="年龄:", font=("微软雅黑", 10)).grid(
            row=3, column=0, padx=10, pady=10, sticky="e"
        )
        self.age_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=25)
        self.age_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # 邮箱
        tk.Label(form_frame, text="邮箱:", font=("微软雅黑", 10)).grid(
            row=4, column=0, padx=10, pady=10, sticky="e"
        )
        self.email_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=25)
        self.email_entry.grid(row=4, column=1, padx=10, pady=10)
        
        # 电话
        tk.Label(form_frame, text="电话:", font=("微软雅黑", 10)).grid(
            row=5, column=0, padx=10, pady=10, sticky="e"
        )
        self.phone_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=25)
        self.phone_entry.grid(row=5, column=1, padx=10, pady=10)
        
        # 按钮框架
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="保存",
            command=self.save,
            font=("微软雅黑", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="修改密码",
            command=self.change_password,
            font=("微软雅黑", 10),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="关闭",
            command=self.window.destroy,
            font=("微软雅黑", 10),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        """加载用户数据"""
        self.username_label.config(text=self.user.get('username', ''))
        self.name_entry.insert(0, self.user.get('name', ''))
        role_text = {'admin': '管理员', 'member': '会员', 'user': '普通用户'}
        self.role_label.config(text=role_text.get(self.user.get('role', ''), ''))
        age_value = self.user.get('age')
        if age_value is not None:
            self.age_entry.insert(0, str(age_value))
        self.email_entry.insert(0, self.user.get('email', ''))
        self.phone_entry.insert(0, self.user.get('phone', ''))
    
    def save(self):
        """保存个人信息"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        age_text = self.age_entry.get().strip()
        age_value = None
        if age_text:
            if not age_text.isdigit():
                messagebox.showwarning("警告", "年龄必须是0-150之间的整数")
                return
            age_value = int(age_text)
            if age_value < 0 or age_value > 150:
                messagebox.showwarning("警告", "年龄必须是0-150之间的整数")
                return
        
        if not name:
            messagebox.showwarning("警告", "姓名不能为空")
            return
        
        if self.client.update_user_info(
            self.user['id'],
            name=name,
            email=email,
            phone=phone,
            age=age_value if age_text else None
        ):
            messagebox.showinfo("成功", "信息更新成功")
            self.user['name'] = name
            self.user['email'] = email
            self.user['phone'] = phone
            self.user['age'] = age_value if age_text else None
        else:
            messagebox.showerror("错误", "更新失败")
    
    def change_password(self):
        """修改密码"""
        dialog = ChangePasswordDialog(self.window, self.client, self.user['id'])
        self.window.wait_window(dialog.window)

class ChangePasswordDialog:
    """修改密码对话框"""
    
    def __init__(self, parent, client, user_id):
        self.client = client
        self.user_id = user_id
        self.window = tk.Toplevel(parent)
        self.window.title("修改密码")
        self.window.geometry("350x200")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建对话框"""
        form_frame = tk.Frame(self.window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(form_frame, text="原密码:", font=("微软雅黑", 10)).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        self.old_password_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20, show="*")
        self.old_password_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(form_frame, text="新密码:", font=("微软雅黑", 10)).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.new_password_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20, show="*")
        self.new_password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(form_frame, text="确认密码:", font=("微软雅黑", 10)).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.confirm_password_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=20, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)
        
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="确定",
            command=self.save,
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
    
    def save(self):
        """保存新密码"""
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not old_password or not new_password:
            messagebox.showwarning("警告", "密码不能为空")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        if len(new_password) < 6:
            messagebox.showwarning("警告", "密码长度至少6位")
            return
        
        if self.client.change_password(self.user_id, old_password, new_password):
            messagebox.showinfo("成功", "密码修改成功")
            self.window.destroy()
        else:
            messagebox.showerror("错误", "原密码错误或修改失败")

