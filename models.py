"""
数据模型模块
定义业务逻辑相关的数据操作
"""
from database import Database
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, timedelta
import hashlib
import re
import smtplib
from email.mime.text import MIMEText
from config import DB_CONFIG
try:
    from config import SMTP_CONFIG
except Exception:
    SMTP_CONFIG = {}

_UNSET = object()


def _normalize_age(age: Any) -> Optional[int]:
    """将年龄标准化为整数或None"""
    if age is None or age is _UNSET:
        return None
    if isinstance(age, str):
        age = age.strip()
        if not age:
            return None
    try:
        age_int = int(age)
    except (TypeError, ValueError):
        raise ValueError("年龄必须是整数")
    if age_int < 0 or age_int > 150:
        raise ValueError("年龄必须在0到150之间")
    return age_int

class UserModel:
    """用户模型"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """密码加密"""
        return hashlib.md5(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """用户登录验证"""
        password_hash = self.hash_password(password)
        users = self.db.execute_query(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password_hash)
        )
        if users:
            user = users[0]
            # 移除密码字段
            user.pop('password', None)
            return user
        return None
    
    def register(self, username: str, password: str, role: str, name: str,
                 email: str = "", phone: str = "", age: Optional[int] = None) -> bool:
        """用户注册"""
        try:
            password_hash = self.hash_password(password)
            age_value = _normalize_age(age)
            self.db.execute_insert(
                """INSERT INTO users (username, password, role, name, email, phone, age)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (username, password_hash, role, name, email, phone, age_value)
            )
            return True
        except ValueError as e:
            print(f"注册失败: {e}")
            return False
        except Exception as e:
            print(f"注册失败: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        users = self.db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
        if users:
            user = users[0]
            user.pop('password', None)
            return user
        return None
    
    def update_user(self, user_id: int, name: str = None, email: str = None,
                   phone: str = None, age: Any = _UNSET) -> bool:
        """更新用户信息"""
        updates = []
        params = []
        if name:
            updates.append("name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if phone:
            updates.append("phone = ?")
            params.append(phone)
        if age is not _UNSET:
            try:
                age_value = _normalize_age(age)
            except ValueError as e:
                print(f"更新用户失败: {e}")
                return False
            updates.append("age = ?")
            params.append(age_value)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = self.db.execute_query("SELECT password FROM users WHERE id = ?", (user_id,))
        if not user:
            return False
        
        if user[0]['password'] != self.hash_password(old_password):
            return False
        
        new_hash = self.hash_password(new_password)
        return self.db.execute_update(
            "UPDATE users SET password = ? WHERE id = ?",
            (new_hash, user_id)
        ) > 0
    
    def get_all_users(self) -> List[Dict]:
        """获取所有用户（管理员）"""
        users = self.db.execute_query("SELECT * FROM users ORDER BY id DESC")
        # 移除所有用户的密码字段
        for user in users:
            user.pop('password', None)
        return users
    
    def get_role_counts(self) -> List[Dict]:
        """获取用户角色数量"""
        rows = self.db.execute_query(
            """
            SELECT role, COUNT(*) AS count
            FROM users
            GROUP BY role
            """
        )
        return rows or []
    
    def get_age_distribution(self) -> Dict[str, int]:
        """获取年龄段统计"""
        rows = self.db.execute_query("SELECT age FROM users WHERE age IS NOT NULL")
        buckets = {
            '0-17': 0,
            '18-25': 0,
            '26-35': 0,
            '36-45': 0,
            '46-60': 0,
            '60+': 0
        }
        for row in rows:
            age = row.get('age')
            if age is None:
                continue
            if age <= 17:
                buckets['0-17'] += 1
            elif age <= 25:
                buckets['18-25'] += 1
            elif age <= 35:
                buckets['26-35'] += 1
            elif age <= 45:
                buckets['36-45'] += 1
            elif age <= 60:
                buckets['46-60'] += 1
            else:
                buckets['60+'] += 1
        return buckets
    
    def get_registration_trend(self, months: int = 12) -> List[Dict]:
        """按月统计注册人数"""
        months = max(1, months)
        start_date = (datetime.now().date() - timedelta(days=30 * months)).isoformat()
        rows = self.db.execute_query(
            """
            SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(*) AS count
            FROM users
            WHERE created_at >= ?
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            ORDER BY month
            """,
            (start_date,)
        )
        row_map = {row['month']: row['count'] for row in rows if row.get('month')}
        trend = []
        # 以当前月份为终点，向前回溯
        current = datetime.now().date().replace(day=1)
        for i in range(months - 1, -1, -1):
            month_date = current - timedelta(days=30 * i)
            label = month_date.strftime('%Y-%m')
            trend.append({'month': label, 'count': row_map.get(label, 0)})
        return trend
    
    def admin_update_user(self, user_id: int, name: str = None, email: str = None,
                         phone: str = None, role: str = None, password: str = None,
                         age: Any = _UNSET) -> bool:
        """管理员更新用户信息（可修改所有字段包括角色和密码）"""
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        if password is not None:
            updates.append("password = ?")
            params.append(self.hash_password(password))
        if age is not _UNSET:
            try:
                age_value = _normalize_age(age)
            except ValueError as e:
                print(f"管理员更新用户失败: {e}")
                return False
            updates.append("age = ?")
            params.append(age_value)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        return self.db.execute_update(query, tuple(params)) > 0
    
    def admin_add_user(self, username: str, password: str, role: str, name: str,
                      email: str = "", phone: str = "", age: Optional[int] = None) -> Tuple[bool, str]:
        """管理员添加用户
        返回: (成功标志, 错误信息)
        """
        try:
            # 检查用户名是否已存在（去除首尾空格）
            username = username.strip()
            if not username:
                return False, "用户名不能为空"
            
            # 验证必填字段
            if not password:
                return False, "密码不能为空"
            if not name:
                return False, "姓名不能为空"
            if not role:
                return False, "角色不能为空"
            
            # 验证角色值
            if role not in ['admin', 'member', 'user']:
                return False, f"无效的角色值: {role}，必须是 admin、member 或 user"
            
            # 检查用户名是否已存在
            existing = self.db.execute_query(
                "SELECT id FROM users WHERE username = ?", (username,)
            )
            if existing:
                return False, f"用户名 '{username}' 已存在"
            
            password_hash = self.hash_password(password)
            try:
                age_value = _normalize_age(age)
            except ValueError as e:
                return False, str(e)
            # 检查插入是否成功（返回值应该大于0）
            user_id = self.db.execute_insert(
                """INSERT INTO users (username, password, role, name, email, phone, age)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (username, password_hash, role, name, email, phone, age_value)
            )
            # 如果插入失败，execute_insert 会返回 0
            if user_id == 0:
                return False, "数据库插入失败，可能是数据库连接问题或约束冲突"
            return True, "添加成功"
        except Exception as e:
            error_msg = f"添加用户失败: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def admin_delete_user(self, user_id: int) -> bool:
        """管理员删除用户"""
        try:
            # 检查用户是否存在
            user = self.db.execute_query("SELECT id FROM users WHERE id = ?", (user_id,))
            if not user:
                return False
            
            # 检查是否有未归还的借阅记录
            borrows = self.db.execute_query(
                """SELECT COUNT(*) as count FROM borrow_records 
                   WHERE user_id = ? AND status = 'borrowed'""",
                (user_id,)
            )
            if borrows and borrows[0]['count'] > 0:
                return False  # 有未归还的图书，不能删除
            
            # 删除用户
            return self.db.execute_update("DELETE FROM users WHERE id = ?", (user_id,)) > 0
        except Exception as e:
            print(f"删除用户失败: {e}")
            return False

class BookModel:
    """图书模型"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def _map_to_standard_category(self, category: str) -> str:
        """将分类名称映射到标准分类"""
        if not category:
            return '未分类'
        
        # 去除首尾空格
        category_clean = category.strip()
        if not category_clean:
            return '未分类'
        
        # 转为小写用于匹配（大小写不敏感）
        category_lower = category_clean.lower()
        
        # 定义标准分类关键词映射（按优先级排序，更具体的在前）
        # 注意：匹配顺序很重要，先匹配更具体的短语，再匹配单词
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
                # 先匹配复合短语
                'classic literature', 'juvenile fiction', 'young adult', 
                # 再匹配单词
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
        
        # 首先检查是否已经是标准分类名称
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
        
        # 按优先级检查英文关键词（更具体的匹配优先）
        # 先按长度排序关键词（长的在前），确保先匹配复合短语
        for std_cat, keywords in category_mapping.items():
            # 按长度降序排序，先匹配更长的短语
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            for keyword in sorted_keywords:
                keyword_lower = keyword.lower()
                # 完整单词/短语匹配（避免部分匹配）
                # 对于多词短语，直接检查是否在字符串中
                if ' ' in keyword:
                    # 多词短语：检查是否包含整个短语
                    if keyword_lower in category_lower:
                        return std_cat
                else:
                    # 单词：使用单词边界匹配
                    pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                    if re.search(pattern, category_lower):
                        return std_cat
        
        return '其他类'
    
    def get_category_summary(self) -> List[Dict]:
        """获取各分类图书数量与库存（使用标准分类）"""
        rows = self.db.execute_query(
            "SELECT category, total_copies, available_copies FROM books"
        )
        if not rows:
            return []
        
        summary: Dict[str, Dict[str, int]] = {}
        for row in rows:
            category_str = (row.get('category') or '').strip()
            total = row.get('total_copies') or 0
            available = row.get('available_copies') or 0
            
            # 将整个分类字符串映射到标准分类（处理多个分类的情况）
            # 如果分类字符串包含多个分类，取第一个匹配的标准分类
            std_category = self._map_to_standard_category(category_str)
            
            # 如果分类字符串包含逗号分隔的多个分类，尝试找到最匹配的标准分类
            if ',' in category_str:
                categories = [part.strip() for part in category_str.split(',') if part.strip()]
                # 尝试为每个分类找到标准分类，取第一个非"其他类"的
                for cat in categories:
                    mapped = self._map_to_standard_category(cat)
                    if mapped != '其他类':
                        std_category = mapped
                        break
            
            # 统计到对应的标准分类（每个图书只统计一次）
            stats = summary.setdefault(
                std_category,
                {'category': std_category, 'book_count': 0, 'total_copies': 0, 'available_copies': 0}
            )
            stats['book_count'] += 1
            stats['total_copies'] += total
            stats['available_copies'] += available
        
        # 定义标准分类的显示顺序
        category_order = ['教育类', '科普类', '文学类', '历史类', '艺术类', '其他类', '未分类']
        
        # 按预定义顺序和数量排序
        sorted_summary = sorted(
            summary.values(), 
            key=lambda item: (
                category_order.index(item['category']) if item['category'] in category_order else 999,
                -item['book_count']  # 数量降序
            )
        )
        
        # 返回所有分类
        return sorted_summary
    
    def get_status_summary(self) -> List[Dict]:
        """获取各状态图书数量"""
        rows = self.db.execute_query(
            """
            SELECT status, COUNT(*) AS count
            FROM books
            GROUP BY status
            """
        )
        return rows or []
    
    def add_book(self, title: str, author: str, isbn: str = "", category: str = "",
                 publisher: str = "", publish_date: str = "", total_copies: int = 1) -> bool:
        """添加图书"""
        try:
            # 根据可借数量设置状态
            status = 'unavailable' if total_copies <= 0 else 'available'
            self.db.execute_insert(
                """INSERT INTO books (title, author, isbn, category, publisher, 
                   publish_date, total_copies, available_copies, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, author, isbn, category, publisher, publish_date, 
                 total_copies, total_copies, status)
            )
            return True
        except Exception as e:
            print(f"添加图书失败: {e}")
            return False
    
    def get_book(self, book_id: int) -> Optional[Dict]:
        """获取图书信息"""
        books = self.db.execute_query("SELECT * FROM books WHERE id = ?", (book_id,))
        return books[0] if books else None
    
    def search_books(self, keyword: str = "", category: str = "") -> List[Dict]:
        """搜索图书"""
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        
        # 确保 keyword 和 category 是字符串，并去除首尾空格
        keyword = str(keyword).strip() if keyword else ""
        category = str(category).strip() if category else ""
        
        if keyword:
            query += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY id DESC"
        result = self.db.execute_query(query, tuple(params))
        return result
    
    def update_book(self, book_id: int, **kwargs) -> bool:
        """更新图书信息"""
        allowed_fields = ['title', 'author', 'isbn', 'category', 'publisher', 
                         'publish_date', 'total_copies', 'status']
        updates = []
        params = []
        
        # 记录是否更新了total_copies或available_copies，需要重新计算状态
        need_status_update = False
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f"{field} = ?")
                params.append(value)
                # 如果更新了total_copies，需要重新计算available_copies和状态
                if field == 'total_copies':
                    need_status_update = True
        
        if not updates:
            return False
        
        params.append(book_id)
        query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
        result = self.db.execute_update(query, tuple(params)) > 0
        
        # 如果更新了total_copies，需要同步更新available_copies
        if 'total_copies' in kwargs and kwargs['total_copies'] is not None:
            # 获取当前图书信息
            book = self.get_book(book_id)
            if book:
                new_total = kwargs['total_copies']
                current_available = book.get('available_copies', 0)
                # 如果新的总数小于当前可借数量，调整可借数量
                if new_total < current_available:
                    self.db.execute_update(
                        "UPDATE books SET available_copies = ? WHERE id = ?",
                        (new_total, book_id)
                    )
                # 根据新的可借数量更新状态
                updated_book = self.get_book(book_id)
                if updated_book:
                    if updated_book['available_copies'] <= 0:
                        self.db.execute_update(
                            "UPDATE books SET status = 'unavailable' WHERE id = ?",
                            (book_id,)
                        )
                    elif updated_book['status'] == 'unavailable' and updated_book['available_copies'] > 0:
                        self.db.execute_update(
                            "UPDATE books SET status = 'available' WHERE id = ?",
                            (book_id,)
                        )
        
        # 无论是否更新total_copies，都要检查并同步状态
        book = self.get_book(book_id)
        if book:
            if book['available_copies'] <= 0 and book['status'] != 'unavailable':
                # 如果可借数量为0但状态不是unavailable，更新状态
                self.db.execute_update(
                    "UPDATE books SET status = 'unavailable' WHERE id = ?",
                    (book_id,)
                )
            elif book['available_copies'] > 0 and book['status'] == 'unavailable':
                # 如果可借数量>0但状态是unavailable，更新状态为available
                self.db.execute_update(
                    "UPDATE books SET status = 'available' WHERE id = ?",
                    (book_id,)
                )
        
        return result
    
    def delete_book(self, book_id: int) -> bool:
        """删除图书"""
        return self.db.execute_update("DELETE FROM books WHERE id = ?", (book_id,)) > 0
    
    def get_all_categories(self) -> List[str]:
        """获取所有图书分类"""
        categories = self.db.execute_query(
            "SELECT DISTINCT category FROM books WHERE category IS NOT NULL AND category != ''"
        )
        return [cat['category'] for cat in categories]

class BorrowModel:
    """借阅模型"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_borrow_return_trend(self, days: int = 30) -> List[Dict]:
        """获取指定天数内的借阅/归还趋势"""
        days = max(1, days)
        start_date = (datetime.now().date() - timedelta(days=days - 1)).isoformat()
        borrow_rows = self.db.execute_query(
            """
            SELECT DATE(borrow_date) AS day, COUNT(*) AS count
            FROM borrow_records
            WHERE borrow_date >= ?
            GROUP BY DATE(borrow_date)
            ORDER BY day
            """,
            (start_date,)
        )
        return_rows = self.db.execute_query(
            """
            SELECT DATE(return_date) AS day, COUNT(*) AS count
            FROM borrow_records
            WHERE return_date IS NOT NULL AND return_date >= ?
            GROUP BY DATE(return_date)
            ORDER BY day
            """,
            (start_date,)
        )
        borrow_map = {row['day']: row['count'] for row in borrow_rows}
        return_map = {row['day']: row['count'] for row in return_rows}
        trend = []
        # 生成连续日期
        for i in range(days):
            day = (datetime.now().date() - timedelta(days=days - 1 - i)).isoformat()
            trend.append({
                'day': day,
                'borrow_count': borrow_map.get(day, 0),
                'return_count': return_map.get(day, 0)
            })
        return trend
    
    def get_borrow_status_counts(self) -> List[Dict]:
        """借阅状态分布"""
        rows = self.db.execute_query(
            """
            SELECT status, COUNT(*) AS count
            FROM borrow_records
            GROUP BY status
            """
        )
        return rows or []
    
    def get_borrow_durations(self) -> List[int]:
        """返回所有已归还记录的借阅时长"""
        rows = self.db.execute_query(
            """
            SELECT GREATEST(DATEDIFF(return_date, borrow_date), 0) AS duration
            FROM borrow_records
            WHERE return_date IS NOT NULL AND status = 'returned'
            """
        )
        return [row['duration'] for row in rows if row.get('duration') is not None]
    
    def get_overdue_days(self) -> List[int]:
        """返回逾期天数集合"""
        rows = self.db.execute_query(
            """
            SELECT GREATEST(DATEDIFF(return_date, due_date), 0) AS overdue_days
            FROM borrow_records
            WHERE return_date IS NOT NULL AND DATEDIFF(return_date, due_date) > 0
            """
        )
        return [row['overdue_days'] for row in rows if row.get('overdue_days') is not None]
    
    def get_top_borrowers(self, limit: int = 10) -> List[Dict]:
        """借阅次数 TOP N"""
        limit = max(1, limit)
        rows = self.db.execute_query(
            """
            SELECT 
                u.id AS user_id,
                u.name AS name,
                u.username AS username,
                COUNT(*) AS borrow_count
            FROM borrow_records br
            JOIN users u ON br.user_id = u.id
            GROUP BY br.user_id
            ORDER BY borrow_count DESC
            LIMIT ?
            """,
            (limit,)
        )
        return rows or []
    
    def borrow_book(self, user_id: int, book_id: int, days: int = 30) -> Tuple[bool, str]:
        """借阅图书
        返回: (成功标志, 错误信息)
        """
        try:
            # 检查图书是否可借
            book = BookModel(self.db).get_book(book_id)
            if not book or book['available_copies'] <= 0:
                return False, "该图书暂无可借副本"
            
            # 获取用户信息，检查借阅数量限制
            user = UserModel(self.db).get_user(user_id)
            if not user:
                return False, "用户不存在"
            
            # 查询用户当前未归还的借阅数量
            current_borrows = self.db.execute_query(
                """SELECT COUNT(*) as count FROM borrow_records 
                   WHERE user_id = ? AND status = 'borrowed'""",
                (user_id,)
            )
            current_count = current_borrows[0]['count'] if current_borrows else 0
            
            # 根据用户角色设置借阅限制
            user_role = user.get('role', 'user')
            if user_role == 'user':
                max_borrows = 2  # 普通用户最多借阅2本
                role_name = "普通用户"
            elif user_role == 'member':
                max_borrows = 5  # 会员用户最多借阅5本
                role_name = "会员用户"
            else:
                # 管理员或其他角色，设置一个较大的限制（或不限制）
                max_borrows = 999  # 管理员基本不限制
                role_name = "管理员"
            
            # 检查是否超过借阅限制
            if current_count >= max_borrows:
                return False, f"{role_name}最多可借阅{max_borrows}本，您当前已借阅{current_count}本，无法继续借阅"
            
            # 计算归还日期
            borrow_date = datetime.now().date()
            due_date = borrow_date + timedelta(days=days)
            
            # 创建借阅记录
            self.db.execute_insert(
                """INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, book_id, borrow_date, due_date, 'borrowed')
            )
            
            # 更新图书可借数量
            self.db.execute_update(
                "UPDATE books SET available_copies = available_copies - 1 WHERE id = ?",
                (book_id,)
            )
            
            # 检查可借数量，如果为0则设置状态为unavailable
            updated_book = BookModel(self.db).get_book(book_id)
            if updated_book and updated_book['available_copies'] <= 0:
                self.db.execute_update(
                    "UPDATE books SET status = 'unavailable' WHERE id = ?",
                    (book_id,)
                )
            
            return True, "借阅成功"
        except Exception as e:
            print(f"借阅失败: {e}")
            return False, f"借阅失败: {str(e)}"
    
    def return_book(self, record_id: int) -> bool:
        """归还图书"""
        try:
            # 获取借阅记录
            records = self.db.execute_query(
                "SELECT * FROM borrow_records WHERE id = ?", (record_id,)
            )
            if not records:
                return False
            
            record = records[0]
            if record['status'] == 'returned':
                return False
            
            # 更新借阅记录
            return_date = datetime.now().date()
            self.db.execute_update(
                """UPDATE borrow_records SET return_date = ?, status = 'returned'
                   WHERE id = ?""",
                (return_date, record_id)
            )
            
            # 更新图书可借数量
            book_id = record['book_id']
            self.db.execute_update(
                "UPDATE books SET available_copies = available_copies + 1 WHERE id = ?",
                (book_id,)
            )
            
            # 检查可借数量，如果>0且当前状态是unavailable，则设置为available
            updated_book = BookModel(self.db).get_book(book_id)
            if updated_book and updated_book['available_copies'] > 0 and updated_book['status'] == 'unavailable':
                self.db.execute_update(
                    "UPDATE books SET status = 'available' WHERE id = ?",
                    (book_id,)
                )
            
            return True
        except Exception as e:
            print(f"归还失败: {e}")
            return False
    
    def update_borrow(self, record_id: int, status: str = None, due_date: Any = None,
                      return_date: Any = None, fine_amount: Any = None) -> bool:
        """更新借阅记录（管理员可用）
        支持更新 status/due_date/return_date/fine_amount，并同步更新图书可借数量与状态
        """
        try:
            # 查询原始记录
            rows = self.db.execute_query("SELECT * FROM borrow_records WHERE id = ?", (record_id,))
            if not rows:
                return False
            record = rows[0]
            old_status = record.get('status')
            book_id = record.get('book_id')

            updates = []
            params = []
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if due_date is not None:
                updates.append("due_date = ?")
                params.append(due_date)
            if return_date is not None:
                updates.append("return_date = ?")
                params.append(return_date)
            if fine_amount is not None:
                updates.append("fine_amount = ?")
                params.append(fine_amount)

            if not updates:
                return False

            params.append(record_id)
            query = f"UPDATE borrow_records SET {', '.join(updates)} WHERE id = ?"
            updated = self.db.execute_update(query, tuple(params)) > 0

            # 同步图书表的 available_copies 与 status
            if updated and book_id:
                # 重新读取记录以获取新状态
                new_rec = self.db.execute_query("SELECT * FROM borrow_records WHERE id = ?", (record_id,))
                new_status = new_rec[0].get('status') if new_rec else None
                # 如果由非返回状态变为已归还，需要增加可借数量
                if old_status != 'returned' and new_status == 'returned':
                    self.db.execute_update(
                        "UPDATE books SET available_copies = available_copies + 1 WHERE id = ?",
                        (book_id,)
                    )
                # 如果由已归还变为非已归还（管理员恢复借阅），则减少可借数量（但不小于0）
                if old_status == 'returned' and new_status != 'returned':
                    self.db.execute_update(
                        "UPDATE books SET available_copies = GREATEST(available_copies - 1, 0) WHERE id = ?",
                        (book_id,)
                    )
                # 调整图书状态字段
                updated_book = self.db.execute_query("SELECT * FROM books WHERE id = ?", (book_id,))
                if updated_book:
                    ab = updated_book[0].get('available_copies', 0)
                    if ab <= 0:
                        self.db.execute_update("UPDATE books SET status = 'unavailable' WHERE id = ?", (book_id,))
                    else:
                        self.db.execute_update("UPDATE books SET status = 'available' WHERE id = ?", (book_id,))

            return updated
        except Exception as e:
            print(f"更新借阅记录失败: {e}")
            return False
    
    def get_user_borrows(self, user_id: int, status: str = None) -> List[Dict]:
        """获取用户的借阅记录"""
        query = """SELECT br.*, b.title, b.author, b.isbn
                   FROM borrow_records br
                   JOIN books b ON br.book_id = b.id
                   WHERE br.user_id = ?"""
        params = [user_id]
        
        if status:
            query += " AND br.status = ?"
            params.append(status)
        
        query += " ORDER BY br.borrow_date DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_all_borrows(self, status: str = None) -> List[Dict]:
        """获取所有借阅记录（管理员）"""
        query = """SELECT br.*, b.title, b.author, u.name as user_name, u.username
                   FROM borrow_records br
                   JOIN books b ON br.book_id = b.id
                   JOIN users u ON br.user_id = u.id
                   WHERE 1=1"""
        params = []
        
        if status:
            query += " AND br.status = ?"
            params.append(status)
        
        query += " ORDER BY br.borrow_date DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_statistics(self) -> Dict:
        """获取借阅统计信息"""
        stats = {}
        
        # 总借阅数
        total = self.db.execute_query("SELECT COUNT(*) as count FROM borrow_records")
        stats['total_borrows'] = total[0]['count'] if total else 0
        
        # 当前借阅数
        current = self.db.execute_query(
            "SELECT COUNT(*) as count FROM borrow_records WHERE status = 'borrowed'"
        )
        stats['current_borrows'] = current[0]['count'] if current else 0
        
        # 逾期数
        overdue = self.db.execute_query(
            """SELECT COUNT(*) as count FROM borrow_records 
               WHERE status = 'borrowed' AND due_date < CURDATE()"""
        )
        stats['overdue'] = overdue[0]['count'] if overdue else 0
        
        # 总图书数
        books = self.db.execute_query("SELECT COUNT(*) as count FROM books")
        stats['total_books'] = books[0]['count'] if books else 0
        
        # 可借图书数
        available = self.db.execute_query(
            "SELECT COUNT(*) as count FROM books WHERE available_copies > 0"
        )
        stats['available_books'] = available[0]['count'] if available else 0
        
        return stats

class EmailModel:
    """邮件模型：保存管理员发送的邮件并尝试通过 SMTP 发送（可选）"""

    def __init__(self, db: Database):
        self.db = db

    def send_email(self, sender_id: int, recipient_user_id: Optional[int], recipient_email: Optional[str],
                   subject: str, body: str, try_send: bool = False) -> bool:
        """
        将邮件保存到数据库。若 try_send=True 且 SMTP 配置存在，则尝试发送邮件。
        如果发送成功，则将 status 标记为 'sent' 并记录 sent_at，否则保持 'draft'。
        """
        try:
            status = 'draft'
            sent_at = None
            # 如果需要并且配置可用，尝试发送
            if try_send and SMTP_CONFIG and SMTP_CONFIG.get('host'):
                try:
                    host = SMTP_CONFIG.get('host')
                    port = SMTP_CONFIG.get('port', 587)
                    user = SMTP_CONFIG.get('user')
                    password = SMTP_CONFIG.get('password')
                    use_tls = SMTP_CONFIG.get('use_tls', True)
                    msg = MIMEText(body, 'plain', 'utf-8')
                    msg['Subject'] = subject
                    msg['From'] = user or 'noreply'
                    msg['To'] = recipient_email or ''
                    server = smtplib.SMTP(host, port, timeout=10)
                    if use_tls:
                        server.starttls()
                    if user and password:
                        server.login(user, password)
                    server.sendmail(msg['From'], [recipient_email], msg.as_string())
                    server.quit()
                    status = 'sent'
                    sent_at = datetime.now()
                except Exception as e:
                    # 发送失败，保持 draft 状态并将异常打印
                    print(f"邮件发送失败: {e}")

            # 保存数据库记录（无论是否发送成功都保存）
            self.db.execute_insert(
                """INSERT INTO emails (sender_id, recipient_user_id, recipient_email, subject, body, status, sent_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sender_id, recipient_user_id, recipient_email, subject, body, status, sent_at)
            )
            return True
        except Exception as e:
            print(f"保存邮件失败: {e}")
            return False

    def get_emails_for_user(self, user_id: int) -> List[Dict]:
        """获取发给指定用户（或由管理员发出的）邮件记录"""
        rows = self.db.execute_query(
            "SELECT * FROM emails WHERE recipient_user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return rows or []

    def get_all_emails(self) -> List[Dict]:
        """管理员查询所有邮件记录"""
        rows = self.db.execute_query("SELECT * FROM emails ORDER BY created_at DESC")
        return rows or []

