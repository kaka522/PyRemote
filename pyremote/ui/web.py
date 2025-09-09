from flask import Flask, render_template, send_file, request, jsonify
import threading
import base64
import io
from pyremote.core.communication import TCPCommunication
from pyremote.core.screen_capture import ScreenCapture
from pyremote.core.input_control import InputControl
from pyremote.utils.logger import logger

# 全局Flask应用实例
web_app = Flask(__name__, template_folder="templates", static_folder="static")
# 核心模块全局实例（Web模式下共享）
web_comm = None
web_screen = None
web_input = None
# 屏幕截图定时任务（线程）
capture_thread = None
stop_capture = False
# 最新截图数据（Base64格式，供前端渲染）
latest_screenshot = "data:image/jpeg;base64,"


def _capture_screen_loop():
    """定时捕获屏幕（每秒1次，供Web前端实时显示）"""
    global latest_screenshot, stop_capture
    while not stop_capture:
        try:
            # 捕获全屏并转为Base64
            img_bytes = web_screen.capture_full_screen()
            if img_bytes:
                img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                latest_screenshot = f"data:image/jpeg;base64,{img_base64}"
            # 每秒1次（平衡流畅度和性能）
            import time
            time.sleep(1)
        except Exception as e:
            logger.error(f"屏幕捕获循环失败：{str(e)}")
            time.sleep(1)


@web_app.route("/")
def index():
    """Web界面首页（远程控制主界面）"""
    return render_template("index.html", initial_screenshot=latest_screenshot)


@web_app.route("/api/screenshot")
def api_screenshot():
    """API：获取最新屏幕截图（Base64）"""
    global latest_screenshot
    return jsonify({"screenshot": latest_screenshot})


@web_app.route("/api/mouse/move", methods=["POST"])
def api_mouse_move():
    """API：控制鼠标移动（接收JSON参数：x, y, relative）"""
    try:
        data = request.get_json()
        x = data.get("x", 0)
        y = data.get("y", 0)
        relative = data.get("relative", True)
        
        result = web_input.move_mouse(int(x), int(y), relative)
        return jsonify({"success": result})
    except Exception as e:
        logger.error(f"鼠标移动API失败：{str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@web_app.route("/api/mouse/click", methods=["POST"])
def api_mouse_click():
    """API：控制鼠标点击（接收JSON参数：button, double）"""
    try:
        data = request.get_json()
        button = data.get("button", "left")
        double = data.get("double", False)
        
        result = web_input.click_mouse(button=button, double=double)
        return jsonify({"success": result})
    except Exception as e:
        logger.error(f"鼠标点击API失败：{str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@web_app.route("/api/key/press", methods=["POST"])
def api_key_press():
    """API：控制按键按下（接收JSON参数：key）"""
    try:
        data = request.get_json()
        key = data.get("key", "")
        
        result = web_input.press_key(key)
        return jsonify({"success": result})
    except Exception as e:
        logger.error(f"按键API失败：{str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@web_app.route("/api/connect", methods=["POST"])
def api_connect():
    """API：连接远程设备（接收JSON参数：host, port）"""
    global web_comm
    try:
        data = request.get_json()
        host = data.get("host", "")
        port = int(data.get("port", 9999))
        
        if web_comm.is_connected:
            web_comm.close()
        
        result = web_comm.connect_client(host, port)
        return jsonify({"success": result})
    except Exception as e:
        logger.error(f"连接API失败：{str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@web_app.route("/api/disconnect", methods=["POST"])
def api_disconnect():
    """API：断开连接"""
    global web_comm
    try:
        web_comm.close()
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"断开API失败：{str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


def run_web(args):
    """启动Web模式（Flask服务+屏幕捕获线程）"""
    global web_comm, web_screen, web_input, capture_thread, stop_capture
    
    # 初始化核心模块
    web_comm = TCPCommunication()
    web_screen = ScreenCapture()
    web_input = InputControl()
    
    # 启动屏幕捕获线程
    stop_capture = False
    capture_thread = threading.Thread(target=_capture_screen_loop, daemon=True)
    capture_thread.start()
    logger.info("Web模式：屏幕捕获线程已启动")
    
    # 启动Flask服务（允许外部访问）
    logger.info(f"Web界面已启动：http://{args.host}:{args.port}")
    web_app.run(host=args.host, port=args.port, debug=False, use_reloader=False)
    
    # 服务停止后清理
    stop_capture = True
    if capture_thread.is_alive():
        capture_thread.join()
    web_comm.close()
    logger.info("Web模式：已停止")


 