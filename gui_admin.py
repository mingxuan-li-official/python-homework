"""
管理员界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
from ui_theme import (
    PRIMARY_COLOR,
    PRIMARY_DARK,
    WARNING_COLOR,
    SUCCESS_COLOR,
    DANGER_COLOR,
    NEUTRAL_BG,
    CARD_BG,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    QUERY_COLOR,
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

class AdminWindow:
    """管理员窗口"""
    
    def __init__(self, root, client, user):
        self.root = root
        self.client = client
        self.user = user

        # 统一背景 + 带侧边栏布局
        self.root.configure(bg=NEUTRAL_BG)
        self._build_layout()
        self._init_styles()
        self.create_widgets()
        self.refresh_statistics()
        self.refresh_admin_charts()
        self.refresh_books()
        self.refresh_borrows()
        self.refresh_users()

    def _switch_tab(self, index: int):
        """侧边栏切换到指定标签页"""
        try:
            self.notebook.select(index)
        except Exception:
            pass

    def _init_styles(self):
        """统一设置表格样式，使其更贴近 Web 风格"""
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="white",
            foreground=TEXT_PRIMARY,
            fieldbackground="white",
            rowheight=28,
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
        style.map("Treeview", highlightthickness=[("selected", 0)])

    def _build_layout(self):
        """构建侧边栏 + 顶部栏 + 内容区基础骨架"""
        # 整体容器
        self.shell = tk.Frame(self.root, bg=NEUTRAL_BG)
        self.shell.pack(fill=tk.BOTH, expand=True)

        # 侧边栏
        self.sidebar = tk.Frame(self.shell, bg="#1f2d3d", width=210)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="图书馆管理系统",
            bg="#1f2d3d",
            fg="white",
            font=("微软雅黑", 13, "bold"),
            pady=18,
        ).pack(fill=tk.X)

        # 侧边栏按钮
        menu_items = [
            ("首页总览", self.refresh_statistics),
            ("图书管理", lambda: self._switch_tab(1)),
            ("借阅管理", lambda: self._switch_tab(2)),
            ("用户管理", lambda: self._switch_tab(3)),
        ]
        for text, command in menu_items:
            btn = tk.Button(
                self.sidebar,
                text=text,
                command=command,
                anchor="w",
                padx=26,
                pady=10,
                relief="flat",
                bg="#243447",
                fg="white",
                activebackground="#30455e",
                activeforeground="white",
                bd=0,
                font=("微软雅黑", 10),
                cursor="hand2",
            )
            btn.pack(fill=tk.X, pady=(0, 2))

        # 右侧主体
        self.main_area = tk.Frame(self.shell, bg=NEUTRAL_BG)
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 顶部工具栏（白色）
        self.header = tk.Frame(self.main_area, bg="white", height=56, bd=0, relief="solid")
        self.header.pack(fill=tk.X, side=tk.TOP)
        self.header.pack_propagate(False)

        tk.Label(
            self.header,
            text="管理控制台",
            bg="white",
            fg=TEXT_PRIMARY,
            font=("微软雅黑", 12, "bold"),
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            self.header,
            text=f"{self.user.get('name', '')}（管理员）",
            bg="white",
            fg=TEXT_SECONDARY,
            font=("微软雅黑", 10),
        ).pack(side=tk.RIGHT, padx=12)

        tk.Button(
            self.header,
            text="退出登录",
            command=self.logout,
            bg=DANGER_COLOR,
            fg="white",
            font=("微软雅黑", 10),
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=14)

        # 主内容卡片
        self.main_card = tk.Frame(self.main_area, bg=CARD_BG, bd=0, relief="flat")
        self.main_card.pack(fill=tk.BOTH, expand=True, padx=22, pady=18)
    
    def create_widgets(self):
        """创建界面组件"""
        # 次级标题区域
        sub_header = tk.Frame(self.main_card, bg=CARD_BG)
        sub_header.pack(fill=tk.X, pady=(6, 2), padx=10)
        tk.Label(
            sub_header,
            text="工作台",
            font=("微软雅黑", 12, "bold"),
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
        ).pack(side=tk.LEFT)
        tk.Label(
            sub_header,
            text="图书 / 借阅 / 用户 一站式管理",
            font=("微软雅黑", 10),
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
        ).pack(side=tk.LEFT, padx=12)

        # 创建Notebook（标签页）
        self.notebook = ttk.Notebook(self.main_card)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        
        # 统计信息标签页
        stats_frame = tk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="统计信息")
        self.create_stats_tab(stats_frame)
        
        # 图书管理标签页
        books_frame = tk.Frame(self.notebook)
        self.notebook.add(books_frame, text="图书管理")
        self.create_books_tab(books_frame)
        
        # 借阅管理标签页
        borrows_frame = tk.Frame(self.notebook)
        self.notebook.add(borrows_frame, text="借阅管理")
        self.create_borrows_tab(borrows_frame)
        
        # 用户管理标签页
        users_frame = tk.Frame(self.notebook)
        self.notebook.add(users_frame, text="用户管理")
        self.create_users_tab(users_frame)
    
    def create_stats_tab(self, parent):
        """创建统计信息标签页"""
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        content_frame = tk.Frame(stats_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧文字统计
        text_frame = tk.Frame(content_frame, width=320)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        text_frame.pack_propagate(False)
        
        self.stats_text = tk.Text(text_frame, font=("微软雅黑", 12), wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # 右侧图表
        chart_frame = tk.Frame(content_frame)
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if Figure is None or FigureCanvasTkAgg is None:
            tk.Label(
                chart_frame,
                text="缺少 matplotlib 依赖，无法显示图表。\n请安装 matplotlib>=3.5.0 后重试。",
                font=("微软雅黑", 12),
                fg="#f44336"
            ).pack(expand=True)
        else:
            self.chart_notebook = ttk.Notebook(chart_frame)
            self.chart_notebook.pack(fill=tk.BOTH, expand=True)
            
            self.inventory_chart_frame = tk.Frame(self.chart_notebook)
            self.chart_notebook.add(self.inventory_chart_frame, text="图书库存/分类结构")
            self.inventory_fig = Figure(figsize=(6, 4), dpi=100)
            self.inventory_canvas = FigureCanvasTkAgg(self.inventory_fig, master=self.inventory_chart_frame)
            self.inventory_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.borrow_chart_frame = tk.Frame(self.chart_notebook)
            self.chart_notebook.add(self.borrow_chart_frame, text="借阅趋势与行为")
            self.borrow_fig = Figure(figsize=(7, 5), dpi=100)
            self.borrow_canvas = FigureCanvasTkAgg(self.borrow_fig, master=self.borrow_chart_frame)
            self.borrow_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(stats_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            btn_frame,
            text="刷新统计",
            command=self.refresh_statistics,
            font=("微软雅黑", 10),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="刷新图表",
            command=self.refresh_admin_charts,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def create_books_tab(self, parent):
        """创建图书管理标签页"""
        # 搜索框架
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="搜索:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("微软雅黑", 10), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
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
            text="添加图书",
            command=self.show_add_book,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="爬取图书",
            command=self.show_import_books,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
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
        
        # 创建Treeview
        columns = ("ID", "书名", "作者", "ISBN", "分类", "出版社", "总数量", "可借数量", "状态")
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
            text="编辑",
            command=self.edit_book,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="删除",
            command=self.delete_book,
            font=("微软雅黑", 10),
            bg=DANGER_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def create_borrows_tab(self, parent):
        """创建借阅管理标签页"""
        # 筛选框架
        filter_frame = tk.Frame(parent)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(filter_frame, text="状态筛选:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="all")
        status_options = [("全部", "all"), ("借阅中", "borrowed"), ("已归还", "returned"), ("逾期", "overdue")]
        for text, value in status_options:
            tk.Radiobutton(filter_frame, text=text, variable=self.status_var,
                          value=value, font=("微软雅黑", 10),
                          command=self.refresh_borrows).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame,
            text="刷新",
            command=self.refresh_borrows,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
        
        # 借阅记录列表
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "用户名", "姓名", "书名", "作者", "借阅日期", "应还日期", "归还日期", "状态")
        self.borrows_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.borrows_tree.heading(col, text=col)
            self.borrows_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.borrows_tree.yview)
        self.borrows_tree.configure(yscrollcommand=scrollbar.set)
        
        self.borrows_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_users_tab(self, parent):
        """创建用户管理标签页"""
        # 搜索框架
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="搜索:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.user_search_entry = tk.Entry(search_frame, font=("微软雅黑", 10), width=30)
        self.user_search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="搜索",
            command=self.search_users,
            font=("微软雅黑", 10),
            bg=QUERY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="刷新",
            command=self.refresh_users,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # 用户列表
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview
        columns = ("ID", "用户名", "姓名", "年龄", "角色", "邮箱", "电话", "注册时间")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            width = 90 if col == "年龄" else 120
            self.users_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.users_tree.bind("<Double-1>", self.on_user_double_click)
        
        # 操作按钮
        btn_frame = tk.Frame(parent)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="增加用户",
            command=self.add_user,
            font=("微软雅黑", 10),
            bg=SUCCESS_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="编辑",
            command=self.edit_user,
            font=("微软雅黑", 10),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="删除用户",
            command=self.delete_user,
            font=("微软雅黑", 10),
            bg=DANGER_COLOR,
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def refresh_statistics(self):
        """刷新统计信息"""
        stats = self.client.get_statistics()
        if stats:
            self.stats_text.delete(1.0, tk.END)
            stats_text = f"""
图书管理系统统计信息
{'='*50}

总图书数量: {stats.get('total_books', 0)} 册
可借图书数量: {stats.get('available_books', 0)} 册

总借阅记录: {stats.get('total_borrows', 0)} 条
当前借阅中: {stats.get('current_borrows', 0)} 条
逾期记录: {stats.get('overdue', 0)} 条

统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            self.stats_text.insert(1.0, stats_text)
    
    def refresh_admin_charts(self):
        """刷新管理员图表"""
        if Figure is None or FigureCanvasTkAgg is None:
            return
        try:
            data = self.client.get_admin_dashboard_data(days=30)
            if not data:
                messagebox.showwarning("提示", "暂无法获取统计数据")
                return
            self._update_inventory_chart(
                data.get('category_summary', []),
                data.get('status_summary', [])
            )
            self._update_borrow_chart(
                data.get('borrow_trend', []),
                data.get('borrow_status', []),
                data.get('borrow_durations', []),
                data.get('overdue_days', [])
            )
        except Exception as e:
            messagebox.showerror("错误", f"刷新图表失败: {str(e)}")
    
    def _update_inventory_chart(self, category_summary, status_summary):
        """更新图书库存图"""
        if Figure is None:
            return
        self.inventory_fig.clf()
        
        ax1 = self.inventory_fig.add_subplot(211)
        categories = [row.get('category', '未分类') for row in category_summary]
        counts = [row.get('book_count', 0) for row in category_summary]
        if categories and any(counts):
            ax1.bar(categories, counts, color="#42a5f5")
            ax1.set_ylabel("图书数量")
            ax1.set_title("分类图书数量")
            ax1.tick_params(axis='x', rotation=45)
        else:
            ax1.text(0.5, 0.5, "暂无分类数据", ha='center', va='center')
            ax1.axis('off')
        
        ax2 = self.inventory_fig.add_subplot(212)
        statuses = [row.get('status', '未知') for row in status_summary]
        status_counts = [row.get('count', 0) for row in status_summary]
        status_map = {
            'available': '可借',
            'borrowed': '借出',
            'unavailable': '不可借',
            'maintenance': '维护'
        }
        display_labels = [status_map.get(status, status) for status in statuses]
        if status_counts and any(status_counts):
            ax2.pie(status_counts, labels=display_labels, autopct="%1.1f%%", startangle=90)
            ax2.set_title("图书状态占比")
        else:
            ax2.text(0.5, 0.5, "暂无状态数据", ha='center', va='center')
            ax2.axis('off')
        
        self.inventory_fig.tight_layout()
        self.inventory_canvas.draw()
    
    def _update_borrow_chart(self, trend, status_counts, durations, overdue_days):
        """更新借阅相关图表"""
        if Figure is None:
            return
        self.borrow_fig.clf()
        ax_trend = self.borrow_fig.add_subplot(221)
        ax_status = self.borrow_fig.add_subplot(222)
        ax_duration = self.borrow_fig.add_subplot(223)
        ax_overdue = self.borrow_fig.add_subplot(224)
        
        # 仅展示最近7天趋势，缺失日期填0
        trend_map = {item.get('day'): item for item in trend if item.get('day')}
        week_days = []
        borrow_vals = []
        return_vals = []
        today = datetime.now().date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            key = day.isoformat()
            data = trend_map.get(key, {})
            week_days.append(day.strftime('%m-%d'))
            borrow_vals.append(data.get('borrow_count', 0))
            return_vals.append(data.get('return_count', 0))
        if week_days:
            ax_trend.plot(week_days, borrow_vals, label="借阅", marker="o", color="#4CAF50")
            ax_trend.plot(week_days, return_vals, label="归还", marker="o", color="#FF9800")
            ax_trend.set_title("借阅/归还趋势 (近7天)")
            ax_trend.tick_params(axis='x', rotation=45)
            ax_trend.legend()
        else:
            ax_trend.text(0.5, 0.5, "暂无趋势数据", ha='center', va='center')
            ax_trend.axis('off')
        
        statuses = [row.get('status', '未知') for row in status_counts]
        counts = [row.get('count', 0) for row in status_counts]
        status_map = {
            'borrowed': '借阅中',
            'returned': '已归还',
            'overdue': '逾期'
        }
        labels = [status_map.get(status, status) for status in statuses]
        if counts and any(counts):
            ax_status.bar(labels, counts, color="#9C27B0")
            ax_status.set_title("借阅状态分布")
        else:
            ax_status.text(0.5, 0.5, "暂无借阅状态数据", ha='center', va='center')
            ax_status.axis('off')
        
        if durations:
            bins = min(10, len(set(durations)))
            ax_duration.hist(durations, bins=bins, color="#03A9F4")
            ax_duration.set_title("借阅时长分布 (天)")
            ax_duration.set_xlabel("天数")
            ax_duration.set_ylabel("记录数")
        else:
            ax_duration.text(0.5, 0.5, "暂无借阅时长数据", ha='center', va='center')
            ax_duration.axis('off')
        
        if overdue_days:
            bins = min(10, len(set(overdue_days)))
            ax_overdue.hist(overdue_days, bins=bins, color="#E91E63")
            ax_overdue.set_title("逾期天数分布")
            ax_overdue.set_xlabel("天数")
            ax_overdue.set_ylabel("记录数")
        else:
            ax_overdue.text(0.5, 0.5, "暂无逾期数据", ha='center', va='center')
            ax_overdue.axis('off')
        
        self.borrow_fig.tight_layout()
        self.borrow_canvas.draw()
    
    def refresh_books(self):
        """刷新图书列表"""
        # 清空现有数据
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        # 获取所有图书（传递空字符串作为keyword，确保返回所有图书）
        books = self.client.search_books(keyword="", category="")
        
        # 调试信息
        if not books:
            print("警告: 未获取到任何图书数据")
        
        # 显示图书列表
        for book in books:
            self.books_tree.insert("", tk.END, values=(
                book.get('id', ''),
                book.get('title', ''),
                book.get('author', ''),
                book.get('isbn', ''),
                book.get('category', ''),
                book.get('publisher', ''),
                book.get('total_copies', 0),
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
                book.get('total_copies', 0),
                book.get('available_copies', 0),
                book.get('status', 'available')
            ))
    
    def show_add_book(self):
        """显示添加图书对话框"""
        dialog = BookDialog(self.root, self.client, None)
        self.root.wait_window(dialog.window)
        self.refresh_books()
    
    def on_book_double_click(self, event):
        """双击图书事件"""
        self.edit_book()
    
    def edit_book(self):
        """编辑图书"""
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的图书")
            return
        
        item = self.books_tree.item(selection[0])
        book_id = item['values'][0]
        
        book = self.client.get_book(book_id)
        if book:
            dialog = BookDialog(self.root, self.client, book)
            self.root.wait_window(dialog.window)
            self.refresh_books()
    
    def delete_book(self):
        """删除图书"""
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的图书")
            return
        
        if not messagebox.askyesno("确认", "确定要删除这本图书吗？"):
            return
        
        item = self.books_tree.item(selection[0])
        book_id = item['values'][0]
        
        if self.client.delete_book(book_id):
            messagebox.showinfo("成功", "删除成功")
            self.refresh_books()
        else:
            messagebox.showerror("错误", "删除失败")
    
    def refresh_borrows(self):
        """刷新借阅记录"""
        # 清空现有数据
        for item in self.borrows_tree.get_children():
            self.borrows_tree.delete(item)
        
        try:
            # 获取借阅记录
            status = self.status_var.get()
            status = None if status == "all" else status
            borrows = self.client.get_all_borrows(status)
            
            # 确保 borrows 是列表
            if not isinstance(borrows, list):
                borrows = []
            
            # 显示借阅记录
            if borrows:
                for borrow in borrows:
                    # 格式化日期
                    borrow_date = borrow.get('borrow_date', '')
                    if borrow_date and isinstance(borrow_date, str):
                        try:
                            # 如果是 ISO 格式，转换为更易读的格式
                            if 'T' in borrow_date:
                                borrow_date = borrow_date.split('T')[0]
                        except:
                            pass
                    
                    due_date = borrow.get('due_date', '')
                    if due_date and isinstance(due_date, str):
                        try:
                            if 'T' in due_date:
                                due_date = due_date.split('T')[0]
                        except:
                            pass
                    
                    return_date = borrow.get('return_date', '') or '未归还'
                    if return_date and return_date != '未归还' and isinstance(return_date, str):
                        try:
                            if 'T' in return_date:
                                return_date = return_date.split('T')[0]
                        except:
                            pass
                    
                    # 格式化状态显示
                    status_text = borrow.get('status', '')
                    status_map = {
                        'borrowed': '借阅中',
                        'returned': '已归还',
                        'overdue': '逾期'
                    }
                    status_display = status_map.get(status_text, status_text)
                    
                    self.borrows_tree.insert("", tk.END, values=(
                        borrow.get('id', ''),
                        borrow.get('username', ''),
                        borrow.get('user_name', ''),
                        borrow.get('title', ''),
                        borrow.get('author', ''),
                        borrow_date,
                        due_date,
                        return_date,
                        status_display
                    ))
            # 如果没有数据，不显示任何内容（空列表表示没有记录）
        except Exception as e:
            messagebox.showerror("错误", f"刷新借阅记录失败: {str(e)}")
            print(f"刷新借阅记录错误: {e}")
    
    def refresh_users(self):
        """刷新用户列表"""
        # 清空现有数据
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            # 获取所有用户
            users = self.client.get_all_users()
            
            # 确保 users 是列表
            if not isinstance(users, list):
                users = []
            
            # 显示用户列表
            if users:
                role_text = {'admin': '管理员', 'member': '会员', 'user': '普通用户'}
                for user in users:
                    # 格式化创建时间
                    created_at = user.get('created_at', '')
                    if created_at and isinstance(created_at, str):
                        try:
                            # 如果是 ISO 格式，转换为更易读的格式
                            if 'T' in created_at:
                                created_at = created_at.replace('T', ' ').split('.')[0]
                        except:
                            pass
                    
                    self.users_tree.insert("", tk.END, values=(
                        user.get('id', ''),
                        user.get('username', ''),
                        user.get('name', ''),
                        user.get('age') if user.get('age') is not None else '',
                        role_text.get(user.get('role', ''), user.get('role', '')),
                        user.get('email', ''),
                        user.get('phone', ''),
                        created_at
                    ))
            # 如果没有数据，不显示任何内容（空列表表示没有记录）
        except Exception as e:
            messagebox.showerror("错误", f"刷新用户列表失败: {str(e)}")
            print(f"刷新用户列表错误: {e}")
    
    def search_users(self):
        """搜索用户"""
        keyword = self.user_search_entry.get().strip().lower()
        users = self.client.get_all_users()
        
        # 清空现有数据
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # 显示搜索结果
        role_text = {'admin': '管理员', 'member': '会员', 'user': '普通用户'}
        for user in users:
            # 搜索用户名、姓名、邮箱
            age_value = user.get('age')
            age_str = str(age_value) if age_value not in (None, '') else ''
            if (keyword in user['username'].lower() or 
                keyword in user.get('name', '').lower() or
                keyword in user.get('email', '').lower() or
                (age_str and keyword in age_str.lower())):
                self.users_tree.insert("", tk.END, values=(
                    user['id'],
                    user['username'],
                    user.get('name', ''),
                    age_value if age_value is not None else '',
                    role_text.get(user.get('role', ''), user.get('role', '')),
                    user.get('email', ''),
                    user.get('phone', ''),
                    user.get('created_at', '')
                ))
    
    def on_user_double_click(self, event):
        """双击用户事件"""
        self.edit_user()
    
    def add_user(self):
        """添加用户"""
        dialog = AddUserDialog(self.root, self.client)
        self.root.wait_window(dialog.window)
        self.refresh_users()
    
    def edit_user(self):
        """编辑用户"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的用户")
            return
        
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        
        # 获取用户信息
        users = self.client.get_all_users()
        user = None
        for u in users:
            if u['id'] == user_id:
                user = u
                break
        
        if user:
            dialog = UserDialog(self.root, self.client, user)
            self.root.wait_window(dialog.window)
            self.refresh_users()
    
    def delete_user(self):
        """删除用户"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的用户")
            return
        
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除用户 '{username}' 吗？\n\n注意：如果该用户有未归还的图书，将无法删除。"):
            return
        
        if self.client.admin_delete_user(user_id):
            messagebox.showinfo("成功", "删除成功")
            self.refresh_users()
        else:
            messagebox.showerror("错误", "删除失败，用户可能不存在或有未归还的图书")
    
    def show_import_books(self):
        """显示爬取图书对话框"""
        dialog = ImportBooksDialog(self.root, self.client)
        self.root.wait_window(dialog.window)
        if dialog.success:
            self.refresh_books()
    
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

class BookDialog:
    """图书编辑对话框"""
    
    def __init__(self, parent, client, book=None):
        self.client = client
        self.book = book
        self.window = tk.Toplevel(parent)
        self.window.title("添加图书" if not book else "编辑图书")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        if book:
            self.load_book_data()
    
    def create_widgets(self):
        """创建对话框组件"""
        form_frame = tk.Frame(self.window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 书名
        tk.Label(form_frame, text="书名*:", font=("微软雅黑", 10)).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        self.title_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # 作者
        tk.Label(form_frame, text="作者*:", font=("微软雅黑", 10)).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.author_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.author_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # ISBN
        tk.Label(form_frame, text="ISBN:", font=("微软雅黑", 10)).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.isbn_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.isbn_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # 分类
        tk.Label(form_frame, text="分类:", font=("微软雅黑", 10)).grid(
            row=3, column=0, padx=10, pady=10, sticky="e"
        )
        self.category_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.category_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # 出版社
        tk.Label(form_frame, text="出版社:", font=("微软雅黑", 10)).grid(
            row=4, column=0, padx=10, pady=10, sticky="e"
        )
        self.publisher_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.publisher_entry.grid(row=4, column=1, padx=10, pady=10)
        
        # 出版日期
        tk.Label(form_frame, text="出版日期:", font=("微软雅黑", 10)).grid(
            row=5, column=0, padx=10, pady=10, sticky="e"
        )
        self.publish_date_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.publish_date_entry.grid(row=5, column=1, padx=10, pady=10)
        tk.Label(form_frame, text="(格式: YYYY-MM-DD)", font=("微软雅黑", 8), fg="gray").grid(
            row=6, column=1, padx=10, sticky="w"
        )
        
        # 总数量
        tk.Label(form_frame, text="总数量*:", font=("微软雅黑", 10)).grid(
            row=7, column=0, padx=10, pady=10, sticky="e"
        )
        self.copies_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.copies_entry.grid(row=7, column=1, padx=10, pady=10)
        
        # 按钮
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
            text="取消",
            command=self.window.destroy,
            font=("微软雅黑", 10),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def load_book_data(self):
        """加载图书数据"""
        if self.book:
            self.title_entry.insert(0, self.book.get('title', ''))
            self.author_entry.insert(0, self.book.get('author', ''))
            self.isbn_entry.insert(0, self.book.get('isbn', ''))
            self.category_entry.insert(0, self.book.get('category', ''))
            self.publisher_entry.insert(0, self.book.get('publisher', ''))
            self.publish_date_entry.insert(0, self.book.get('publish_date', ''))
            self.copies_entry.insert(0, str(self.book.get('total_copies', 1)))
    
    def save(self):
        """保存图书"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        category = self.category_entry.get().strip()
        publisher = self.publisher_entry.get().strip()
        publish_date = self.publish_date_entry.get().strip()
        
        try:
            total_copies = int(self.copies_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "总数量必须是数字")
            return
        
        if not title or not author:
            messagebox.showwarning("警告", "书名和作者不能为空")
            return
        
        if self.book:
            # 更新
            success = self.client.update_book(
                self.book['id'],
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                publisher=publisher,
                publish_date=publish_date,
                total_copies=total_copies
            )
        else:
            # 添加
            success = self.client.add_book(
                title, author, isbn, category, publisher, publish_date, total_copies
            )
        
        if success:
            messagebox.showinfo("成功", "保存成功")
            self.window.destroy()
        else:
            messagebox.showerror("错误", "保存失败")

class AddUserDialog:
    """添加用户对话框"""
    
    def __init__(self, parent, client):
        self.client = client
        self.window = tk.Toplevel(parent)
        self.window.title("添加用户")
        self.window.geometry("500x550")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建对话框组件"""
        form_frame = tk.Frame(self.window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 用户名
        tk.Label(form_frame, text="用户名*:", font=("微软雅黑", 10)).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        self.username_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # 密码
        tk.Label(form_frame, text="密码*:", font=("微软雅黑", 10)).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.password_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # 姓名
        tk.Label(form_frame, text="姓名*:", font=("微软雅黑", 10)).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.name_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.name_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # 角色
        tk.Label(form_frame, text="角色*:", font=("微软雅黑", 10)).grid(
            row=3, column=0, padx=10, pady=10, sticky="e"
        )
        self.role_var = tk.StringVar(value="user")
        role_frame = tk.Frame(form_frame)
        role_frame.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        tk.Radiobutton(role_frame, text="管理员", variable=self.role_var,
                      value="admin", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(role_frame, text="会员", variable=self.role_var,
                      value="member", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(role_frame, text="普通用户", variable=self.role_var,
                      value="user", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        
        # 邮箱
        tk.Label(form_frame, text="邮箱:", font=("微软雅黑", 10)).grid(
            row=4, column=0, padx=10, pady=10, sticky="e"
        )
        self.email_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.email_entry.grid(row=4, column=1, padx=10, pady=10)
        
        # 电话
        tk.Label(form_frame, text="电话:", font=("微软雅黑", 10)).grid(
            row=5, column=0, padx=10, pady=10, sticky="e"
        )
        self.phone_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.phone_entry.grid(row=5, column=1, padx=10, pady=10)

        # 年龄
        tk.Label(form_frame, text="年龄:", font=("微软雅黑", 10)).grid(
            row=6, column=0, padx=10, pady=10, sticky="e"
        )
        self.age_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.age_entry.grid(row=6, column=1, padx=10, pady=10)
        
        # 按钮
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
            text="取消",
            command=self.window.destroy,
            font=("微软雅黑", 10),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def save(self):
        """保存用户信息"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        name = self.name_entry.get().strip()
        role = self.role_var.get()
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
        
        if not username:
            messagebox.showwarning("警告", "用户名不能为空")
            return
        
        if not password:
            messagebox.showwarning("警告", "密码不能为空")
            return
        
        if not name:
            messagebox.showwarning("警告", "姓名不能为空")
            return
        
        if not role:
            messagebox.showwarning("警告", "请选择角色")
            return
        
        # 调用客户端方法添加用户
        success, message = self.client.admin_add_user(
            username=username,
            password=password,
            role=role,
            name=name,
            email=email if email else "",
            phone=phone if phone else "",
            age=age_value
        )
        
        if success:
            messagebox.showinfo("成功", message)
            self.window.destroy()
        else:
            messagebox.showerror("添加失败", f"添加用户失败：\n{message}")

class UserDialog:
    """用户编辑对话框"""
    
    def __init__(self, parent, client, user):
        self.client = client
        self.user = user
        self.window = tk.Toplevel(parent)
        self.window.title("编辑用户")
        self.window.geometry("500x520")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_user_data()
    
    def create_widgets(self):
        """创建对话框组件"""
        form_frame = tk.Frame(self.window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 用户名（只读）
        tk.Label(form_frame, text="用户名:", font=("微软雅黑", 10)).grid(
            row=0, column=0, padx=10, pady=10, sticky="e"
        )
        username_label = tk.Label(form_frame, text=self.user['username'], 
                                 font=("微软雅黑", 10), fg="gray")
        username_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # 姓名
        tk.Label(form_frame, text="姓名*:", font=("微软雅黑", 10)).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.name_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # 角色
        tk.Label(form_frame, text="角色*:", font=("微软雅黑", 10)).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.role_var = tk.StringVar()
        role_frame = tk.Frame(form_frame)
        role_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        tk.Radiobutton(role_frame, text="管理员", variable=self.role_var,
                      value="admin", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(role_frame, text="会员", variable=self.role_var,
                      value="member", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(role_frame, text="普通用户", variable=self.role_var,
                      value="user", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        
        # 邮箱
        tk.Label(form_frame, text="邮箱:", font=("微软雅黑", 10)).grid(
            row=3, column=0, padx=10, pady=10, sticky="e"
        )
        self.email_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.email_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # 电话
        tk.Label(form_frame, text="电话:", font=("微软雅黑", 10)).grid(
            row=4, column=0, padx=10, pady=10, sticky="e"
        )
        self.phone_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.phone_entry.grid(row=4, column=1, padx=10, pady=10)

        # 年龄
        tk.Label(form_frame, text="年龄:", font=("微软雅黑", 10)).grid(
            row=5, column=0, padx=10, pady=10, sticky="e"
        )
        self.age_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30)
        self.age_entry.grid(row=5, column=1, padx=10, pady=10)
        
        # 密码（可选）
        tk.Label(form_frame, text="新密码:", font=("微软雅黑", 10)).grid(
            row=6, column=0, padx=10, pady=10, sticky="e"
        )
        self.password_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=30, show="*")
        self.password_entry.grid(row=6, column=1, padx=10, pady=10)
        tk.Label(form_frame, text="(留空则不修改密码)", font=("微软雅黑", 8), fg="gray").grid(
            row=7, column=1, padx=10, sticky="w"
        )
        
        # 按钮
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
            text="取消",
            command=self.window.destroy,
            font=("微软雅黑", 10),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def load_user_data(self):
        """加载用户数据"""
        if self.user:
            self.name_entry.insert(0, self.user.get('name', ''))
            self.role_var.set(self.user.get('role', 'user'))
            self.email_entry.insert(0, self.user.get('email', ''))
            self.phone_entry.insert(0, self.user.get('phone', ''))
            age_value = self.user.get('age')
            if age_value is not None:
                self.age_entry.insert(0, str(age_value))
    
    def save(self):
        """保存用户信息"""
        name = self.name_entry.get().strip()
        role = self.role_var.get()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        age_text = self.age_entry.get().strip()
        password = self.password_entry.get().strip()
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
        
        if not role:
            messagebox.showwarning("警告", "请选择角色")
            return
        
        # 准备更新数据
        update_data = {
            'name': name,
            'email': email if email else None,
            'phone': phone if phone else None,
            'role': role,
            'age': age_value if age_text else None
        }
        
        # 如果输入了新密码，则更新密码
        if password:
            update_data['password'] = password
        
        # 调用客户端方法更新用户
        success = self.client.admin_update_user(
            self.user['id'],
            name=update_data['name'],
            email=update_data['email'],
            phone=update_data['phone'],
            role=update_data['role'],
            password=update_data.get('password'),
            age=update_data['age']
        )
        
        if success:
            messagebox.showinfo("成功", "用户信息更新成功")
            self.window.destroy()
        else:
            messagebox.showerror("错误", "更新失败")

class ImportBooksDialog:
    """爬取图书对话框"""
    
    def __init__(self, parent, client):
        self.client = client
        self.success = False
        self.window = tk.Toplevel(parent)
        self.window.title("从Open Library爬取图书")
        self.window.geometry("800x600")  # 加宽扩大界面
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self.importing = False
        self.create_widgets()
    
    def create_widgets(self):
        """创建对话框组件"""
        form_frame = tk.Frame(self.window)
        form_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=20)  # 改为 expand=False
        
        # 说明文字
        info_label = tk.Label(
            form_frame,
            text="从Open Library爬取图书数据",
            font=("微软雅黑", 12, "bold"),
            fg="#2196F3"
        )
        info_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 查询关键词
        tk.Label(form_frame, text="查询关键词*:", font=("微软雅黑", 10)).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.query_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=45)
        self.query_entry.insert(0, "subject:fiction")
        self.query_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        tk.Label(
            form_frame,
            text="示例: subject:fiction, author:Shakespeare, title:python",
            font=("微软雅黑", 8),
            fg="gray"
        ).grid(row=2, column=1, padx=10, sticky="w")
        
        # 爬取数量
        tk.Label(form_frame, text="爬取数量*:", font=("微软雅黑", 10)).grid(
            row=3, column=0, padx=10, pady=10, sticky="e"
        )
        self.count_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=45)
        self.count_entry.insert(0, "100")
        self.count_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        tk.Label(
            form_frame,
            text="建议范围: 1-1000 (数量越大耗时越长)",
            font=("微软雅黑", 8),
            fg="gray"
        ).grid(row=4, column=1, padx=10, sticky="w")
        
        # 每本书的副本数
        tk.Label(form_frame, text="每本书副本数:", font=("微软雅黑", 10)).grid(
            row=5, column=0, padx=10, pady=10, sticky="e"
        )
        self.copies_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=45)
        self.copies_entry.insert(0, "3")
        self.copies_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")
        
        # 批次大小
        tk.Label(form_frame, text="批次大小:", font=("微软雅黑", 10)).grid(
            row=6, column=0, padx=10, pady=10, sticky="e"
        )
        self.batch_size_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=45)
        self.batch_size_entry.insert(0, "100")
        self.batch_size_entry.grid(row=6, column=1, padx=10, pady=10, sticky="w")
        tk.Label(
            form_frame,
            text="每次请求获取的记录数 (1-100)，默认100",
            font=("微软雅黑", 8),
            fg="gray"
        ).grid(row=7, column=1, padx=10, sticky="w")
        
        # 请求延迟
        tk.Label(form_frame, text="请求延迟(秒):", font=("微软雅黑", 10)).grid(
            row=8, column=0, padx=10, pady=10, sticky="e"
        )
        self.delay_entry = tk.Entry(form_frame, font=("微软雅黑", 10), width=45)
        self.delay_entry.insert(0, "0.5")
        self.delay_entry.grid(row=8, column=1, padx=10, pady=10, sticky="w")
        tk.Label(
            form_frame,
            text="每页请求之间的延时，建议0.5-1.0秒",
            font=("微软雅黑", 8),
            fg="gray"
        ).grid(row=9, column=1, padx=10, sticky="w")
        
        # 进度显示
        progress_frame = tk.Frame(form_frame)
        progress_frame.grid(row=10, column=0, columnspan=2, pady=20, sticky="ew")
        
        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("微软雅黑", 9),
            fg="#4CAF50"
        )
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=550
        )
        self.progress_bar.pack(pady=5)
        
        # 按钮 - 放在 form_frame 内部
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=11, column=0, columnspan=2, pady=20)
        
        self.start_btn = tk.Button(
            btn_frame,
            text="开始爬取",
            command=self.start_import,
            font=("微软雅黑", 10),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = tk.Button(
            btn_frame,
            text="取消",
            command=self.cancel,
            font=("微软雅黑", 10),
            bg="#9E9E9E",
            fg="white",
            padx=20,
            pady=5
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def start_import(self):
        """开始导入"""
        if self.importing:
            return
        
        # 获取参数
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("警告", "请输入查询关键词")
            return
        
        try:
            count = int(self.count_entry.get().strip())
            if count < 1 or count > 10000:
                messagebox.showwarning("警告", "爬取数量应在1-10000之间")
                return
        except ValueError:
            messagebox.showerror("错误", "爬取数量必须是数字")
            return
        
        try:
            copies = int(self.copies_entry.get().strip())
            if copies < 1 or copies > 100:
                messagebox.showwarning("警告", "副本数应在1-100之间")
                return
        except ValueError:
            messagebox.showerror("错误", "副本数必须是数字")
            return
        
        try:
            batch_size = int(self.batch_size_entry.get().strip())
            if batch_size < 1 or batch_size > 100:
                messagebox.showwarning("警告", "批次大小应在1-100之间")
                return
        except ValueError:
            messagebox.showerror("错误", "批次大小必须是数字")
            return
        
        try:
            delay = float(self.delay_entry.get().strip())
            if delay < 0.1 or delay > 5.0:
                messagebox.showwarning("警告", "请求延迟应在0.1-5.0秒之间")
                return
        except ValueError:
            messagebox.showerror("错误", "请求延迟必须是数字")
            return
        
        # 确认
        if not messagebox.askyesno(
            "确认",
            f"将爬取约 {count} 本图书，这可能需要一些时间。\n是否继续？"
        ):
            return
        
        # 开始导入（在后台线程中执行）
        self.importing = True
        self.start_btn.config(state=tk.DISABLED, text="爬取中...")
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="正在爬取图书，请稍候...")
        self.progress_bar.start()
        
        # 在后台线程中执行导入
        thread = threading.Thread(target=self._do_import, args=(
            query, count, batch_size, delay, copies
        ))
        thread.daemon = True
        thread.start()
    
    def _do_import(self, query, count, batch_size, delay, copies):
        """在后台线程中执行导入"""
        try:
            success, message, data = self.client.import_books_from_openlibrary(
                query=query,
                count=count,
                batch_size=batch_size,
                delay=delay,
                copies=copies
            )
            
            # 在主线程中更新UI
            self.window.after(0, self._import_finished, success, message, data)
        except Exception as e:
            self.window.after(0, self._import_finished, False, f"导入失败: {str(e)}", {})
    
    def _import_finished(self, success, message, data):
        """导入完成后的回调"""
        self.importing = False
        self.progress_bar.stop()
        self.start_btn.config(state=tk.NORMAL, text="开始爬取")
        self.cancel_btn.config(state=tk.NORMAL)
        
        if success:
            stored = data.get('stored', 0)
            skipped = data.get('skipped', 0)
            self.progress_label.config(
                text=f"爬取完成！成功: {stored} 本，跳过: {skipped} 本",
                fg="#4CAF50"
            )
            messagebox.showinfo("成功", message)
            self.success = True
        else:
            self.progress_label.config(text="爬取失败", fg="#f44336")
            messagebox.showerror("错误", message)
    
    def cancel(self):
        """取消"""
        if self.importing:
            if not messagebox.askyesno("确认", "爬取正在进行中，确定要取消吗？"):
                return
        self.window.destroy()

