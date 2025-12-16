"""
生成测试数据脚本
随机生成书籍、用户和借阅关系数据并插入到数据库中
"""
import random
from datetime import datetime, timedelta
from database import Database
from models import UserModel, BookModel, BorrowModel
import hashlib

# 预设数据池
CHINESE_SURNAMES = ['张', '王', '李', '刘', '陈', '杨', '赵', '黄', '周', '吴', 
                    '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗',
                    '梁', '宋', '郑', '谢', '韩', '唐', '冯', '于', '董', '萧']

CHINESE_GIVEN_NAMES = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
                       '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞',
                       '平', '刚', '桂英', '建华', '文', '华', '建国', '红', '志强', '梅']

BOOK_TITLES = [
    'Python编程从入门到实践', 'Java核心技术', '数据结构与算法', '计算机网络', '操作系统概念',
    '数据库系统概论', '软件工程', '编译原理', '计算机组成原理', '算法导论',
    '深入理解计算机系统', '设计模式', '重构', '代码整洁之道', '人月神话',
    '三体', '百年孤独', '1984', '动物农场', '围城',
    '活着', '平凡的世界', '白夜行', '嫌疑人X的献身', '解忧杂货店',
    '红楼梦', '西游记', '水浒传', '三国演义', '史记',
    '时间简史', '人类简史', '未来简史', '枪炮、病菌与钢铁', '思考，快与慢',
    '经济学原理', '管理学', '市场营销', '财务管理', '战略管理'
]

BOOK_AUTHORS = [
    '张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十',
    '刘德华', '张学友', '郭富城', '黎明', '成龙', '李连杰', '周星驰', '梁朝伟',
    '鲁迅', '老舍', '巴金', '茅盾', '沈从文', '钱钟书', '张爱玲', '三毛',
    '史蒂芬·霍金', '尤瓦尔·赫拉利', '马尔克斯', '村上春树', '东野圭吾', '余华', '莫言', '路遥'
]

PUBLISHERS = [
    '人民文学出版社', '商务印书馆', '中华书局', '清华大学出版社', '北京大学出版社',
    '机械工业出版社', '电子工业出版社', '人民邮电出版社', '高等教育出版社', '科学出版社',
    '上海译文出版社', '译林出版社', '中信出版社', '三联书店', '作家出版社'
]

CATEGORIES = [
    '计算机', '文学', '历史', '哲学', '经济', '管理', '科学', '艺术',
    '小说', '传记', '教育', '心理学', '社会学', '政治', '法律', '医学'
]

def hash_password(password: str) -> str:
    """密码加密"""
    return hashlib.md5(password.encode()).hexdigest()

def generate_username(name: str, index: int) -> str:
    """生成用户名"""
    return f"{name}{index:03d}"

def generate_email(name: str, index: int) -> str:
    """生成邮箱"""
    return f"{name.lower()}{index}@example.com"

def generate_phone() -> str:
    """生成手机号"""
    return f"1{random.randint(3, 9)}{random.randint(100000000, 999999999)}"

def generate_isbn() -> str:
    """生成ISBN"""
    return f"978-7-{random.randint(100, 999)}-{random.randint(10000, 99999)}-{random.randint(0, 9)}"

def generate_publish_date() -> str:
    """生成出版日期"""
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2023, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    publish_date = start_date + timedelta(days=random_days)
    return publish_date.strftime('%Y-%m-%d')

def generate_chinese_name() -> str:
    """生成中文姓名"""
    surname = random.choice(CHINESE_SURNAMES)
    given_name = ''.join(random.choices(CHINESE_GIVEN_NAMES, k=random.randint(1, 2)))
    return surname + given_name

def generate_users(db: Database, count: int = 20):
    """生成用户数据"""
    print(f"正在生成 {count} 个用户...")
    user_model = UserModel(db)
    
    roles = ['user', 'member', 'user', 'member', 'user']  # 增加普通用户和会员的比例
    generated_users = []
    
    for i in range(count):
        name = generate_chinese_name().strip()  # 确保名字没有首尾空格
        username = generate_username(name, i + 1).strip()  # 确保用户名没有首尾空格
        password = "123456"  # 统一密码方便测试
        role = random.choice(roles)
        email = generate_email(name, i + 1).strip()  # 去除首尾空格
        phone = generate_phone().strip()  # 去除首尾空格
        age = random.randint(16, 65)
        
        # 确保 role 值正确
        if role not in ['admin', 'member', 'user']:
            role = 'user'  # 默认值
        
        try:
            # 先检查用户名是否已存在
            existing = db.execute_query(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )
            if existing:
                print(f"  ✗ 创建用户失败 {username}: 用户名已存在")
                continue
            
            # 使用 admin_add_user 方法，它有更好的错误处理
            success, error_msg = user_model.admin_add_user(username, password, role, name, email, phone, age)
            if success:
                # 获取刚创建的用户ID
                user = user_model.login(username, password)
                if user:
                    user['age'] = age
                    generated_users.append(user)
                    print(f"  ✓ 创建用户: {username} ({name}) - {role}")
            else:
                print(f"  ✗ 创建用户失败 {username}: {error_msg}")
        except Exception as e:
            print(f"  ✗ 创建用户失败 {username}: {e}")
    
    print(f"成功生成 {len(generated_users)} 个用户\n")
    return generated_users

def generate_books(db: Database, count: int = 30):
    """生成书籍数据"""
    print(f"正在生成 {count} 本图书...")
    book_model = BookModel(db)
    generated_books = []
    
    for i in range(count):
        title = random.choice(BOOK_TITLES)
        author = random.choice(BOOK_AUTHORS)
        isbn = generate_isbn()
        category = random.choice(CATEGORIES)
        publisher = random.choice(PUBLISHERS)
        publish_date = generate_publish_date()
        total_copies = random.randint(1, 5)  # 每本书1-5本
        
        try:
            success = book_model.add_book(
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                publisher=publisher,
                publish_date=publish_date,
                total_copies=total_copies
            )
            if success:
                # 获取刚创建的图书ID（使用 keyword 参数搜索 ISBN）
                books = book_model.search_books(keyword=isbn)
                if books:
                    # 找到匹配的 ISBN
                    matched_book = None
                    for book in books:
                        if book.get('isbn') == isbn:
                            matched_book = book
                            break
                    if matched_book:
                        generated_books.append(matched_book)
                        print(f"  ✓ 创建图书: {title} - {author} ({total_copies}本)")
                    else:
                        # 如果没找到精确匹配，使用第一个结果
                        generated_books.append(books[0])
                        print(f"  ✓ 创建图书: {title} - {author} ({total_copies}本)")
                else:
                    # 如果搜索不到，直接查询数据库获取最新创建的图书
                    all_books = db.execute_query(
                        "SELECT * FROM books WHERE isbn = %s ORDER BY id DESC LIMIT 1",
                        (isbn,)
                    )
                    if all_books:
                        generated_books.append(all_books[0])
                        print(f"  ✓ 创建图书: {title} - {author} ({total_copies}本)")
        except Exception as e:
            print(f"  ✗ 创建图书失败 {title}: {e}")
    
    print(f"成功生成 {len(generated_books)} 本图书\n")
    return generated_books

def generate_borrows(db: Database, users: list, books: list, count: int = 40):
    """生成借阅关系"""
    print(f"正在生成 {count} 条借阅记录...")
    borrow_model = BorrowModel(db)
    book_model = BookModel(db)
    generated_borrows = 0
    
    # 确保有足够的用户和图书
    if not users or not books:
        print("  ✗ 用户或图书数据不足，无法生成借阅记录")
        return
    
    for i in range(count):
        user = random.choice(users)
        book = random.choice(books)
        
        # 检查图书是否可借
        if book['available_copies'] <= 0:
            continue
        
        # 随机决定借阅天数（15-60天）
        days = random.randint(15, 60)
        
        try:
            success, message = borrow_model.borrow_book(user['id'], book['id'], days)
            if success:
                generated_borrows += 1
                
                # 随机决定是否归还（70%已归还，30%未归还）
                if random.random() < 0.7:
                    # 获取刚创建的借阅记录（最新的未归还记录）
                    borrows = db.execute_query(
                        """SELECT * FROM borrow_records 
                           WHERE user_id = ? AND book_id = ? AND status = 'borrowed'
                           ORDER BY id DESC LIMIT 1""",
                        (user['id'], book['id'])
                    )
                    if borrows:
                        borrow = borrows[0]
                        # 随机生成归还日期（借阅日期到今天的某个时间）
                        borrow_date = borrow['borrow_date']
                        if isinstance(borrow_date, str):
                            borrow_date = datetime.strptime(borrow_date, '%Y-%m-%d').date()
                        today = datetime.now().date()
                        if borrow_date < today:
                            return_date = borrow_date + timedelta(days=random.randint(1, min(days, (today - borrow_date).days)))
                            # 直接更新数据库
                            db.execute_update(
                                """UPDATE borrow_records SET return_date = ?, status = 'returned' WHERE id = ?""",
                                (return_date, borrow['id'])
                            )
                            # 更新图书可借数量
                            db.execute_update(
                                "UPDATE books SET available_copies = available_copies + 1 WHERE id = ?",
                                (book['id'],)
                            )
                            print(f"  ✓ 创建借阅记录: {user['name']} 借阅《{book['title']}》 (已归还)")
                else:
                    print(f"  ✓ 创建借阅记录: {user['name']} 借阅《{book['title']}》 (未归还)")
                
                # 更新book的available_copies（因为borrow_book已经减1了）
                updated_book = book_model.get_book(book['id'])
                if updated_book:
                    book['available_copies'] = updated_book['available_copies']
        except Exception as e:
            print(f"  ✗ 创建借阅记录失败: {e}")
    
    print(f"成功生成 {generated_borrows} 条借阅记录\n")

def main():
    """主函数"""
    print("=" * 60)
    print("开始生成测试数据")
    print("=" * 60)
    print()
    
    # 初始化数据库
    db = Database()
    book_model = BookModel(db)
    
    # 询问是否清空现有数据
    print("警告：此操作将生成测试数据，不会删除现有数据。")
    print("如果数据库已有数据，新数据将追加到现有数据中。")
    print()
    
    # 生成数据
    try:
        # 生成用户
        users = generate_users(db, count=20)
        
        # 生成图书
        books = generate_books(db, count=30)
        
        # 生成借阅关系
        if users and books:
            generate_borrows(db, users, books, count=40)
        
        print("=" * 60)
        print("测试数据生成完成！")
        print("=" * 60)
        print()
        print("默认用户密码: 123456")
        print("可以使用以下账号登录测试:")
        print("  - 管理员: admin / admin123")
        print("  - 普通用户: 使用生成的用户名 / 123456")
        print()
        
    except Exception as e:
        print(f"生成数据时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

