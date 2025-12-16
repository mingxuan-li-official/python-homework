# 图书管理系统

## 项目简介

这是一个基于Python开发的图书管理系统，采用客户端-服务器架构，支持远程访问。系统实现了用户管理、图书管理、借阅管理等核心功能，并提供了友好的GUI界面。

## 功能特性

### 基本功能（已实现）

1. **用户界面**
   - 基于tkinter的图形用户界面
   - 登录/注册窗口
   - 管理员界面和普通用户界面

2. **数据库支持**
   - 使用SQLite数据库
   - 规范的数据库设计（用户表、图书表、借阅记录表）
   - 支持数据的增删改查操作

3. **远程登录访问（网络模块）**
   - 基于Socket的客户端-服务器架构
   - 支持多客户端同时连接
   - JSON格式的数据传输

4. **用户登录与注销**
   - 用户登录验证
   - 用户注册功能
   - 安全退出登录

5. **不同身份用户的操作区分**
   - **管理员**：
     - 图书管理（添加、编辑、删除、搜索）
     - 借阅记录管理
     - 数据统计（总图书数、借阅数、逾期数等）
   - **普通用户（会员/普通用户）**：
     - 图书浏览和搜索
     - 图书借阅
     - 我的借阅记录查看和归还
     - 个人信息维护
     - 密码修改

## 项目结构

```
大作业/
├── main.py              # 主程序入口
├── server.py            # 服务端程序
├── database.py          # 数据库模块
├── models.py            # 数据模型（业务逻辑）
├── network_client.py    # 网络客户端模块
├── gui_login.py         # 登录界面
├── gui_main.py          # 主界面
├── gui_admin.py         # 管理员界面
├── gui_user.py          # 普通用户界面
├── library.db           # SQLite数据库文件（运行后自动生成）
├── requirements.txt     # 依赖包列表
└── README.md           # 项目说明文档
```

## 环境要求

- Python 3.7+
- MySQL 5.7+ 或 MySQL 8.0+
- tkinter（Python标准库，通常已包含）
- mysql-connector-python（MySQL数据库连接器）

## 安装与运行

### 1. 安装MySQL数据库

请确保已安装并启动MySQL数据库服务器。如果尚未安装，请访问 [MySQL官网](https://dev.mysql.com/downloads/mysql/) 下载安装。

### 2. 配置数据库连接

编辑 `config.py` 文件，配置MySQL数据库连接信息：

```python
DB_CONFIG = {
    'host': 'localhost',      # MySQL服务器地址
    'port': 3306,             # MySQL端口
    'user': 'root',          # MySQL用户名
    'password': 'your_password',  # MySQL密码（请修改为实际密码）
    'database': 'library',    # 数据库名称
    'charset': 'utf8mb4'      # 字符集
}
```

### 3. 安装依赖

安装Python依赖包：

```bash
# 安装依赖
pip install -r requirements.txt
```

如果使用虚拟环境：

```bash
# 创建虚拟环境（可选）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 启动服务端

首先需要启动服务器：

```bash
python server.py
```

服务端默认监听 `0.0.0.0:8888`，可以在 `server.py` 中修改。

**注意**：首次运行时会自动创建数据库和表结构，并初始化默认管理员账户。

### 5. 启动客户端

在另一个终端（或另一台机器）启动客户端：

```bash
python main.py
```

或者直接运行：

```bash
python gui_login.py
```

## 使用说明

### 默认账户

系统初始化时会自动创建默认管理员账户：
- 用户名：`admin`
- 密码：`admin123`

### 操作流程

1. **启动服务端**
   - 运行 `server.py`
   - 等待客户端连接

2. **启动客户端并连接**
   - 运行 `main.py` 或 `gui_login.py`
   - 点击"连接到服务器"按钮
   - 输入用户名和密码登录

3. **管理员操作**
   - 登录后进入管理员界面
   - 可以管理图书（添加、编辑、删除）
   - 可以查看所有借阅记录
   - 可以查看统计信息

4. **普通用户操作**
   - 注册新账户或使用已有账户登录
   - 浏览和搜索图书
   - 借阅图书
   - 查看和管理自己的借阅记录
   - 维护个人信息

## 数据库设计

### 用户表 (users)
- id: 主键
- username: 用户名（唯一）
- password: 密码（MD5加密）
- role: 角色（admin/teacher/student）
- name: 姓名
- email: 邮箱
- phone: 电话
- created_at: 创建时间

### 图书表 (books)
- id: 主键
- title: 书名
- author: 作者
- isbn: ISBN号（唯一）
- category: 分类
- publisher: 出版社
- publish_date: 出版日期
- total_copies: 总数量
- available_copies: 可借数量
- status: 状态（available/borrowed/maintenance）
- created_at: 创建时间

### 借阅记录表 (borrow_records)
- id: 主键
- user_id: 用户ID（外键）
- book_id: 图书ID（外键）
- borrow_date: 借阅日期
- return_date: 归还日期
- due_date: 应还日期
- status: 状态（borrowed/returned/overdue）
- fine_amount: 罚款金额

## 网络通信协议

客户端和服务器使用JSON格式进行通信：

**请求格式：**
```json
{
    "action": "操作名称",
    "data": {
        "参数1": "值1",
        "参数2": "值2"
    }
}
```

**响应格式：**
```json
{
    "success": true/false,
    "message": "消息",
    "data": {}
}
```

## 测试建议

1. **本地测试**：在同一台机器上运行服务端和客户端
2. **远程测试**：在不同机器上运行服务端和客户端
   - 修改 `network_client.py` 中的 `host` 参数为服务器IP地址
   - 确保防火墙允许8888端口通信

## 注意事项

1. 首次运行会自动创建数据库文件 `library.db`
2. 服务端需要先启动，客户端才能连接
3. 密码使用MD5加密存储（生产环境建议使用更安全的加密方式）
4. 数据库文件在同一目录下，注意备份

## 扩展功能建议

如需实现附加功能，可以考虑：

1. **数据可视化**：使用matplotlib绘制统计图表
2. **数据分析**：分析借阅趋势、热门图书等
3. **数据库并发控制**：使用数据库锁机制
4. **程序打包**：使用PyInstaller打包为可执行文件
5. **版本控制**：使用Git进行版本管理

## 开发者

本项目为Python程序设计课程作业。

## 许可证

本项目仅供学习使用。

