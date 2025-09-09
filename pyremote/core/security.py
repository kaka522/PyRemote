import time
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

class RSAEncryptor:
    """RSA非对称加密实现"""
    def __init__(self):
        # 生成RSA密钥对（2048位）
        self.key_pair = RSA.generate(2048)
        self.peer_public_key = None
        self.public_cipher = None  # 加密用（对方公钥）
        self.private_cipher = PKCS1_OAEP.new(self.key_pair)  # 解密用（本地私钥）

    def get_public_key_pem(self):
        """获取本地公钥（PEM格式）"""
        return self.key_pair.publickey().export_key()

    def set_peer_public_key(self, peer_public_key_pem):
        """设置对方公钥（用于加密）"""
        self.peer_public_key = RSA.import_key(peer_public_key_pem)
        self.public_cipher = PKCS1_OAEP.new(self.peer_public_key)

    def encrypt(self, data):
        """加密数据（使用对方公钥）"""
        if not self.public_cipher:
            raise Exception("未设置对方公钥，无法加密")
        # 分块加密（RSA 2048位最大加密长度为214字节）
        chunk_size = 214
        encrypted_chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            encrypted_chunk = self.public_cipher.encrypt(chunk)
            encrypted_chunks.append(encrypted_chunk)
        return b"".join(encrypted_chunks)

    def decrypt(self, encrypted_data):
        """解密数据（使用本地私钥）"""
        # 分块解密（RSA 2048位解密后长度为256字节）
        chunk_size = 256
        decrypted_chunks = []
        for i in range(0, len(encrypted_data), chunk_size):
            chunk = encrypted_data[i:i+chunk_size]
            decrypted_chunk = self.private_cipher.decrypt(chunk)
            decrypted_chunks.append(decrypted_chunk)
        return b"".join(decrypted_chunks)

class DataValidator:
    """数据校验（防篡改、防重放）"""
    def __init__(self):
        self.timestamp_window = 30  # 时间戳有效期（秒）

    def pack_data(self, data_type, data):
        """封装数据：类型(4字节) + 时间戳(8字节) + 内容 + 校验和(32字节)"""
        # 数据类型（整数，4字节）
        type_bytes = int(data_type).to_bytes(4, byteorder="big")
        # 时间戳（毫秒级，8字节）
        timestamp = int(time.time() * 1000).to_bytes(8, byteorder="big")
        # 校验和（SHA-256）
        checksum = hashlib.sha256(type_bytes + timestamp + data).digest()
        # 拼接数据
        return type_bytes + timestamp + data + checksum

    def unpack_data(self, packed_data):
        """解封装数据：返回（数据类型，内容）"""
        type_bytes = packed_data[:4]
        timestamp_bytes = packed_data[4:12]
        checksum = packed_data[-32:]
        data = packed_data[12:-32]
        
        data_type = int.from_bytes(type_bytes, byteorder="big")
        return data_type, data

    def validate_data(self, packed_data):
        """校验数据：1. 时间戳有效 2. 校验和匹配"""
        if len(packed_data) < 4 + 8 + 32:
            print("数据长度不足，校验失败")
            return False
        
        # 解包基础字段
        type_bytes = packed_data[:4]
        timestamp_bytes = packed_data[4:12]
        checksum = packed_data[-32:]
        data = packed_data[12:-32]
        
        # 1. 校验时间戳（防重放）
        timestamp = int.from_bytes(timestamp_bytes, byteorder="big") / 1000
        current_time = time.time()
        if abs(current_time - timestamp) > self.timestamp_window:
            print(f"时间戳过期（当前：{current_time}，数据：{timestamp}）")
            return False
        
        # 2. 校验和匹配（防篡改）
        calculated_checksum = hashlib.sha256(type_bytes + timestamp_bytes + data).digest()
        if calculated_checksum != checksum:
            print("校验和不匹配，数据被篡改")
            return False
        
        return True