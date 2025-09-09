import pystun3
import socket
from pyremote.utils.logger import logger

class P2PPenetration:
    """基于STUN协议的P2P穿透实现（解决NAT穿透问题）"""
    def __init__(self):
        self.stun_server = "stun.l.google.com:19302"  # 谷歌公共STUN服务器（免费）
        self.public_ip = None  # 公网IP
        self.public_port = None  # 公网端口
        self.local_ip = None    # 本地IP
        self.local_port = None  # 本地端口

    def get_nat_info(self, local_port=9999):
        """
        获取NAT信息（公网IP/端口、本地IP/端口）
        :param local_port: 本地监听端口
        :return: (public_ip, public_port, local_ip, local_port) 或 None（失败）
        """
        try:
            # 创建UDP socket用于STUN探测
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("", local_port))  # 绑定本地端口
            
            # 调用STUN获取NAT映射信息
            result = pystun3.get_ip_info(sock=sock, stun_host=self.stun_server.split(":")[0], 
                                        stun_port=int(self.stun_server.split(":")[1]))
            
            if result["type"] in ["Full Cone", "Restricted Cone", "Port Restricted Cone"]:
                # 支持穿透的NAT类型（对称NAT无法直接穿透）
                self.public_ip = result["public_ip"]
                self.public_port = result["public_port"]
                self.local_ip = result["local_ip"]
                self.local_port = local_port
                logger.info(f"NAT穿透信息获取成功：公网({self.public_ip}:{self.public_port})，本地({self.local_ip}:{self.local_port})")
                sock.close()
                return (self.public_ip, self.public_port, self.local_ip, self.local_port)
            else:
                logger.error(f"不支持的NAT类型：{result['type']}（无法进行P2P穿透）")
                sock.close()
                return None
        except Exception as e:
            logger.error(f"获取NAT信息失败：{str(e)}")
            return None

    def try_p2p_connect(self, peer_public_ip, peer_public_port, local_port=9999):
        """
        尝试P2P连接（向对方公网IP/端口发起连接）
        :param peer_public_ip: 对方公网IP
        :param peer_public_port: 对方公网端口
        :param local_port: 本地监听端口
        :return: 成功=socket对象，失败=None
        """
        try:
            # 先获取本地NAT信息
            if not self.get_nat_info(local_port):
                logger.error("获取本地NAT信息失败，无法发起P2P连接")
                return None
            
            # 创建TCP socket（P2P连接使用TCP保证可靠性）
            p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            p2p_socket.bind(("", local_port))  # 绑定本地端口（与STUN探测端口一致）
            p2p_socket.settimeout(10)  # 10秒超时（避免无限阻塞）
            
            # 向对方公网IP/端口发起连接（关键：NAT打孔）
            logger.info(f"尝试P2P连接：{peer_public_ip}:{peer_public_port}")
            p2p_socket.connect((peer_public_ip, peer_public_port))
            
            logger.info("P2P连接成功（已穿透NAT）")
            return p2p_socket
        except socket.timeout:
            logger.error("P2P连接超时（可能NAT类型不支持或对方未在线）")
            return None
        except Exception as e:
            logger.error(f"P2P连接失败：{str(e)}")
            return None