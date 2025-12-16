"""
游客模式界面 - 只能查看图书，不能借阅
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui_theme import (
    PRIMARY_COLOR,
    PRIMARY_DARK,
    DANGER_COLOR,
    QUERY_COLOR,
    NEUTRAL_BG,
    CARD_BG,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

class GuestWindow:
    """游客窗口"""
    
    def __init__(self, root, client):
        self.root = root
        self.client = client
        self.root.configure(bg=NEUTRAL_BG)
        self.create_widgets()
        self.refresh_books()
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = tk.Frame(self.root, bg="white", height=52)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        toolbar.pack_propagate(False)
        
        tk.Label(
            toolbar,
            text="游客模式 - 仅可查看图书",
            font=("微软雅黑", 12, "bold"),
            bg="white",
            fg=TEXT_PRIMARY,
        ).pack(side=tk.LEFT, padx=15, pady=12)
        
        tk.Button(
            toolbar,
            text="登录",
            command=self.show_login,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=15, pady=10)
        
        # 提示信息
        info_frame = tk.Frame(self.root, bg=CARD_BG, height=40)
        info_frame.pack(fill=tk.X, side=tk.TOP)
        tk.Label(
            info_frame,
            text="提示：游客模式只能查看图书信息，无法借阅。请登录后使用完整功能。",
            font=("微软雅黑", 10),
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
        ).pack(pady=10)
        
        # 图书浏览区域
        books_frame = tk.Frame(self.root, bg=NEUTRAL_BG)
        books_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 搜索框架
        search_frame = tk.Frame(books_frame, bg=CARD_BG)
        search_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(search_frame, text="搜索:", font=("微软雅黑", 10), bg=CARD_BG, fg=TEXT_PRIMARY).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("微软雅黑", 10), width=30, relief="flat", highlightthickness=1, highlightbackground="#d9d9d9", highlightcolor=PRIMARY_COLOR)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_books())
        
        tk.Button(
            search_frame,
            text="搜索",
            command=self.search_books,
            font=("微软雅黑", 10),
            bg=QUERY_COLOR,
            fg="white",
            bd=0,
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
            bd=0,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # 图书列表
        list_frame = tk.Frame(books_frame, bg=CARD_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("ID", "书名", "作者", "ISBN", "分类", "出版社", "可借数量", "状态")
        self.books_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        
        self.books_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.books_tree.bind("<Double-1>", self.on_book_double_click)
        
        # 操作按钮（仅查看详情）
        btn_frame = tk.Frame(books_frame, bg=CARD_BG)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="查看详情",
            command=self.view_book_detail,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            bd=0,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # 借阅按钮（禁用状态，显示提示）
        borrow_btn = tk.Button(
            btn_frame,
            text="借阅（需登录）",
            command=self.show_login_prompt,
            font=("微软雅黑", 10),
            bg=DANGER_COLOR,
            fg="white",
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        borrow_btn.pack(side=tk.LEFT, padx=5)
    
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
    
    def show_login_prompt(self):
        """显示登录提示"""
        messagebox.showinfo("提示", "游客模式无法借阅图书，请先登录后再使用借阅功能。")
        self.show_login()
    
    def show_login(self):
        """显示登录对话框"""
        if messagebox.askyesno("确认", "确定要登录吗？当前游客模式将退出。"):
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

        tip = tk.Label(
            card,
            text="提示：游客模式只能查看，无法借阅。请登录后使用借阅功能。",
            font=("微软雅黑", 10),
            fg=TEXT_SECONDARY,
            bg=CARD_BG,
            wraplength=420,
            justify="left",
        )
        tip.pack(pady=(4, 8))

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
        ).pack(pady=10)

