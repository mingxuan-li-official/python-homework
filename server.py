"""
图书管理系统服务端
处理客户端请求，提供远程访问功能
"""
import socket
import threading
import json
import struct
from datetime import datetime, date
from decimal import Decimal
from database import Database
from models import UserModel, BookModel, BorrowModel
from openlibrary_import import OpenLibraryImporter


def json_serialize(obj):
    """自定义JSON序列化函数，处理datetime、date和Decimal对象"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        # 将Decimal转换为float，保留精度
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

class LibraryServer:
    """图书管理系统服务端"""
    
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.db = Database()
        self.user_model = UserModel(self.db)
        self.book_model = BookModel(self.db)
        self.borrow_model = BorrowModel(self.db)
        self.running = False
    
    def handle_request(self, request: dict) -> dict:
        """处理客户端请求"""
        action = request.get('action')
        data = request.get('data', {})
        
        try:
            if action == 'login':
                return self.handle_login(data)
            elif action == 'register':
                return self.handle_register(data)
            elif action == 'get_user_info':
                return self.handle_get_user_info(data)
            elif action == 'update_user_info':
                return self.handle_update_user_info(data)
            elif action == 'change_password':
                return self.handle_change_password(data)
            elif action == 'search_books':
                return self.handle_search_books(data)
            elif action == 'get_book':
                return self.handle_get_book(data)
            elif action == 'borrow_book':
                return self.handle_borrow_book(data)
            elif action == 'return_book':
                return self.handle_return_book(data)
            elif action == 'get_my_borrows':
                return self.handle_get_my_borrows(data)
            # 管理员操作
            elif action == 'add_book':
                return self.handle_add_book(data)
            elif action == 'update_book':
                return self.handle_update_book(data)
            elif action == 'delete_book':
                return self.handle_delete_book(data)
            elif action == 'get_all_borrows':
                return self.handle_get_all_borrows(data)
            elif action == 'get_statistics':
                return self.handle_get_statistics(data)
            elif action == 'get_categories':
                return self.handle_get_categories(data)
            elif action == 'get_all_users':
                return self.handle_get_all_users(data)
            elif action == 'admin_update_user':
                return self.handle_admin_update_user(data)
            elif action == 'admin_add_user':
                return self.handle_admin_add_user(data)
            elif action == 'admin_delete_user':
                return self.handle_admin_delete_user(data)
            elif action == 'import_books_from_openlibrary':
                return self.handle_import_books_from_openlibrary(data)
            elif action == 'get_admin_dashboard_data':
                return self.handle_get_admin_dashboard_data(data)
            elif action == 'get_user_dashboard_data':
                return self.handle_get_user_dashboard_data(data)
            else:
                return {'success': False, 'message': f'未知操作: {action}'}
        except Exception as e:
            return {'success': False, 'message': f'服务器错误: {str(e)}'}
    
    def handle_login(self, data: dict) -> dict:
        """处理登录请求"""
        username = data.get('username')
        password = data.get('password')
        user = self.user_model.login(username, password)
        if user:
            return {'success': True, 'data': user}
        return {'success': False, 'message': '用户名或密码错误'}
    
    def handle_register(self, data: dict) -> dict:
        """处理注册请求"""
        success = self.user_model.register(
            data.get('username'),
            data.get('password'),
            data.get('role', 'user'),
            data.get('name'),
            data.get('email', ''),
            data.get('phone', ''),
            data.get('age')
        )
        return {'success': success, 'message': '注册成功' if success else '注册失败，用户名可能已存在'}
    
    def handle_get_user_info(self, data: dict) -> dict:
        """获取用户信息"""
        user = self.user_model.get_user(data.get('user_id'))
        if user:
            return {'success': True, 'data': user}
        return {'success': False, 'message': '用户不存在'}
    
    def handle_update_user_info(self, data: dict) -> dict:
        """更新用户信息"""
        kwargs = {
            'user_id': data.get('user_id'),
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone')
        }
        if 'age' in data:
            kwargs['age'] = data.get('age')
        success = self.user_model.update_user(**kwargs)
        return {'success': success, 'message': '更新成功' if success else '更新失败'}
    
    def handle_change_password(self, data: dict) -> dict:
        """修改密码"""
        success = self.user_model.change_password(
            data.get('user_id'),
            data.get('old_password'),
            data.get('new_password')
        )
        return {'success': success, 'message': '密码修改成功' if success else '原密码错误或修改失败'}
    
    def handle_search_books(self, data: dict) -> dict:
        """搜索图书"""
        books = self.book_model.search_books(
            data.get('keyword', ''),
            data.get('category', '')
        )
        return {'success': True, 'data': books}
    
    def handle_get_book(self, data: dict) -> dict:
        """获取图书详情"""
        book = self.book_model.get_book(data.get('book_id'))
        if book:
            return {'success': True, 'data': book}
        return {'success': False, 'message': '图书不存在'}
    
    def handle_borrow_book(self, data: dict) -> dict:
        """借阅图书"""
        success, message = self.borrow_model.borrow_book(
            data.get('user_id'),
            data.get('book_id'),
            data.get('days', 30)
        )
        return {'success': success, 'message': message}
    
    def handle_return_book(self, data: dict) -> dict:
        """归还图书"""
        success = self.borrow_model.return_book(data.get('record_id'))
        return {'success': success, 'message': '归还成功' if success else '归还失败'}
    
    def handle_get_my_borrows(self, data: dict) -> dict:
        """获取我的借阅记录"""
        borrows = self.borrow_model.get_user_borrows(
            data.get('user_id'),
            data.get('status')
        )
        return {'success': True, 'data': borrows}
    
    def handle_add_book(self, data: dict) -> dict:
        """添加图书（管理员）"""
        success = self.book_model.add_book(
            data.get('title'),
            data.get('author'),
            data.get('isbn', ''),
            data.get('category', ''),
            data.get('publisher', ''),
            data.get('publish_date', ''),
            data.get('total_copies', 1)
        )
        return {'success': success, 'message': '添加成功' if success else '添加失败'}
    
    def handle_update_book(self, data: dict) -> dict:
        """更新图书（管理员）"""
        book_id = data.pop('book_id')
        success = self.book_model.update_book(book_id, **data)
        return {'success': success, 'message': '更新成功' if success else '更新失败'}
    
    def handle_delete_book(self, data: dict) -> dict:
        """删除图书（管理员）"""
        success = self.book_model.delete_book(data.get('book_id'))
        return {'success': success, 'message': '删除成功' if success else '删除失败'}
    
    def handle_get_all_borrows(self, data: dict) -> dict:
        """获取所有借阅记录（管理员）"""
        borrows = self.borrow_model.get_all_borrows(data.get('status'))
        return {'success': True, 'data': borrows}
    
    def handle_get_statistics(self, data: dict) -> dict:
        """获取统计信息（管理员）"""
        stats = self.borrow_model.get_statistics()
        return {'success': True, 'data': stats}
    
    def handle_get_categories(self, data: dict) -> dict:
        """获取所有分类"""
        categories = self.book_model.get_all_categories()
        return {'success': True, 'data': categories}
    
    def handle_get_all_users(self, data: dict) -> dict:
        """获取所有用户（管理员）"""
        users = self.user_model.get_all_users()
        return {'success': True, 'data': users}
    
    def handle_admin_update_user(self, data: dict) -> dict:
        """管理员更新用户信息"""
        kwargs = {
            'user_id': data.get('user_id'),
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'role': data.get('role'),
            'password': data.get('password')
        }
        if 'age' in data:
            kwargs['age'] = data.get('age')
        success = self.user_model.admin_update_user(**kwargs)
        return {'success': success, 'message': '更新成功' if success else '更新失败'}
    
    def handle_admin_add_user(self, data: dict) -> dict:
        """管理员添加用户"""
        success, message = self.user_model.admin_add_user(
            data.get('username'),
            data.get('password'),
            data.get('role'),
            data.get('name'),
            data.get('email', ''),
            data.get('phone', ''),
            data.get('age')
        )
        return {'success': success, 'message': message}
    
    def handle_admin_delete_user(self, data: dict) -> dict:
        """管理员删除用户"""
        success = self.user_model.admin_delete_user(data.get('user_id'))
        if success:
            return {'success': True, 'message': '删除成功'}
        else:
            return {'success': False, 'message': '删除失败，用户可能不存在或有未归还的图书'}
    
    def handle_import_books_from_openlibrary(self, data: dict) -> dict:
        """从Open Library导入图书（管理员）"""
        try:
            query = data.get('query', 'subject:fiction')
            target_count = data.get('count', 100)
            batch_size = data.get('batch_size', 100)
            delay = data.get('delay', 0.5)
            copies = data.get('copies', 3)
            
            # 验证参数
            target_count = max(1, min(target_count, 10000))  # 限制在1-10000之间
            batch_size = max(1, min(batch_size, 100))  # 限制在1-100之间
            delay = max(0.1, min(delay, 5.0))  # 限制在0.1-5.0秒之间
            copies = max(1, min(copies, 100))  # 限制在1-100之间
            
            importer = OpenLibraryImporter(db=self.db, copies=copies)
            stored, skipped = importer.import_books(
                query=query,
                target_count=target_count,
                batch_size=batch_size,
                delay=delay
            )
            
            return {
                'success': True,
                'message': f'导入完成：成功 {stored} 本，跳过 {skipped} 本',
                'data': {
                    'stored': stored,
                    'skipped': skipped
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'导入失败: {str(e)}'}
    
    def handle_get_admin_dashboard_data(self, data: dict) -> dict:
        """管理员可视化数据"""
        try:
            days = data.get('days', 30)
            response = {
                'category_summary': self.book_model.get_category_summary(),
                'status_summary': self.book_model.get_status_summary(),
                'borrow_trend': self.borrow_model.get_borrow_return_trend(days),
                'borrow_status': self.borrow_model.get_borrow_status_counts(),
                'borrow_durations': self.borrow_model.get_borrow_durations(),
                'overdue_days': self.borrow_model.get_overdue_days()
            }
            return {'success': True, 'data': response}
        except Exception as e:
            return {'success': False, 'message': f'统计数据获取失败: {str(e)}'}
    
    def handle_get_user_dashboard_data(self, data: dict) -> dict:
        """用户可视化数据"""
        try:
            months = data.get('months', 12)
            limit = data.get('limit', 10)
            result = {
                'role_counts': self.user_model.get_role_counts(),
                'age_distribution': self.user_model.get_age_distribution(),
                'registration_trend': self.user_model.get_registration_trend(months),
                'top_borrowers': self.borrow_model.get_top_borrowers(limit)
            }
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'message': f'用户统计数据获取失败: {str(e)}'}
    
    def _receive_all_data(self, client_socket, expected_size):
        """接收指定长度的所有数据"""
        buffer = b''
        while len(buffer) < expected_size:
            chunk = client_socket.recv(expected_size - len(buffer))
            if not chunk:
                break
            buffer += chunk
        return buffer
    
    def _send_data(self, client_socket, data):
        """发送数据（带长度前缀）"""
        data_bytes = data.encode('utf-8')
        length = len(data_bytes)
        # 先发送4字节的长度（大端序）
        client_socket.send(struct.pack('>I', length))
        # 然后发送数据
        client_socket.send(data_bytes)
    
    def handle_client(self, client_socket, client_addr):
        """处理客户端连接"""
        print(f"[{client_addr}] 客户端已连接")
        try:
            while True:
                # 先接收4字节的长度
                length_data = self._receive_all_data(client_socket, 4)
                if len(length_data) != 4:
                    break
                
                # 解析长度
                data_length = struct.unpack('>I', length_data)[0]
                
                # 接收完整数据
                data = self._receive_all_data(client_socket, data_length)
                if len(data) != data_length:
                    break
                
                try:
                    request = json.loads(data.decode('utf-8'))
                    # 处理请求
                    response = self.handle_request(request)
                    # 发送响应（带长度前缀）
                    response_json = json.dumps(response, default=json_serialize, ensure_ascii=False)
                    self._send_data(client_socket, response_json)
                except json.JSONDecodeError:
                    error_response = json.dumps({
                        'success': False,
                        'message': '无效的请求格式'
                    }, ensure_ascii=False)
                    self._send_data(client_socket, error_response)
        except Exception as e:
            print(f"[{client_addr}] 连接错误: {e}")
        finally:
            client_socket.close()
            print(f"[{client_addr}] 客户端已断开")
    
    def start(self):
        """启动服务器"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        
        self.running = True
        print(f"图书管理系统服务端已启动，监听 {self.host}:{self.port}")
        
        try:
            while self.running:
                client_socket, client_addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_addr)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\n服务端正在关闭...")
        finally:
            server_socket.close()
            self.running = False

if __name__ == "__main__":
    server = LibraryServer()
    server.start()

