"""
主界面 - 根据用户角色显示不同的界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from gui_admin import AdminWindow
from gui_user import UserWindow
from gui_guest import GuestWindow

class MainWindow:
    """主窗口"""
    
    def __init__(self, client, user):
        self.client = client
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"图书管理系统 - {user['name']}")
        self.root.geometry("1000x700")
        
        # 根据角色创建不同的界面
        if user['role'] == 'admin':
            AdminWindow(self.root, self.client, self.user)
        elif user['role'] == 'guest':
            GuestWindow(self.root, self.client)
        else:
            UserWindow(self.root, self.client, self.user)
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()
        # 关闭连接
        if self.client:
            self.client.disconnect()

