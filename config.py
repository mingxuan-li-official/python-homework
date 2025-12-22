"""
数据库配置文件
配置MySQL数据库连接信息
"""
# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',      # MySQL服务器地址
    'port': 3306,             # MySQL端口
    'user': 'root',          # MySQL用户名
    'password': 'root',           # MySQL密码（请根据实际情况修改）
    'database': 'library_system',    # 数据库名称
    'charset': 'utf8mb4'      # 字符集
}

# 可选：SMTP 配置（如果需要让服务器直接发送邮件）
# 若不配置或留空，则仅在数据库中保存邮件记录，不会尝试通过 SMTP 发送。
SMTP_CONFIG = {
    'host': '',        # SMTP 服务器地址，例如 'smtp.example.com'
    'port': 587,       # SMTP 端口，通常 587 或 465
    'user': '',        # SMTP 登录用户名
    'password': '',    # SMTP 登录密码
    'use_tls': True,   # 是否使用 STARTTLS
}

