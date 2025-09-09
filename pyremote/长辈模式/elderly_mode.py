import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
from pyremote.core.communication import TCPCommunication
from pyremote.core.screen_capture import ScreenCapture
from pyremote.core.input_control import InputControl
from pyremote.utils.logger import logger

# 初始化语音引擎（用于语音提示）
try:
    tts_engine = pyttsx3.init()
    # 配置语音参数（语速、音量）
    tts_engine.setProperty('rate', 150)  # 语速：150词/分钟（默认200， slower更适合长辈）
    tts_engine.setProperty('volume', 1.0)  # 音量：0.0-1.0
except Exception as e:
    logger.warning(f"语音引擎初始化失败：{str(e)}（长辈模式将无语音提示）")
    tts_engine = None


def speak_text(text):
    """语音朗读文本（长辈模式核心功能）"""
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"语音朗读失败：{str(e)}")


class ElderlyModeGUI:
    """长辈模式GUI（简化界面、放大按钮、语音提示）"""
    def __init__(self, root, args):
        self.root = root
        self.args = args
        self.root.title("PyRemote 长辈模式")
        self.root.geometry("800x600")  # 大窗口，适合长辈操作
        self.root.resizable(False, False)  # 禁止缩放（避免误操作）
        
        # 核心模块初始化
        self.comm = TCPCommunication()
        self.screen_capture = ScreenCapture()
        self.input_control = InputControl()
        
        # 连接状态标记
        self.is_connected = False
        
        # 构建界面
        self._build_ui()
        # 初始语音提示
        speak_text("欢迎使用PyRemote长辈模式，请点击连接按钮开始")

    def _build_ui(self):
        """构建简化界面（分3个区域：连接区、控制区、状态区）"""
        # 1. 连接区域（顶部，大按钮+简单输入）
        connect_frame = ttk.Frame(self.root, padding=20)
        connect_frame.pack(fill=tk.X)
        
        ttk.Label(connect_frame, text="对方电脑地址（IP:端口）", font=("微软雅黑", 14)).grid(row=0, column=0, padx=10, pady=10)
        self.peer_addr_entry = ttk.Entry(connect_frame, font=("微软雅黑", 14), width=30)
        self.peer_addr_entry.grid(row=0, column=1, padx=10, pady=10)
        self.peer_addr_entry.insert(0, self.args.client if self.args.client else "")  # 预填命令行参数
        
        # 连接/断开按钮（大尺寸，红色/绿色区分）
        self.connect_btn = ttk.Button(connect_frame, text="连接对方电脑", command=self._toggle_connect,
                                     style="Elder.TButton", width=20)
        self.connect_btn.grid(row=0, column=2, padx=10, pady=10)

        # 2. 控制区域（中间，大按钮+明确图标文字）
        control_frame = ttk.Frame(self.root, padding=20)
        control_frame.pack(fill=tk.BOTH, expand=True)
        
        # 鼠标控制按钮（4个方向+点击）
        ttk.Button(control_frame, text="↑ 上移鼠标", command=lambda: self._control_mouse(0, -50),
                   style="Elder.TButton", width=15).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="← 左移鼠标", command=lambda: self._control_mouse(-50, 0),
                   style="Elder.TButton", width=15).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="→ 右移鼠标", command=lambda: self._control_mouse(50, 0),
                   style="Elder.TButton", width=15).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(control_frame, text="↓ 下移鼠标", command=lambda: self._control_mouse(0, 50),
                   style="Elder.TButton", width=15).grid(row=2, column=1, padx=5, pady=5)
        
        # 鼠标点击/滚动按钮
        ttk.Button(control_frame, text="左键单击", command=lambda: self._control_click("left"),
                   style="Elder.TButton", width=15).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="右键单击", command=lambda: self._control_click("right"),
                   style="Elder.TButton", width=15).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="↑ 滚动页面", command=lambda: self._control_scroll("up"),
                   style="Elder.TButton", width=15).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="↓ 滚动页面", command=lambda: self._control_scroll("down"),
                   style="Elder.TButton", width=15).grid(row=3, column=2, padx=5, pady=5)
        
        # 常用按键按钮（确定、返回、复制、粘贴）
        ttk.Button(control_frame, text="按 确定键", command=lambda: self._control_key("enter"),
                   style="Elder.TButton", width=15).grid(row=4, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="按 返回键", command=lambda: self._control_key("backspace"),
                   style="Elder.TButton", width=15).grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="复制（Ctrl+C）", command=lambda: self._control_key("ctrl+c"),
                   style="Elder.TButton", width=15).grid(row=4, column=2, padx=5, pady=5)
        ttk.Button(control_frame, text="粘贴（Ctrl+V）", command=lambda: self._control_key("ctrl+v"),
                   style="Elder.TButton", width=15).grid(row=4, column=3, padx=5, pady=5)

        # 3. 状态区域（底部，大字体显示连接状态）
        status_frame = ttk.Frame(self.root, padding=10)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="未连接 - 请输入对方地址并点击连接", 
                                     font=("微软雅黑", 14), foreground="red")
        self.status_label.pack()

        # 配置按钮样式（放大字体、增加内边距）
        self.root.style = ttk.Style()
        self.root.style.configure("Elder.TButton", font=("微软雅黑", 14), padding=15)

    def _toggle_connect(self):
        """切换连接状态（连接/断开）"""
        if not self.is_connected:
            # 连接操作
            peer_addr = self.peer_addr_entry.get().strip()
            if not peer_addr or ":" not in peer_addr:
                messagebox.showwarning("输入错误", "请输入正确的对方地址（格式：IP:端口）")
                speak_text("输入错误，请输入正确的对方地址，格式是IP冒号端口")
                return
            
            peer_ip, peer_port = peer_addr.split(":")
            peer_port = int(peer_port)
            
            # 发起连接（带语音提示）
            speak_text(f"正在连接{peer_ip}，请稍候")
            self.status_label.config(text=f"正在连接：{peer_ip}:{peer_port}", foreground="orange")
            
            # 异步连接（避免阻塞GUI）
            import threading
            threading.Thread(target=self._do_connect, args=(peer_ip, peer_port), daemon=True).start()
        else:
            # 断开操作
            self.comm.close()
            self.is_connected = False
            self.connect_btn.config(text="连接对方电脑")
            self.status_label.config(text="已断开连接", foreground="red")
            speak_text("已断开连接")

    def _do_connect(self, peer_ip, peer_port):
        """实际执行连接（异步）"""
        if self.comm.connect_client(peer_ip, peer_port):
            self.is_connected = True
            self.connect_btn.config(text="断开连接")
            self.status_label.config(text=f"已连接：{peer_ip}:{peer_port}", foreground="green")
            speak_text(f"连接成功，现在可以控制对方电脑了")
            
            # 注册数据接收回调（如接收对方屏幕截图）
            self.comm.on_data_received = self._on_data_received
        else:
            self.status_label.config(text="连接失败，请检查地址或对方是否在线", foreground="red")
            speak_text("连接失败，请检查对方地址是否正确，或者对方是否已经打开软件")

    def _control_mouse(self, dx, dy):
        """控制鼠标移动（长辈模式简化：固定相对偏移50像素）"""
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接对方电脑再进行控制")
            speak_text("未连接，请先连接对方电脑")
            return
        self.input_control.move_mouse(dx, dy, relative=True)
        speak_text("鼠标已移动")

    def _control_click(self, button):
        """控制鼠标点击"""
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接对方电脑再进行控制")
            speak_text("未连接，请先连接对方电脑")
            return
        self.input_control.click_mouse(button=button)
        speak_text(f"{button}键已点击")

    def _control_scroll(self, direction):
        """控制鼠标滚动"""
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接对方电脑再进行控制")
            speak_text("未连接，请先连接对方电脑")
            return
        self.input_control.scroll_mouse(direction=direction, amount=3)  # 放大滚动幅度
        speak_text(f"页面{direction}滚动")

    def _control_key(self, key):
        """控制按键输入"""
        if not self.is_connected:
            messagebox.showwarning("未连接", "请先连接对方电脑再进行控制")
            speak_text("未连接，请先连接对方电脑")
            return
        self.input_control.press_key(key)
        speak_text(f"已按下{key}键")

    def _on_data_received(self, data_type, data):
        """接收对方数据的回调（如屏幕截图）"""
        # 此处可扩展：显示对方屏幕截图（长辈模式可简化为弹窗显示）
        if data_type == 1:  # 约定1=屏幕截图数据
            logger.info("收到对方屏幕截图，大小：{len(data)}字节")
            # 可选：用PIL显示图片
            from PIL import Image, ImageTk
            import io
            
            try:
                img = Image.open(io.BytesIO(data))
                img.thumbnail((600, 400))  # 缩小图片适配窗口
                img_tk = ImageTk.PhotoImage(img)
                
                # 创建临时窗口显示截图
                img_window = tk.Toplevel(self.root)
                img_window.title("对方电脑屏幕")
                img_label = ttk.Label(img_window, image=img_tk)
                img_label.image = img_tk  # 防止GC回收
                img_label.pack()
                speak_text("收到对方屏幕截图")
            except Exception as e:
                logger.error(f"显示屏幕截图失败：{str(e)}")


def run_elderly_mode(args):
    """启动长辈模式"""
    root = tk.Tk()
    app = ElderlyModeGUI(root, args)
    root.mainloop()