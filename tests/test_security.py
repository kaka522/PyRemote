import pytest
from pyremote.core.security import RSAEncryptor, DataValidator
import time

def test_rsa_encrypt_decrypt():
    """测试RSA加密解密功能（非对称加密）"""
    # 初始化两个加密器（模拟客户端和服务端）
    alice = RSAEncryptor()
    bob = RSAEncryptor()
    
    # 交换公钥
    alice.set_peer_public_key(bob.get_public_key_pem())
    bob.set_peer_public_key(alice.get_public_key_pem())
    
    # 测试加密解密
    test_data = b"PyRemote_Test_Data_123"
    encrypted = alice.encrypt(test_data)
    decrypted = bob.decrypt(encrypted)
    
    assert decrypted == test_data, "RSA加密解密失败：解密后数据与原数据不一致"

def test_data_validator():
    """测试数据校验功能（防篡改、防重放）"""
    validator = DataValidator()
    
    # 1. 测试正常数据封装与校验
    test_type = 1  # 1=屏幕截图数据
    test_data = b"Test_Screenshot_Data"
    packed = validator.pack_data(test_type, test_data)
    assert validator.validate_data(packed) is True, "正常数据校验失败"
    
    # 解包验证
    unpacked_type, unpacked_data = validator.unpack_data(packed)
    assert unpacked_type == test_type, "数据类型解包错误"
    assert unpacked_data == test_data, "数据内容解包错误"
    
    # 2. 测试数据篡改（修改1字节）
    tampered_packed = packed[:10] + b'x' + packed[11:]
    assert validator.validate_data(tampered_packed) is False, "篡改数据未被检测到"
    
    # 3. 测试时间戳过期（修改时间戳为1小时前）
    import struct
    # 提取原始时间戳字段（第4-12字节）
    original_timestamp = packed[4:12]
    # 计算1小时前的时间戳（毫秒级）
    old_timestamp = int(time.time() * 1000) - 3600 * 1000
    old_timestamp_bytes = struct.pack(">Q", old_timestamp)  # 8字节大端序
    # 构造过期数据
    expired_packed = packed[:4] + old_timestamp_bytes + packed[12:]
    assert validator.validate_data(expired_packed) is False, "过期数据未被检测到"