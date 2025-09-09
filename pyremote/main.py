import argparse
from pyremote.ui.cli import run_cli
from pyremote.ui.gui import run_gui
from pyremote.ui.web import run_web
from pyremote.长辈模式.elderly_mode import run_elderly_mode
from pyremote.utils.logger import init_logger

def main():
    # 初始化日志
    init_logger()
    
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="PyRemote - 轻量级跨平台远程控制工具")
    parser.add_argument("--mode", choices=["cli", "gui", "web", "elderly"], 
                        default="gui", help="运行模式（cli:命令行, gui:桌面界面, web:Web界面, elderly:长辈模式）")
    parser.add_argument("--host", default="0.0.0.0", help="服务端IP（仅服务端模式）")
    parser.add_argument("--port", type=int, default=9999, help="服务端端口（仅服务端模式）")
    parser.add_argument("--client", help="客户端连接地址（格式：IP:端口，仅客户端模式）")
    
    args = parser.parse_args()
    
    # 启动对应模式
    if args.mode == "cli":
        run_cli(args)
    elif args.mode == "gui":
        run_gui(args)
    elif args.mode == "web":
        run_web(args)
    elif args.mode == "elderly":
        run_elderly_mode(args)

if __name__ == "__main__":
    main()