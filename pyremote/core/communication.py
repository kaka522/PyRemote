import socket
import threading
from pyremote.core.security import RSAEncryptor, DataValidator
from pyremote.utils.config import get_config

class TCPCommunication:
    def __init__(self):
        # 初始化配置、加密器、数据校验器
        self.config = get_config()
        self.rsa = RSAEncryptor()
        self.validator = DataValidator()
        self.socket = None
        self.is_connected = False
        self.on_data_received = None  # 数据接收回调函数

    def start_server(self, host, port):
        """启动服务端"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((host, port))
            self.socket.listen(5)
            print(f"服务端启动：{host}:{port}")
            
            # 异步接受连接
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return True
        except Exception as e:
            print(f"服务端启动失败：{str(e)}")
            return False

    def connect_client(self, host, port):
        """启动客户端（连接服务端）"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.is_connected = True
            
            # 双向认证
            if self._auth_exchange():
                print(f"客户端连接成功：{host}:{port}")
                # 异步接收数据
                threading.Thread(target=self._receive_data, daemon=True).start()
                return True
            else:
                print("客户端认证失败")
                self.socket.close()
                return False
        except Exception as e:
            print(f"客户端连接失败：{str(e)}")
            return False

    def _accept_connections(self):
        """异步接受客户端连接（服务端）"""
        while True:
            client_socket, addr = self.socket.accept()
            print(f"新连接：{addr}")
            
            # 双向认证
            if self._auth_exchange(client_socket):
                self.socket = client_socket
                self.is_connected = True
                # 异步接收数据
                threading.Thread(target=self._receive_data, daemon=True).start()
                break
            else:
                print(f"连接 {addr} 认证失败，关闭连接")
                client_socket.close()

    def _auth_exchange(self, socket=None):
        """双向认证（RSA公钥交换）"""
        target_socket = socket or self.socket
        try:
            # 发送本地公钥
            public_key = self.rsa.get_public_key_pem()
            target_socket.sendall(len(public_key).to_bytes(4, byteorder="big"))
            target_socket.sendall(public_key)
            
            # 接收对方公钥
            peer_key_len = int.from_bytes(target_socket.recv(4), byteorder="big")
            peer_public_key = target_socket.recv(peer_key_len)
            self.rsa.set_peer_public_key(peer_public_key)
            
            # 验证认证信息
            auth_msg = self.rsa.encrypt(b"PyRemote_Auth_OK")
            target_socket.sendall(len(auth_msg).to_bytes(4, byteorder="big"))
            target_socket.sendall(auth_msg)
            
            # 验证对方认证信息
            peer_auth_len = int.from_bytes(target_socket.recv(4), byteorder="big")
            peer_auth_msg = self.rsa.decrypt(target_socket.recv(peer_auth_len))
            return peer_auth_msg == b"PyRemote_Auth_OK"
        except Exception as e:
            print(f"认证失败：{str(e)}")
            return False

    def send_data(self, data_type, data):
        """发送数据（分块加密+校验）"""
        if not self.is_connected:
            print("未建立连接，无法发送数据")
            return False
        
        try:
            # 数据封装（类型+内容+校验和+时间戳）
            packed_data = self.validator.pack_data(data_type, data)
            # RSA加密
            encrypted_data = self.rsa.encrypt(packed_data)
            
            # 发送数据（长度前缀+加密内容）
            self.socket.sendall(len(encrypted_data).to_bytes(4, byteorder="big"))
            self.socket.sendall(encrypted_data)
            return True
        except Exception as e:
            print(f"数据发送失败：{str(e)}")
            self.is_connected = False
            return False

    def _receive_data(self):
        """异步接收数据"""
        while self.is_connected:
            try:
                # 接收数据长度
                data_len = int.from_bytes(self.socket.recv(4), byteorder="big")
                if data_len <= 0:
                    raise Exception("无效数据长度")
                
                # 接收加密数据
                encrypted_data = b""
                while len(encrypted_data) < data_len:
                    chunk = self.socket.recv(min(data_len - len(encrypted_data), 4096))
                    if not chunk:
                        raise Exception("连接中断")
                    encrypted_data += chunk
                
                # 解密+校验
                packed_data = self.rsa.decrypt(encrypted_data)
                if self.validator.validate_data(packed_data):
                    data_type, data = self.validator.unpack_data(packed_data)
                    # 调用回调函数处理数据
                    if self.on_data_received:
                        self.on_data_received(data_type, data)
            except Exception as e:
                print(f"数据接收失败：{str(e)}")
                self.is_connected = False
                break

    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
        self.is_connected = False