import platform
import pyautogui
from pyremote.platform.windows import WindowsInput
from pyremote.platform.macos import MacOSInput
from pyremote.platform.linux import LinuxInput

# 初始化PyAutoGUI配置（防故障安全设置）
pyautogui.FAILSAFE = True  # 鼠标移到屏幕角落时停止操作
pyautogui.PAUSE = 0.01  # 每次操作后短暂延迟，避免系统卡顿


class InputControl:
    """跨平台鼠标键盘控制（自动适配系统）"""
    def __init__(self):
        self.platform = platform.system().lower()
        # 初始化平台专属控制实现
        self.input_impl = self._get_platform_impl()
        # 获取屏幕分辨率（用于坐标适配）
        self.screen_width, self.screen_height = pyautogui.size()

    def _get_platform_impl(self):
        """根据系统选择对应控制实现"""
        if self.platform == "windows":
            return WindowsInput()
        elif self.platform == "darwin":  # macOS
            return MacOSInput()
        elif self.platform == "linux":
            return LinuxInput()
        else:
            raise Exception(f"不支持的平台：{self.platform}")

    def move_mouse(self, x, y, relative=False):
        """
        移动鼠标
        :param x: 目标X坐标（绝对坐标/相对偏移）
        :param y: 目标Y坐标（绝对坐标/相对偏移）
        :param relative: True=相对当前位置，False=绝对屏幕坐标
        """
        try:
            if relative:
                pyautogui.moveRel(x, y, duration=0.05)  # 相对移动，0.05秒平滑过渡
            else:
                # 确保坐标在屏幕范围内（防越界）
                x = max(0, min(x, self.screen_width - 1))
                y = max(0, min(y, self.screen_height - 1))
                pyautogui.moveTo(x, y, duration=0.05)
            return True
        except Exception as e:
            print(f"鼠标移动失败：{str(e)}")
            return False

    def click_mouse(self, button="left", double=False):
        """
        鼠标点击
        :param button: 按键类型（left=左键，right=右键，middle=中键）
        :param double: True=双击，False=单击
        """
        try:
            if double:
                pyautogui.doubleClick(button=button)
            else:
                pyautogui.click(button=button)
            return True
        except Exception as e:
            print(f"鼠标点击失败：{str(e)}")
            return False

    def scroll_mouse(self, direction="up", amount=1):
        """
        鼠标滚动
        :param direction: 滚动方向（up=上滚，down=下滚）
        :param amount: 滚动幅度（默认1，越大滚动越快）
        """
        try:
            scroll_amount = amount if direction == "up" else -amount
            pyautogui.scroll(scroll_amount)
            return True
        except Exception as e:
            print(f"鼠标滚动失败：{str(e)}")
            return False

    def press_key(self, key):
        """
        单个按键按下（支持组合键，用'+'连接，如'ctrl+c'）
        :param key: 按键名称（参考pyautogui键位表，如'a'、'enter'、'ctrl'）
        """
        try:
            # 处理组合键（如'ctrl+v'拆分为['ctrl', 'v']）
            if '+' in key:
                key_list = key.split('+')
                with pyautogui.hold(key_list[:-1]):  # 按住组合键前缀（如ctrl）
                    pyautogui.press(key_list[-1])     # 按下目标键（如v）
            else:
                pyautogui.press(key)
            return True
        except Exception as e:
            print(f"按键按下失败：{str(e)}")
            return False

    def type_text(self, text, interval=0.05):
        """
        输入文本
        :param text: 要输入的字符串
        :param interval: 每个字符的输入间隔（默认0.05秒，避免输入过快）
        """
        try:
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception as e:
            print(f"文本输入失败：{str(e)}")
            return False


# 平台专属实现（以Linux为例，解决特殊权限/接口差异）
# pyremote/platform/linux.py
class LinuxInput:
    def __init__(self):
        # Linux下需要额外处理X11权限（针对屏幕控制）
        self._check_x11_permission()

    def _check_x11_permission(self):
        """检查Linux X11显示权限（避免屏幕控制失败）"""
        import os
        if "DISPLAY" not in os.environ:
            raise Exception("Linux环境缺少DISPLAY变量，无法控制输入（需X11服务）")
        # 可选：检查xhost权限（允许当前用户访问X11）
        try:
            import subprocess
            subprocess.run(["xhost", "+SI:localuser:$USER"], check=True, capture_output=True)
        except Exception as e:
            print(f"X11权限配置警告：{str(e)}（可能影响输入控制）")

# Windows/macOS平台实现（基础功能与PyAutoGUI兼容，可扩展特殊功能）
# pyremote/platform/windows.py
class WindowsInput:
    def __init__(self):
        # Windows下可扩展：如支持虚拟按键码（VK_CODE）
        self.vk_codes = {
            "ctrl": 0x11,
            "alt": 0x12,
            "shift": 0x10,
            "enter": 0x0D
        }

# pyremote/platform/macos.py
class MacOSInput:
    def __init__(self):
        # macOS下特殊处理：如F1-F12按键需要按住fn键
        self.fn_required_keys = ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"]