"""
网络客户端模块
负责与服务端通信
"""
import socket
import json
import struct
from typing import Optional, Dict, List, Tuple, Any

_UNSET = object()

class NetworkClient:
    """网络客户端类"""
    
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.socket:
            self.socket.close()
            self.connected = False
    
    def _receive_all_data(self, expected_size):
        """接收指定长度的所有数据"""
        buffer = b''
        while len(buffer) < expected_size:
            chunk = self.socket.recv(expected_size - len(buffer))
            if not chunk:
                break
            buffer += chunk
        return buffer
    
    def _send_data(self, data):
        """发送数据（带长度前缀）"""
        data_bytes = data.encode('utf-8')
        length = len(data_bytes)
        # 先发送4字节的长度（大端序）
        self.socket.send(struct.pack('>I', length))
        # 然后发送数据
        self.socket.send(data_bytes)
    
    def send_request(self, action: str, data: dict = None) -> Optional[Dict]:
        """发送请求到服务器"""
        if not self.connected or not self.socket:
            return {'success': False, 'message': '未连接到服务器'}
        
        try:
            request = {
                'action': action,
                'data': data or {}
            }
            request_json = json.dumps(request, ensure_ascii=False)
            self._send_data(request_json)
            
            # 先接收4字节的长度
            length_data = self._receive_all_data(4)
            if len(length_data) != 4:
                return {'success': False, 'message': '服务器断开连接'}
            
            # 解析长度
            data_length = struct.unpack('>I', length_data)[0]
            
            # 接收完整响应数据
            response_data = self._receive_all_data(data_length)
            if len(response_data) != data_length:
                return {'success': False, 'message': '数据接收不完整'}
            
            response = json.loads(response_data.decode('utf-8'))
            return response
        except json.JSONDecodeError as e:
            return {'success': False, 'message': f'JSON解析错误: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'通信错误: {str(e)}'}
    
    # 用户相关方法
    def login(self, username: str, password: str) -> Optional[Dict]:
        """登录"""
        response = self.send_request('login', {
            'username': username,
            'password': password
        })
        return response.get('data') if response.get('success') else None
    
    def register(self, username: str, password: str, role: str, name: str,
                 email: str = "", phone: str = "", age: Optional[int] = None) -> bool:
        """注册"""
        payload = {
            'username': username,
            'password': password,
            'role': role,
            'name': name,
            'email': email,
            'phone': phone
        }
        if age is not None:
            payload['age'] = age
        response = self.send_request('register', payload)
        return response.get('success', False)
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        response = self.send_request('get_user_info', {'user_id': user_id})
        return response.get('data') if response.get('success') else None
    
    def update_user_info(self, user_id: int, name: str = None, email: str = None,
                        phone: str = None, age: Any = _UNSET) -> bool:
        """更新用户信息"""
        data = {'user_id': user_id}
        if name:
            data['name'] = name
        if email:
            data['email'] = email
        if phone:
            data['phone'] = phone
        if age is not _UNSET:
            data['age'] = age
        response = self.send_request('update_user_info', data)
        return response.get('success', False)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        response = self.send_request('change_password', {
            'user_id': user_id,
            'old_password': old_password,
            'new_password': new_password
        })
        return response.get('success', False)
    
    # 图书相关方法
    def search_books(self, keyword: str = "", category: str = "") -> List[Dict]:
        """搜索图书"""
        response = self.send_request('search_books', {
            'keyword': keyword or "",
            'category': category or ""
        })
        if response and response.get('success'):
            data = response.get('data', [])
            return data if isinstance(data, list) else []
        else:
            # 如果请求失败，返回空列表
            error_msg = response.get('message', '未知错误') if response else '未连接到服务器'
            print(f"搜索图书失败: {error_msg}")
            return []
    
    def get_book(self, book_id: int) -> Optional[Dict]:
        """获取图书详情"""
        response = self.send_request('get_book', {'book_id': book_id})
        return response.get('data') if response.get('success') else None
    
    def borrow_book(self, user_id: int, book_id: int, days: int = 30) -> Tuple[bool, str]:
        """借阅图书
        返回: (成功标志, 错误信息)
        """
        response = self.send_request('borrow_book', {
            'user_id': user_id,
            'book_id': book_id,
            'days': days
        })
        success = response.get('success', False)
        message = response.get('message', '借阅失败')
        return success, message
    
    def return_book(self, record_id: int) -> bool:
        """归还图书"""
        response = self.send_request('return_book', {'record_id': record_id})
        return response.get('success', False)
    
    def get_my_borrows(self, user_id: int, status: str = None) -> List[Dict]:
        """获取我的借阅记录"""
        response = self.send_request('get_my_borrows', {
            'user_id': user_id,
            'status': status
        })
        return response.get('data', []) if response.get('success') else []
    
    # 管理员方法
    def add_book(self, title: str, author: str, isbn: str = "", category: str = "",
                 publisher: str = "", publish_date: str = "", total_copies: int = 1) -> bool:
        """添加图书"""
        response = self.send_request('add_book', {
            'title': title,
            'author': author,
            'isbn': isbn,
            'category': category,
            'publisher': publisher,
            'publish_date': publish_date,
            'total_copies': total_copies
        })
        return response.get('success', False)
    
    def update_book(self, book_id: int, **kwargs) -> bool:
        """更新图书"""
        data = {'book_id': book_id}
        data.update(kwargs)
        response = self.send_request('update_book', data)
        return response.get('success', False)
    
    def delete_book(self, book_id: int) -> bool:
        """删除图书"""
        response = self.send_request('delete_book', {'book_id': book_id})
        return response.get('success', False)
    
    def get_all_borrows(self, status: str = None) -> List[Dict]:
        """获取所有借阅记录"""
        try:
            response = self.send_request('get_all_borrows', {'status': status})
            if response and response.get('success'):
                data = response.get('data', [])
                return data if isinstance(data, list) else []
            else:
                error_msg = response.get('message', '未知错误') if response else '未连接到服务器'
                print(f"获取借阅记录失败: {error_msg}")
                return []
        except Exception as e:
            print(f"获取借阅记录异常: {e}")
            return []
    
    def get_statistics(self) -> Optional[Dict]:
        """获取统计信息"""
        response = self.send_request('get_statistics', {})
        return response.get('data') if response.get('success') else None
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        response = self.send_request('get_categories', {})
        return response.get('data', []) if response.get('success') else []
    
    def get_all_users(self) -> List[Dict]:
        """获取所有用户（管理员）"""
        try:
            response = self.send_request('get_all_users', {})
            if response and response.get('success'):
                data = response.get('data', [])
                return data if isinstance(data, list) else []
            else:
                error_msg = response.get('message', '未知错误') if response else '未连接到服务器'
                print(f"获取用户列表失败: {error_msg}")
                return []
        except Exception as e:
            print(f"获取用户列表异常: {e}")
            return []
    
    def admin_update_user(self, user_id: int, name: str = None, email: str = None,
                         phone: str = None, role: str = None, password: str = None,
                         age: Any = _UNSET) -> bool:
        """管理员更新用户信息"""
        data = {'user_id': user_id}
        if name is not None:
            data['name'] = name
        if email is not None:
            data['email'] = email
        if phone is not None:
            data['phone'] = phone
        if role is not None:
            data['role'] = role
        if password is not None:
            data['password'] = password
        if age is not _UNSET:
            data['age'] = age
        response = self.send_request('admin_update_user', data)
        return response.get('success', False)
    
    def admin_add_user(self, username: str, password: str, role: str, name: str,
                      email: str = "", phone: str = "", age: Optional[int] = None) -> Tuple[bool, str]:
        """管理员添加用户
        返回: (成功标志, 错误信息)
        """
        payload = {
            'username': username,
            'password': password,
            'role': role,
            'name': name,
            'email': email,
            'phone': phone
        }
        if age is not None:
            payload['age'] = age
        response = self.send_request('admin_add_user', payload)
        success = response.get('success', False)
        message = response.get('message', '未知错误')
        return success, message
    
    def admin_delete_user(self, user_id: int) -> bool:
        """管理员删除用户"""
        response = self.send_request('admin_delete_user', {'user_id': user_id})
        return response.get('success', False)
    
    def get_admin_dashboard_data(self, days: int = 30) -> Dict:
        """获取管理员图表数据"""
        response = self.send_request('get_admin_dashboard_data', {'days': days})
        return response.get('data', {}) if response.get('success') else {}
    
    def get_user_dashboard_data(self, months: int = 12, limit: int = 10) -> Dict:
        """获取用户/会员图表数据"""
        response = self.send_request('get_user_dashboard_data', {
            'months': months,
            'limit': limit
        })
        return response.get('data', {}) if response.get('success') else {}
    
    def import_books_from_openlibrary(self, query: str = "subject:fiction", count: int = 100,
                                      batch_size: int = 100, delay: float = 0.5,
                                      copies: int = 3) -> Tuple[bool, str, Dict]:
        """从Open Library导入图书
        返回: (成功标志, 消息, 结果数据)
        """
        response = self.send_request('import_books_from_openlibrary', {
            'query': query,
            'count': count,
            'batch_size': batch_size,
            'delay': delay,
            'copies': copies
        })
        success = response.get('success', False)
        message = response.get('message', '未知错误')
        data = response.get('data', {})
        return success, message, data

