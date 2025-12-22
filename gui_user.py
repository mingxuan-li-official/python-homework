"""
普通用户界面（会员/普通用户）
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import re
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
    create_rounded_button,
)

try:
    import matplotlib
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    # 优先使用支持中文的字体，防止中文字符缺失警告
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
except ImportError:
    Figure = None
    FigureCanvasTkAgg = None

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

        create_rounded_button(
            self.sidebar,
            text="首页",
            command=lambda: self._switch_tab(0),
            anchor="w",
            padx=24,
            pady=10,
            bg="#243447",
            fg="white",
            activebackground="#30455e",
            activeforeground="white",
            font=("微软雅黑", 10),
            radius=4
        ).pack(fill=tk.X, pady=(0, 2))
        create_rounded_button(
            self.sidebar,
            text="图书浏览",
            command=lambda: self._switch_tab(1),
            anchor="w",
            padx=24,
            pady=10,
            bg="#243447",
            fg="white",
            activebackground="#30455e",
            activeforeground="white",
            font=("微软雅黑", 10),
            radius=4
        ).pack(fill=tk.X, pady=(0, 2))
        create_rounded_button(
            self.sidebar,
            text="我的借阅",
            command=lambda: self._switch_tab(2),
            anchor="w",
            padx=24,
            pady=10,
            bg="#243447",
            fg="white",
            activebackground="#30455e",
            activeforeground="white",
            font=("微软雅黑", 10),
            radius=4
        ).pack(fill=tk.X, pady=(0, 2))
        create_rounded_button(
            self.sidebar,
            text="消息通知",
            command=lambda: self._switch_tab(3),
            anchor="w",
            padx=24,
            pady=10,
            bg="#243447",
            fg="white",
            activebackground="#30455e",
            activeforeground="white",
            font=("微软雅黑", 10),
            radius=4
        ).pack(fill=tk.X, pady=(0, 2))
        create_rounded_button(
            self.sidebar,
            text="个人信息",
            command=lambda: self._switch_tab(4),
            anchor="w",
            padx=24,
            pady=10,
            bg="#243447",
            fg="white",
            activebackground="#30455e",
            activeforeground="white",
            font=("微软雅黑", 10),
            radius=4
        ).pack(fill=tk.X, pady=(0, 2))

        # 右侧主体
        main_area = tk.Frame(container, bg=NEUTRAL_BG)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 顶部栏
        self.header = tk.Frame(main_area, bg="white", height=54)
        self.header.pack(fill=tk.X, side=tk.TOP)
        self.header.pack_propagate(False)
        role_text = "会员" if self.user["role"] == "member" else "普通用户"
        self.header_name_label = tk.Label(
            self.header,
            text=f"{role_text}: {self.user['name']}",
            font=("微软雅黑", 11, "bold"),
            bg="white",
            fg=TEXT_PRIMARY,
        )
        self.header_name_label.pack(side=tk.LEFT, padx=18)
        create_rounded_button(
            self.header,
            text="退出登录",
            command=self.logout,
            font=("微软雅黑", 10),
            bg=DANGER_COLOR,
            fg="white",
            padx=10,
            pady=6,
            radius=6
        ).pack(side=tk.RIGHT, padx=14)

        # 主内容卡片
        self.main_card = tk.Frame(main_area, bg=CARD_BG, bd=0)
        self.main_card.pack(fill=tk.BOTH, expand=True, padx=22, pady=16)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建Notebook（标签页）
        self.notebook = ttk.Notebook(self.main_card)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # 首页标签页
        home_frame = tk.Frame(self.notebook)
        self.notebook.add(home_frame, text="首页")
        self.create_home_tab(home_frame)
        
        # 图书浏览标签页
        books_frame = tk.Frame(self.notebook)
        self.notebook.add(books_frame, text="图书浏览")
        self.create_books_tab(books_frame)
        
        # 我的借阅标签页
        borrows_frame = tk.Frame(self.notebook)
        self.notebook.add(borrows_frame, text="我的借阅")
        self.create_borrows_tab(borrows_frame)
        
        # 消息通知标签页
        notifications_frame = tk.Frame(self.notebook)
        self.notebook.add(notifications_frame, text="消息通知")
        self.create_notifications_tab(notifications_frame)
        
        # 个人信息标签页
        info_frame = tk.Frame(self.notebook)
        self.notebook.add(info_frame, text="个人信息")
        self.create_user_info_tab(info_frame)
    
    def _switch_tab(self, index: int):
        try:
            self.notebook.select(index)
            # 如果切换到首页标签页（索引0），刷新首页数据
            if index == 0:
                self.refresh_home_data()
        except Exception:
            pass
    
    def create_home_tab(self, parent):
        """创建首页标签页"""
        # 主容器
        main_container = tk.Frame(parent, bg=NEUTRAL_BG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 顶部蓝色横幅
        banner_frame = tk.Frame(main_container, bg="#5FB0FF", height=200)
        banner_frame.pack(fill=tk.X, side=tk.TOP)
        banner_frame.pack_propagate(False)
        
        # 横幅内容容器
        banner_content = tk.Frame(banner_frame, bg="#5FB0FF")
        banner_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # 左侧文字区域
        left_text_frame = tk.Frame(banner_content, bg="#5FB0FF")
        left_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 主标题
        title_label = tk.Label(
            left_text_frame,
            text="欢迎使用图书管理系统",
            font=("微软雅黑", 24, "bold"),
            bg="#5FB0FF",
            fg="white",
            anchor="w"
        )
        title_label.pack(fill=tk.X, pady=(0, 10))
        
        # 问候语
        role_text = "会员" if self.user.get("role") == "member" else "普通用户"
        greeting_text = f"你好, {self.user.get('name', '用户')}, 祝你有美好的一天!"
        greeting_label = tk.Label(
            left_text_frame,
            text=greeting_text,
            font=("微软雅黑", 14),
            bg="#5FB0FF",
            fg="white",
            anchor="w"
        )
        greeting_label.pack(fill=tk.X, pady=(0, 20))
        
        # 按钮区域
        button_frame = tk.Frame(left_text_frame, bg="#5FB0FF")
        button_frame.pack(fill=tk.X)
        
        # 浏览图书按钮
        browse_btn = create_rounded_button(
            button_frame,
            text="浏览图书",
            command=lambda: self._switch_tab(1),
            font=("微软雅黑", 12),
            bg="#87CEEB",
            fg="white",
            padx=20,
            pady=10,
            radius=8
        )
        browse_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # 我的借阅按钮
        borrow_btn = create_rounded_button(
            button_frame,
            text="我的借阅",
            command=lambda: self._switch_tab(2),
            font=("微软雅黑", 12),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=20,
            pady=10,
            radius=8
        )
        borrow_btn.pack(side=tk.LEFT)
        
        # 右侧装饰图标（书签）
        right_icon_frame = tk.Frame(banner_content, bg="#5FB0FF", width=150)
        right_icon_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_icon_frame.pack_propagate(False)
        
        # 使用Unicode书签符号作为装饰
        icon_label = tk.Label(
            right_icon_frame,
            text="🔖",
            font=("微软雅黑", 80),
            bg="#5FB0FF",
            fg="white"
        )
        icon_label.pack(expand=True)
        
        # 底部白色内容区域
        content_area = tk.Frame(main_container, bg="white")
        content_area.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 3个数据卡片容器
        cards_frame = tk.Frame(content_area, bg="white")
        cards_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建3个数据卡片（去除用户总数）
        self.home_cards = []
        card_configs = [
            {"label": "图书总数", "icon": "📚", "color": "#42a5f5", "key": "total_books"},
            {"label": "当前借阅", "icon": "📋", "color": SUCCESS_COLOR, "key": "current_borrows"},
            {"label": "图书类型", "icon": "🔖", "color": "#ef5350", "key": "book_types"}
        ]
        
        for i, config in enumerate(card_configs):
            card = tk.Frame(cards_frame, bg="white", relief="flat", bd=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
            
            # 图标区域
            icon_frame = tk.Frame(card, bg=config["color"], width=80, height=80)
            icon_frame.pack(pady=20)
            icon_frame.pack_propagate(False)
            
            icon_label = tk.Label(
                icon_frame,
                text=config["icon"],
                font=("微软雅黑", 40),
                bg=config["color"],
                fg="white"
            )
            icon_label.pack(expand=True)
            
            # 数值标签
            value_label = tk.Label(
                card,
                text="0",
                font=("微软雅黑", 28, "bold"),
                bg="white",
                fg=TEXT_PRIMARY
            )
            value_label.pack(pady=(10, 5))
            self.home_cards.append({"value_label": value_label, "key": config["key"]})
            
            # 文字标签
            text_label = tk.Label(
                card,
                text=config["label"],
                font=("微软雅黑", 14),
                bg="white",
                fg=TEXT_SECONDARY
            )
            text_label.pack(pady=(0, 20))
        
        # 初始化数据
        self.refresh_home_data()
    
    def refresh_home_data(self):
        """刷新首页数据"""
        try:
            # 获取统计数据
            stats = self.client.get_statistics()
            if stats:
                # 更新图书总数
                for card in self.home_cards:
                    if card["key"] == "total_books":
                        card["value_label"].config(text=str(stats.get('total_books', 0)))
            
            # 获取用户当前借阅数量
            try:
                borrows = self.client.get_my_borrows(self.user['id'], status='borrowed')
                current_borrow_count = len(borrows) if borrows else 0
            except:
                current_borrow_count = 0
            
            for card in self.home_cards:
                if card["key"] == "current_borrows":
                    card["value_label"].config(text=str(current_borrow_count))
            
            # 获取图书类型数
            try:
                categories = self.client.get_categories()
                if categories:
                    # 使用原始分类列表去重
                    unique_categories = set()
                    for cat in categories:
                        if cat and cat.strip():
                            unique_categories.add(cat.strip())
                    type_count = len(unique_categories)
                else:
                    type_count = 0
            except:
                type_count = 0
            
            for card in self.home_cards:
                if card["key"] == "book_types":
                    card["value_label"].config(text=str(type_count))
        except Exception as e:
            print(f"刷新首页数据失败: {e}")
    
    def create_books_tab(self, parent):
        """创建图书浏览标签页"""
        # 搜索框架
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="搜索:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("微软雅黑", 10), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_books())
        
        create_rounded_button(
            search_frame,
            text="搜索",
            command=self.search_books,
            font=("微软雅黑", 10),
            bg=QUERY_COLOR,
            fg="white",
            padx=15,
            pady=5,
            radius=6
        ).pack(side=tk.LEFT, padx=5)
        
        create_rounded_button(
            search_frame,
            text="刷新",
            command=self.refresh_books,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5,
            radius=6
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
        
        create_rounded_button(
            btn_frame,
            text="查看详情",
            command=self.view_book_detail,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5,
            radius=6
        ).pack(side=tk.LEFT, padx=5)
        
        create_rounded_button(
            btn_frame,
            text="借阅",
            command=self.borrow_book,
            font=("微软雅黑", 10),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=15,
            pady=5,
            radius=6
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
        
        create_rounded_button(
            filter_frame,
            text="刷新",
            command=self.refresh_my_borrows,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5,
            radius=6
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
        
        create_rounded_button(
            btn_frame,
            text="归还",
            command=self.return_book,
            font=("微软雅黑", 10),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=15,
            pady=5,
            radius=6
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
            # 更新个人信息页面的图表
            if hasattr(self, 'borrow_chart_fig') and self.borrow_chart_fig:
                self.update_borrow_category_chart()
            # 刷新推荐列表（无论是否有图表）
            try:
                self.refresh_recommendations()
            except Exception:
                pass
            try:
                self.refresh_notifications()
            except Exception:
                pass
        else:
            messagebox.showerror("错误", message)
    
    def create_notifications_tab(self, parent):
        """创建消息通知标签页"""
        main_frame = tk.Frame(parent, bg=CARD_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        header = tk.Frame(main_frame, bg=CARD_BG)
        header.pack(fill=tk.X, pady=(0,10))
        tk.Label(header, text="消息通知", font=("微软雅黑", 16, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY).pack(side=tk.LEFT)
        # 列表区
        list_frame = tk.Frame(main_frame, bg=CARD_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        cols = ("类型","标题","内容","时间")
        self.notif_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        for col in cols:
            self.notif_tree.heading(col, text=col)
            self.notif_tree.column(col, width=250 if col=="内容" else 120)
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.notif_tree.yview)
        self.notif_tree.configure(yscrollcommand=scroll.set)
        self.notif_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        # 按钮区
        btnf = tk.Frame(main_frame, bg=CARD_BG)
        btnf.pack(pady=10)
        create_rounded_button(btnf, text="刷新", command=self.refresh_notifications, font=("微软雅黑",10), bg=PRIMARY_COLOR, fg="white", padx=12, pady=6, radius=6).pack(side=tk.LEFT, padx=6)
        create_rounded_button(btnf, text="标为已读", command=self.mark_notification_read, font=("微软雅黑",10), bg=SUCCESS_COLOR, fg="white", padx=12, pady=6, radius=6).pack(side=tk.LEFT, padx=6)
        create_rounded_button(btnf, text="全部标为已读", command=self.clear_all_notifications, font=("微软雅黑",10), bg=QUERY_COLOR, fg="white", padx=12, pady=6, radius=6).pack(side=tk.LEFT, padx=6)
        # tag styles: 区分未读/已读，已读使用主题主色（通常为黑色/深色）
        try:
            # 未读样式
            self.notif_tree.tag_configure('overdue_unread', foreground='#d32f2f')
            self.notif_tree.tag_configure('system_unread', foreground='#1976d2')
            # 已读样式（使用主题主文本色）
            self.notif_tree.tag_configure('overdue_read', foreground=TEXT_PRIMARY)
            self.notif_tree.tag_configure('system_read', foreground=TEXT_PRIMARY)
        except Exception:
            pass
        # 绑定双击查看消息详情
        self.notif_tree.bind("<Double-1>", self.on_notification_double_click)

    def refresh_notifications(self):
        """刷新消息通知：系统更新（静态） + 逾期提醒（从借阅记录计算）"""
        try:
            for it in self.notif_tree.get_children():
                self.notif_tree.delete(it)
        except Exception:
            return
        # 从服务器拉取用户接收到的邮件（作为消息展示）
        try:
            emails = self.client.get_user_emails(self.user['id'])
            if isinstance(emails, list) and emails:
                for e in emails:
                    try:
                        eid = e.get('id')
                        msg_type = '邮件'
                        title = e.get('subject', '')
                        content = e.get('body', '')
                        time_str = e.get('sent_at') or e.get('created_at') or ''
                        tag = 'system_unread' if e.get('status') == 'sent' else 'system_read'
                        iid = f"email_{eid}" if eid is not None else None
                        if iid:
                            self.notif_tree.insert("", tk.END, iid=iid, values=(msg_type, title, content, time_str), tags=(tag,))
                        else:
                            self.notif_tree.insert("", tk.END, values=(msg_type, title, content, time_str), tags=(tag,))
                    except Exception:
                        pass
            else:
                # fallback: 显示示例系统更新
                sys_updates = [
                    {"type":"系统更新","title":"版本 1.0.1","content":"修复已知bug并优化性能","time":datetime.now().strftime('%Y-%m-%d')},
                ]
                for u in sys_updates:
                    try:
                        self.notif_tree.insert("", tk.END, values=(u['type'], u['title'], u['content'], u['time']), tags=('system_unread',))
                    except Exception:
                        pass
        except Exception:
            # 如果拉取邮件失败，仍显示示例系统更新
            try:
                sys_updates = [
                    {"type":"系统更新","title":"版本 1.0.1","content":"修复已知bug并优化性能","time":datetime.now().strftime('%Y-%m-%d')},
                ]
                for u in sys_updates:
                    try:
                        self.notif_tree.insert("", tk.END, values=(u['type'], u['title'], u['content'], u['time']), tags=('system_unread',))
                    except Exception:
                        pass
            except Exception:
                pass
        # 逾期提醒
        try:
            borrows = self.client.get_my_borrows(self.user['id'], status='borrowed')
            for b in borrows:
                due = b.get('due_date')
                if due:
                    try:
                        due_date = datetime.strptime(due, '%Y-%m-%d').date()
                        if due_date < date.today():
                            days = (date.today() - due_date).days
                            title = f"图书逾期：{b.get('title','')}"
                            content = f"已逾期 {days} 天，应还日期 {due}"
                            time_str = b.get('borrow_date') or ''
                            # 逾期提醒默认为未读
                            self.notif_tree.insert("", tk.END, values=('逾期提醒', title, content, time_str), tags=('overdue_unread',))
                    except Exception:
                        pass
        except Exception:
            pass

    def mark_notification_read(self):
        sel = self.notif_tree.selection()
        if not sel:
            messagebox.showwarning("警告", "请选择要标记为已读的消息")
            return
        for s in sel:
            try:
                self.mark_notification_read_by_id(s)
            except Exception:
                pass

    def mark_notification_read_by_id(self, item_id):
        """标记单条消息为已读（更换标签以改变颜色）"""
        try:
            item = self.notif_tree.item(item_id)
            tags = item.get('tags', ()) or ()
            # 根据未读标签切换到已读标签
            new_tag = None
            if 'system_unread' in tags:
                new_tag = 'system_read'
            elif 'overdue_unread' in tags:
                new_tag = 'overdue_read'
            else:
                # 如果没有明确未读标签，统一使用 system_read
                new_tag = 'system_read'
            self.notif_tree.item(item_id, tags=(new_tag,))
        except Exception:
            pass

    def on_notification_double_click(self, event):
        """双击打开消息详情并自动标为已读"""
        try:
            sel = self.notif_tree.selection()
            if not sel:
                return
            item_id = sel[0]
            item = self.notif_tree.item(item_id)
            values = item.get('values', [])
            # values expected: (type, title, content, time)
            NotificationDetailWindow(self.root, self, item_id, values)
        except Exception:
            pass

    def clear_all_notifications(self):
        for it in list(self.notif_tree.get_children()):
            try:
                self.notif_tree.delete(it)
            except Exception:
                pass
    
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
            # 更新个人信息页面的图表
            if hasattr(self, 'borrow_chart_fig') and self.borrow_chart_fig:
                self.update_borrow_category_chart()
            try:
                self.refresh_recommendations()
            except Exception:
                pass
        else:
            messagebox.showerror("错误", "归还失败")
    
    def create_user_info_tab(self, parent):
        """创建个人信息标签页"""
        # 主容器
        main_frame = tk.Frame(parent, bg=CARD_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        header = tk.Frame(main_frame, bg=CARD_BG)
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(
            header,
            text="个人信息",
            font=("微软雅黑", 16, "bold"),
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
        ).pack(side=tk.LEFT)
        
        # 内容区域：左右分栏
        content_frame = tk.Frame(main_frame, bg=CARD_BG)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧表单框架
        form_frame = tk.Frame(content_frame, bg=CARD_BG, width=400)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 20))
        form_frame.pack_propagate(False)
        
        # 用户名（只读）
        tk.Label(form_frame, text="用户名:", font=("微软雅黑", 11), bg=CARD_BG, fg=TEXT_PRIMARY).grid(
            row=0, column=0, padx=15, pady=12, sticky="e"
        )
        self.info_username_label = tk.Label(
            form_frame, 
            text=self.user.get('username', ''), 
            font=("微软雅黑", 11), 
            fg=TEXT_SECONDARY,
            bg=CARD_BG
        )
        self.info_username_label.grid(row=0, column=1, padx=15, pady=12, sticky="w")
        
        # 姓名
        tk.Label(form_frame, text="姓名:", font=("微软雅黑", 11), bg=CARD_BG, fg=TEXT_PRIMARY).grid(
            row=1, column=0, padx=15, pady=12, sticky="e"
        )
        self.info_name_entry = tk.Entry(form_frame, font=("微软雅黑", 11), width=30)
        self.info_name_entry.insert(0, self.user.get('name', ''))
        self.info_name_entry.grid(row=1, column=1, padx=15, pady=12, sticky="w")
        
        # 角色（只读）
        tk.Label(form_frame, text="角色:", font=("微软雅黑", 11), bg=CARD_BG, fg=TEXT_PRIMARY).grid(
            row=2, column=0, padx=15, pady=12, sticky="e"
        )
        role_text = {'admin': '管理员', 'member': '会员', 'user': '普通用户'}
        self.info_role_label = tk.Label(
            form_frame, 
            text=role_text.get(self.user.get('role', ''), ''), 
            font=("微软雅黑", 11), 
            fg=TEXT_SECONDARY,
            bg=CARD_BG
        )
        self.info_role_label.grid(row=2, column=1, padx=15, pady=12, sticky="w")
        
        # 年龄
        tk.Label(form_frame, text="年龄:", font=("微软雅黑", 11), bg=CARD_BG, fg=TEXT_PRIMARY).grid(
            row=3, column=0, padx=15, pady=12, sticky="e"
        )
        self.info_age_entry = tk.Entry(form_frame, font=("微软雅黑", 11), width=30)
        age_value = self.user.get('age')
        if age_value is not None:
            self.info_age_entry.insert(0, str(age_value))
        self.info_age_entry.grid(row=3, column=1, padx=15, pady=12, sticky="w")
        
        # 邮箱
        tk.Label(form_frame, text="邮箱:", font=("微软雅黑", 11), bg=CARD_BG, fg=TEXT_PRIMARY).grid(
            row=4, column=0, padx=15, pady=12, sticky="e"
        )
        self.info_email_entry = tk.Entry(form_frame, font=("微软雅黑", 11), width=30)
        self.info_email_entry.insert(0, self.user.get('email', ''))
        self.info_email_entry.grid(row=4, column=1, padx=15, pady=12, sticky="w")
        
        # 电话
        tk.Label(form_frame, text="电话:", font=("微软雅黑", 11), bg=CARD_BG, fg=TEXT_PRIMARY).grid(
            row=5, column=0, padx=15, pady=12, sticky="e"
        )
        self.info_phone_entry = tk.Entry(form_frame, font=("微软雅黑", 11), width=30)
        self.info_phone_entry.insert(0, self.user.get('phone', ''))
        self.info_phone_entry.grid(row=5, column=1, padx=15, pady=12, sticky="w")
        
        # 右侧图表框架
        chart_frame = tk.Frame(content_frame, bg=CARD_BG)
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 图表标题
        tk.Label(
            chart_frame,
            text="个人借阅分类统计",
            font=("微软雅黑", 14, "bold"),
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
        ).pack(pady=(0, 10))
        
        # 创建饼状图
        if Figure is None or FigureCanvasTkAgg is None:
            tk.Label(
                chart_frame,
                text="缺少 matplotlib 依赖，无法显示图表。\n请安装 matplotlib>=3.5.0 后重试。",
                font=("微软雅黑", 11),
                fg="#f44336",
                bg=CARD_BG
            ).pack(expand=True)
            self.borrow_chart_fig = None
            self.borrow_chart_canvas = None
        else:
            # 缩小图表尺寸以节省页面空间
            self.borrow_chart_fig = Figure(figsize=(4, 4), dpi=100)
            self.borrow_chart_canvas = FigureCanvasTkAgg(self.borrow_chart_fig, master=chart_frame)
            # 不再强制全扩展，减少垂直占用
            self.borrow_chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=False, pady=(0, 8))
            # 初始化图表
            self.update_borrow_category_chart()
            # 推荐图书列表（基于用户喜好）
            reco_label = tk.Label(
                chart_frame,
                text="为你推荐",
                font=("微软雅黑", 12, "bold"),
                bg=CARD_BG,
                fg=TEXT_PRIMARY,
            )
            reco_label.pack(pady=(8, 4))

            # 推荐列表（Treeview）
            reco_columns = ("ID", "书名", "作者", "分类", "可借数量")
            self.reco_tree = ttk.Treeview(chart_frame, columns=reco_columns, show="headings", height=3)
            for col in reco_columns:
                self.reco_tree.heading(col, text=col)
                # 书名列稍宽
                width = 250 if col == "书名" else 100
                self.reco_tree.column(col, width=width)
            reco_scroll = ttk.Scrollbar(chart_frame, orient=tk.VERTICAL, command=self.reco_tree.yview)
            self.reco_tree.configure(yscrollcommand=reco_scroll.set)
            self.reco_tree.pack(fill=tk.BOTH, expand=False, padx=6, pady=(0, 6))
            reco_scroll.pack(fill=tk.Y, side=tk.RIGHT)

            # 推荐操作按钮
            reco_btn_frame = tk.Frame(chart_frame, bg=CARD_BG)
            reco_btn_frame.pack(pady=(0, 12))
            create_rounded_button(
                reco_btn_frame,
                text="查看详情",
                command=self.recommend_view_detail,
                font=("微软雅黑", 10),
                bg=PRIMARY_COLOR,
                fg="white",
                padx=12,
                pady=6,
                radius=6
            ).pack(side=tk.LEFT, padx=6)
            create_rounded_button(
                reco_btn_frame,
                text="借阅",
                command=self.recommend_borrow,
                font=("微软雅黑", 10),
                bg=SUCCESS_COLOR,
                fg="white",
                padx=12,
                pady=6,
                radius=6
            ).pack(side=tk.LEFT, padx=6)
        
        # 按钮框架
        btn_frame = tk.Frame(main_frame, bg=CARD_BG)
        btn_frame.pack(pady=20)
        
        create_rounded_button(
            btn_frame,
            text="保存",
            command=self.save_user_info,
            font=("微软雅黑", 11),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=25,
            pady=8,
            radius=6
        ).pack(side=tk.LEFT, padx=8)
        
        create_rounded_button(
            btn_frame,
            text="修改密码",
            command=self.change_password_from_tab,
            font=("微软雅黑", 11),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=25,
            pady=8,
            radius=6
        ).pack(side=tk.LEFT, padx=8)
        
        create_rounded_button(
            btn_frame,
            text="刷新信息",
            command=self.refresh_user_info,
            font=("微软雅黑", 11),
            bg=QUERY_COLOR,
            fg="white",
            padx=25,
            pady=8,
            radius=6
        ).pack(side=tk.LEFT, padx=8)
    
    def save_user_info(self):
        """保存个人信息（从标签页）"""
        name = self.info_name_entry.get().strip()
        email = self.info_email_entry.get().strip()
        phone = self.info_phone_entry.get().strip()
        age_text = self.info_age_entry.get().strip()
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
            # 更新顶部栏显示的名称
            self.refresh_header_name()
            try:
                self.refresh_recommendations()
            except Exception:
                pass
        else:
            messagebox.showerror("错误", "更新失败")
    
    def _map_to_standard_category(self, category: str) -> str:
        """将分类名称映射到标准分类（与models.py中的逻辑一致）"""
        if not category:
            return '未分类'
        
        category_clean = category.strip()
        if not category_clean:
            return '未分类'
        
        category_lower = category_clean.lower()
        
        # 定义标准分类关键词映射
        category_mapping = {
            '教育类': [
                'education', 'educational', 'textbook', '教材', '教育', '学习', '教学', 
                '培训', '课程', 'study', 'teaching', 'learning', 'school', 'academic'
            ],
            '科普类': [
                'science', 'scientific', '科普', '科学', '技术', 'technology', '物理', 
                'chemistry', 'biology', '数学', 'math', '天文', 'astronomy', '地理', 
                'geography', '自然', 'nature', 'physics', '化学', '生物', 'engineering'
            ],
            '文学类': [
                'classic literature', 'juvenile fiction', 'young adult', 
                'literature', 'literary', '文学', '小说', 'fiction', 'novel', '诗歌', 
                'poetry', 'poem', '散文', 'essay', '故事', 'story', 'tale', 
                'children', 'drama', 'play', 'theater', 'theatre', 'comedy', 
                'tragedy', 'romance', 'mystery', 'thriller', 'horror', 'fantasy'
            ],
            '历史类': [
                'history', 'historical', '历史', '古代', 'ancient', '近代', 'modern', 
                '现代', 'contemporary', '史', '传记', 'biography', 'autobiography', 
                'memoir', 'war', 'military', 'politics', 'political', 'civilization'
            ],
            '艺术类': [
                'art', 'arts', '艺术', '美术', '绘画', 'painting', 'drawing', '音乐', 
                'music', 'musical', '舞蹈', 'dance', '戏剧', 'theater', 'theatre', 
                '电影', 'film', 'cinema', '摄影', 'photography', '设计', 'design', 
                'graphic', 'fashion', 'architecture', 'sculpture', 'visual'
            ]
        }
        
        # 检查是否已经是标准分类名称
        if category_clean in ['教育类', '科普类', '文学类', '历史类', '艺术类', '其他类', '未分类']:
            return category_clean
        
        # 检查是否包含标准分类关键词（中文）
        if '教育' in category_clean:
            return '教育类'
        elif '科普' in category_clean or '科学' in category_clean:
            return '科普类'
        elif '文学' in category_clean:
            return '文学类'
        elif '历史' in category_clean:
            return '历史类'
        elif '艺术' in category_clean:
            return '艺术类'
        
        # 按优先级检查英文关键词
        for std_cat, keywords in category_mapping.items():
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            for keyword in sorted_keywords:
                keyword_lower = keyword.lower()
                if ' ' in keyword:
                    if keyword_lower in category_lower:
                        return std_cat
                else:
                    pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                    if re.search(pattern, category_lower):
                        return std_cat
        
        return '其他类'
    
    def _get_user_borrow_categories(self):
        """获取用户借阅的各类图书统计"""
        # 获取所有借阅记录
        borrows = self.client.get_my_borrows(self.user['id'], status=None)
        
        # 统计各类图书数量
        category_count = {}
        for borrow in borrows:
            # 获取图书信息
            book_id = borrow.get('book_id')
            if book_id:
                book = self.client.get_book(book_id)
                if book:
                    category = book.get('category', '')
                    # 映射到标准分类
                    std_category = self._map_to_standard_category(category)
                    category_count[std_category] = category_count.get(std_category, 0) + 1
        
        return category_count
    
    def update_borrow_category_chart(self):
        """更新借阅分类饼状图"""
        if Figure is None or self.borrow_chart_fig is None:
            return
        
        try:
            # 获取分类统计
            category_count = self._get_user_borrow_categories()
            
            # 清空图表
            self.borrow_chart_fig.clf()
            ax = self.borrow_chart_fig.add_subplot(111)
            
            if not category_count:
                # 没有借阅记录
                ax.text(0.5, 0.5, "暂无借阅记录", ha='center', va='center', fontsize=14)
                ax.axis('off')
            else:
                # 准备数据
                categories = list(category_count.keys())
                counts = list(category_count.values())
                
                # 定义标准分类的显示顺序和颜色
                category_order = ['教育类', '科普类', '文学类', '历史类', '艺术类', '其他类', '未分类']
                colors = ['#42a5f5', '#66bb6a', '#ffa726', '#ab47bc', '#ef5350', '#78909c', '#bdbdbd']
                
                # 按顺序排序
                sorted_data = sorted(
                    zip(categories, counts),
                    key=lambda x: (category_order.index(x[0]) if x[0] in category_order else 999, -x[1])
                )
                categories, counts = zip(*sorted_data) if sorted_data else ([], [])
                
                # 创建颜色映射
                color_map = {cat: colors[i % len(colors)] for i, cat in enumerate(category_order)}
                pie_colors = [color_map.get(cat, '#bdbdbd') for cat in categories]
                
                # 绘制饼状图
                wedges, texts, autotexts = ax.pie(
                    counts,
                    labels=categories,
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=pie_colors,
                    textprops={'fontsize': 10}
                )
                
                # 设置标题
                ax.set_title("个人借阅分类占比", fontsize=12, fontweight='bold', pad=20)
                
                # 调整文本样式
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            
            self.borrow_chart_fig.tight_layout()
            self.borrow_chart_canvas.draw()
        except Exception as e:
            print(f"更新借阅分类图表失败: {e}")
        # 更新推荐图书（借阅分类变化时也刷新推荐）
        try:
            self.refresh_recommendations()
        except Exception:
            pass

    def refresh_recommendations(self, limit: int = 3):
        """根据用户的借阅偏好推荐图书并展示在推荐列表中"""
        # 清空现有推荐
        try:
            for item in self.reco_tree.get_children():
                self.reco_tree.delete(item)
        except Exception:
            # 如果推荐控件尚未创建，直接返回
            return

        # 获取用户借阅分类统计（已映射为标准分类）
        category_count = self._get_user_borrow_categories()
        top_category = None
        if category_count:
            # 选择借阅次数最多的分类
            try:
                top_category = max(category_count.items(), key=lambda x: x[1])[0]
            except Exception:
                top_category = None

        # 获取所有图书并在客户端侧进行过滤（因为服务端search按原始category匹配）
        books = self.client.search_books()
        recommendations = []
        if top_category:
            for book in books:
                try:
                    if self._map_to_standard_category(book.get('category', '')) == top_category:
                        recommendations.append(book)
                except Exception:
                    continue

        # 如果没有推荐（如用户无借阅历史），则使用有库存的热门图书（列表前几项）
        if not recommendations:
            for book in books:
                if book.get('available_copies', 0) > 0:
                    recommendations.append(book)

        # 限制数量并插入到Treeview
        for book in recommendations[:limit]:
            self.reco_tree.insert("", tk.END, values=(
                book.get('id'),
                book.get('title', ''),
                book.get('author', ''),
                book.get('category', ''),
                book.get('available_copies', 0)
            ))

    def recommend_view_detail(self):
        """查看推荐列表中选中图书的详情"""
        selection = self.reco_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要查看的推荐图书")
            return
        item = self.reco_tree.item(selection[0])
        book_id = item['values'][0]
        book = self.client.get_book(book_id)
        if book:
            BookDetailWindow(self.root, book)

    def recommend_borrow(self):
        """从推荐列表借阅选中图书"""
        selection = self.reco_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要借阅的推荐图书")
            return
        item = self.reco_tree.item(selection[0])
        book_id = item['values'][0]
        available = item['values'][4] if len(item['values']) > 4 else 0
        try:
            available = int(available)
        except Exception:
            available = 0

        if available <= 0:
            messagebox.showwarning("警告", "该图书暂无可借副本")
            return

        if not messagebox.askyesno("确认", "确定要借阅这本推荐图书吗？"):
            return

        success, message = self.client.borrow_book(self.user['id'], book_id)
        if success:
            messagebox.showinfo("成功", message)
            self.refresh_books()
            self.refresh_my_borrows()
            # 更新图表与推荐
            if hasattr(self, 'borrow_chart_fig') and self.borrow_chart_fig:
                self.update_borrow_category_chart()
            try:
                self.refresh_recommendations()
            except Exception:
                pass
        else:
            messagebox.showerror("错误", message)
    
    def refresh_user_info(self):
        """刷新个人信息"""
        user_info = self.client.get_user_info(self.user['id'])
        if user_info:
            self.user.update(user_info)
            # 更新表单字段
            self.info_username_label.config(text=self.user.get('username', ''))
            self.info_name_entry.delete(0, tk.END)
            self.info_name_entry.insert(0, self.user.get('name', ''))
            role_text = {'admin': '管理员', 'member': '会员', 'user': '普通用户'}
            self.info_role_label.config(text=role_text.get(self.user.get('role', ''), ''))
            self.info_age_entry.delete(0, tk.END)
            age_value = self.user.get('age')
            if age_value is not None:
                self.info_age_entry.insert(0, str(age_value))
            self.info_email_entry.delete(0, tk.END)
            self.info_email_entry.insert(0, self.user.get('email', ''))
            self.info_phone_entry.delete(0, tk.END)
            self.info_phone_entry.insert(0, self.user.get('phone', ''))
            # 更新顶部栏
            self.refresh_header_name()
            # 更新图表
            self.update_borrow_category_chart()
            # 刷新推荐图书
            try:
                self.refresh_recommendations()
            except Exception:
                pass
            try:
                self.refresh_notifications()
            except Exception:
                pass
            messagebox.showinfo("成功", "信息已刷新")
    
    def refresh_header_name(self):
        """刷新顶部栏显示的名称"""
        role_text = "会员" if self.user.get("role") == "member" else "普通用户"
        self.header_name_label.config(text=f"{role_text}: {self.user.get('name', '')}")
    
    def change_password_from_tab(self):
        """从标签页修改密码"""
        dialog = ChangePasswordDialog(self.root, self.client, self.user['id'])
        self.root.wait_window(dialog.window)
    
    def show_user_info(self):
        """显示个人信息窗口（保留原有弹窗功能）"""
        UserInfoWindow(self.root, self.client, self.user)
    
    def load_user_info(self):
        """加载用户信息"""
        user_info = self.client.get_user_info(self.user['id'])
        if user_info:
            self.user.update(user_info)
        # 加载完成后刷新推荐
        try:
            self.refresh_recommendations()
        except Exception:
            pass
        try:
            self.refresh_notifications()
        except Exception:
            pass
    
    
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

        create_rounded_button(
            card,
            text="关闭",
            command=self.window.destroy,
            font=("微软雅黑", 10, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=20,
            pady=8,
            radius=6
        ).pack(pady=12)

class NotificationDetailWindow:
    """消息详情弹窗：展示消息内容并支持标为已读"""

    def __init__(self, parent, user_window, item_id, values):
        """
        values: (type, title, content, time)
        """
        self.user_window = user_window
        self.item_id = item_id
        self.window = tk.Toplevel(parent)
        self.window.title("消息详情")
        self.window.geometry("520x320")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        self.create_widgets(values)

    def create_widgets(self, values):
        msg_type = values[0] if len(values) > 0 else ''
        title = values[1] if len(values) > 1 else ''
        content = values[2] if len(values) > 2 else ''
        time_str = values[3] if len(values) > 3 else ''

        frame = tk.Frame(self.window, bg=CARD_BG)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        tk.Label(frame, text=f"类型：{msg_type}", font=("微软雅黑", 11, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0,6))
        tk.Label(frame, text=f"标题：{title}", font=("微软雅黑", 12), bg=CARD_BG, fg=TEXT_PRIMARY, wraplength=480, justify="left").pack(anchor="w", pady=(0,6))
        tk.Label(frame, text=f"时间：{time_str}", font=("微软雅黑", 10), bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor="w", pady=(0,8))

        content_frame = tk.Frame(frame, bg="white", bd=1, relief="solid")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0,8))
        lbl = tk.Label(content_frame, text=content, font=("微软雅黑", 11), bg="white", fg=TEXT_PRIMARY, wraplength=480, justify="left")
        lbl.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        btn_frame = tk.Frame(frame, bg=CARD_BG)
        btn_frame.pack(pady=6)
        create_rounded_button(btn_frame, text="标为已读并关闭", command=self.mark_read_and_close, font=("微软雅黑", 10), bg=SUCCESS_COLOR, fg="white", padx=12, pady=6, radius=6).pack(side=tk.LEFT, padx=6)
        create_rounded_button(btn_frame, text="关闭", command=self.window.destroy, font=("微软雅黑", 10), bg=PRIMARY_COLOR, fg="white", padx=12, pady=6, radius=6).pack(side=tk.LEFT, padx=6)

    def mark_read_and_close(self):
        try:
            self.user_window.mark_notification_read_by_id(self.item_id)
        except Exception:
            pass
        self.window.destroy()

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
        
        create_rounded_button(
            btn_frame,
            text="保存",
            command=self.save,
            font=("微软雅黑", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
            radius=6
        ).pack(side=tk.LEFT, padx=5)
        
        create_rounded_button(
            btn_frame,
            text="修改密码",
            command=self.change_password,
            font=("微软雅黑", 10),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=5,
            radius=6
        ).pack(side=tk.LEFT, padx=5)
        
        create_rounded_button(
            btn_frame,
            text="关闭",
            command=self.window.destroy,
            font=("微软雅黑", 10),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=5,
            radius=6
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
        
        create_rounded_button(
            btn_frame,
            text="确定",
            command=self.save,
            font=("微软雅黑", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
            radius=6
        ).pack(side=tk.LEFT, padx=5)
        
        create_rounded_button(
            btn_frame,
            text="取消",
            command=self.window.destroy,
            font=("微软雅黑", 10),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=5,
            radius=6
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

