import platform
from PIL import ImageGrab, Image
from pyremote.platform.windows import WindowsScreen
from pyremote.platform.macos import MacOSScreen
from pyremote.platform.linux import LinuxScreen

class ScreenCapture:
    """跨平台屏幕捕获（自动适配系统）"""
    def __init__(self):
        self.platform = platform.system().lower()
        # 初始化对应平台的捕获实现
        self.screen_impl = self._get_platform_impl()

    def _get_platform_impl(self):
        """获取平台-specific实现"""
        if self.platform == "windows":
            return WindowsScreen()
        elif self.platform == "darwin":  # macOS
            return MacOSScreen()
        elif self.platform == "linux":
            return LinuxScreen()
        else:
            raise Exception(f"不支持的平台：{self.platform}")

    def capture_full_screen(self):
        """捕获全屏"""
        try:
            # 调用平台-specific方法
            img = self.screen_impl.capture_full()
            # 压缩图像（降低传输带宽）
            return self._compress_image(img)
        except Exception as e:
            print(f"全屏捕获失败：{str(e)}")
            return None

    def capture_region(self, x, y, width, height):
        """捕获指定区域（x,y: 左上角坐标）"""
        try:
            img = self.screen_impl.capture_region(x, y, width, height)
            return self._compress_image(img)
        except Exception as e:
            print(f"区域捕获失败：{str(e)}")
            return None

    def _compress_image(self, img, quality=60):
        """压缩图像（JPEG格式）"""
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # 内存中保存为JPEG
        import io
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG", quality=quality)
        return img_byte_arr.getvalue()

# 平台-specific实现（以Windows为例，其他平台类似）
# pyremote/platform/windows.py
class WindowsScreen:
    def capture_full(self):
        """Windows全屏捕获（Pillow+Windows API）"""
        return ImageGrab.grab(all_screens=True)  # 支持多屏幕

    def capture_region(self, x, y, width, height):
        """Windows区域捕获"""
        bbox = (x, y, x + width, y + height)
        return ImageGrab.grab(bbox=bbox)