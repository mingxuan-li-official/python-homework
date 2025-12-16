"""
数据库模块 - 使用MySQL数据库
负责数据库的初始化、连接和基本操作
参考废案/app/database.py的实现模式
"""
from contextlib import contextmanager
from typing import Any, Generator, List, Dict, Tuple, Optional, Sequence
import hashlib

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from pymysql.err import OperationalError, Error

from config import DB_CONFIG


# 全局连接对象
_CONNECTION: Optional[Connection] = None


def _get_connection() -> Connection:
    """获取全局 MySQL 连接，必要时自动创建数据库。"""
    global _CONNECTION
    if _CONNECTION is None or not _CONNECTION.open:
        _CONNECTION = _create_connection()
    return _CONNECTION


def _create_connection() -> Connection:
    """创建MySQL连接，如果数据库不存在则自动创建"""
    try:
        return pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            autocommit=False,
            cursorclass=DictCursor,
        )
    except OperationalError as exc:
        # 1049: Unknown database
        if exc.args and exc.args[0] == 1049:
            _ensure_database_exists()
            return pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset=DB_CONFIG['charset'],
                autocommit=False,
                cursorclass=DictCursor,
            )
        raise


def _ensure_database_exists() -> None:
    """确保数据库存在，如果不存在则创建"""
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset=DB_CONFIG['charset'],
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` "
                f"DEFAULT CHARACTER SET {DB_CONFIG['charset']} "
                f"COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


@contextmanager
def _get_cursor(commit: bool = True) -> Generator[DictCursor, None, None]:
    """上下文管理 MySQL cursor，对异常自动回滚。"""
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


class Database:
    """数据库管理类 - 提供与现有代码兼容的接口"""
    
    def __init__(self):
        """初始化数据库连接和表结构"""
        # 确保数据库存在
        try:
            _get_connection()
        except Exception:
            pass
        self.init_database()
    
    def get_connection(self) -> Connection:
        """获取数据库连接（兼容旧接口）"""
        return _get_connection()
    
    def init_database(self):
        """初始化数据库表结构"""
        with _get_cursor() as cursor:
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    age INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CHECK (role IN ('admin', 'member', 'user'))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # 如果表已存在，确保 age 字段存在
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN age INT")
            except Exception:
                # 字段已存在时忽略错误
                pass
            
            # 创建图书表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    author VARCHAR(100) NOT NULL,
                    isbn VARCHAR(20) UNIQUE,
                    category VARCHAR(50),
                    publisher VARCHAR(100),
                    publish_date DATE,
                    total_copies INT DEFAULT 1,
                    available_copies INT DEFAULT 1,
                    status VARCHAR(20) DEFAULT 'available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CHECK (status IN ('available', 'unavailable', 'borrowed', 'maintenance'))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 如果表已存在，确保status字段足够长以支持'unavailable'
            # 修改字段长度为VARCHAR(50)以确保足够存储所有状态值
            try:
                cursor.execute("ALTER TABLE books MODIFY COLUMN status VARCHAR(50) DEFAULT 'available'")
            except Exception as e:
                # 如果字段修改失败（可能字段已经是足够长度或表不存在），忽略错误
                pass
            
            # 创建借阅记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS borrow_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    book_id INT NOT NULL,
                    borrow_date DATE NOT NULL,
                    return_date DATE,
                    due_date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'borrowed',
                    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                    CHECK (status IN ('borrowed', 'returned', 'overdue'))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
        
        # 初始化默认管理员账户
        self.init_default_admin()
    
    def init_default_admin(self):
        """初始化默认管理员账户"""
        with _get_cursor() as cursor:
            # 检查是否已有管理员
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
            result = cursor.fetchone()
            if result['count'] == 0:
                # 默认管理员：admin/admin123
                password_hash = hashlib.md5("admin123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, password, role, name, email, age)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, ("admin", password_hash, "admin", "系统管理员", "admin@library.com", None))
    
    def _convert_placeholders(self, query: str) -> str:
        """将SQLite的?占位符转换为MySQL的%s占位符"""
        return query.replace('?', '%s')
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """执行查询并返回结果列表"""
        query = self._convert_placeholders(query)
        
        conn = _get_connection()
        # 提交当前事务，确保能看到其他进程已提交的更改
        conn.commit()
        
        try:
            with _get_cursor(commit=False) as cursor:
                cursor.execute(query, params or ())
                rows = cursor.fetchall()
                return list(rows) if rows else []
        except Error as e:
            print(f"查询执行失败: {e}")
            print(f"SQL: {query}")
            print(f"参数: {params}")
            return []
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """执行更新操作并返回影响的行数"""
        query = self._convert_placeholders(query)
        
        try:
            with _get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.rowcount
        except Error as e:
            print(f"更新执行失败: {e}")
            print(f"SQL: {query}")
            print(f"参数: {params}")
            return 0
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """执行插入操作并返回插入的ID"""
        query = self._convert_placeholders(query)
        
        try:
            with _get_cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except Error as e:
            print(f"插入执行失败: {e}")
            print(f"SQL: {query}")
            print(f"参数: {params}")
            return 0

