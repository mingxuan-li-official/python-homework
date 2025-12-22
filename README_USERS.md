# 用户角色与功能说明（图书管理系统）

下表说明了系统中各类用户的角色定位与可用功能，便于开发、测试与使用时快速对照。

| 角色 | 说明 | 可用主要功能（示例） | 常用界面/权限点 |
|---|---:|---|---|
| 管理员（admin） | 系统最高权限用户，负责系统管理与维护 | - 添加/编辑/删除图书（`add_book`/`update_book`/`delete_book`）  - 查看/管理所有借阅记录（`get_all_borrows`/`update_borrow`）  - 管理用户（`get_all_users`/`admin_add_user`/`admin_update_user`/`admin_delete_user`）  - 查看统计信息（`get_statistics`/仪表盘数据）  - 发送系统邮件和查看邮件记录（`send_email`/`get_all_emails`） | `gui_admin.py`；需要放行服务器端口，使用管理员账户登录（默认：`admin`/`admin123`） |
| 教师（teacher） | 具有比普通学生更高的权限（可作扩展） | - 浏览/搜索图书 - 借阅图书 - 查看个人借阅记录 - 维护个人信息 | 通常使用普通用户界面(`gui_user.py`)；项目中可根据需要扩展教师专属功能 |
| 学生/普通用户（student / user） | 系统常规使用者，借阅图书的主体 | - 注册/登录（`register`/`login`） - 搜索与浏览图书（`search_books`/`get_book`） - 借阅/归还图书（`borrow_book`/`return_book`） - 查看我的借阅记录（`get_my_borrows`） - 个人信息维护与改密（`get_user_info`/`update_user_info`/`change_password`） - 查看个人邮件（`get_user_emails`） | `gui_user.py`；通过客户端（`main.py`/`gui_login.py`）连接服务器，使用用户凭证登录 |
| 访客（guest） | 未登录或未注册的用户，受限访问 | - 浏览/搜索图书（只读） - 查看图书详情 - 可注册新账号 | `gui_guest.py`；用于未登录状态下快速浏览图书目录 |

附：各类功能对应的网络请求接口（客户端方法示例）——实现细节见 `network_client.py`：

- 登录/注册：`login`, `register`  
- 图书浏览/管理：`search_books`, `get_book`, `add_book`, `update_book`, `delete_book`  
- 借阅流程：`borrow_book`, `return_book`, `get_my_borrows`, `get_all_borrows`, `admin_update_borrow`  
- 用户管理：`get_user_info`, `update_user_info`, `change_password`, `get_all_users`, `admin_add_user`, `admin_update_user`, `admin_delete_user`  
- 统计与仪表盘：`get_statistics`, `get_admin_dashboard_data`, `get_user_dashboard_data`  
- 邮件系统：`send_email`, `get_all_emails`, `get_user_emails`

使用说明（简要）
- 局域网测试：启动 `server.py`（默认为 `0.0.0.0:8888`），在同一局域网的客户端把 `network_client.NetworkClient(host=服务器IP)` 的 `host` 修改为服务器 IP，启动客户端登录测试。  
- 本机测试：服务端和客户端在同一台机器，客户端可使用 `127.0.0.1` 或 `localhost` 连接。  
- 跨网访问：需在路由器做端口映射（外网IP + 端口转发到服务器内网IP:8888），并确保防火墙放行端口。

建议
- 若计划线上部署，请替换默认 MD5 存储方式为更安全的散列（如 bcrypt/argon2），并使用 HTTPS / 更安全的通信方式替代明文 Socket 或在应用层加密。  
- 根据实际应用需要在 `gui_admin.py`/`gui_user.py` 中对教师角色进行细化权限分配。


