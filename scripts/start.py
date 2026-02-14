#!/usr/bin/env python3
"""
统一启动脚本

功能：
- 启动后端 FastAPI 服务
- 启动前端静态文件服务
- 自动打开浏览器
- 支持 Windows 和 Linux/Mac
"""
import os
import sys
import subprocess
import time
import webbrowser
import platform

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 端口配置
BACKEND_PORT = 8765
FRONTEND_PORT = 3000

def check_port(port):
    """
    检查端口是否被占用
    """
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", port))
            return True
    except:
        return False

def start_backend():
    """
    启动后端服务
    """
    backend_dir = os.path.join(PROJECT_ROOT, "src", "web_app", "backend")
    os.chdir(backend_dir)
    
    print(f"[INFO] 启动后端服务在 http://localhost:{BACKEND_PORT}")
    cmd = [
        sys.executable, "-m", "uvicorn", "api_server:app",
        "--host", "0.0.0.0",
        "--port", str(BACKEND_PORT),
        "--reload"
    ]
    return subprocess.Popen(cmd)

def start_frontend():
    """
    启动前端服务
    """
    frontend_dir = os.path.join(PROJECT_ROOT, "src", "web_app", "frontend")
    os.chdir(frontend_dir)
    
    print(f"[INFO] 启动前端服务在 http://localhost:{FRONTEND_PORT}")
    
    if platform.system() == "Windows":
        cmd = [sys.executable, "-m", "http.server", str(FRONTEND_PORT)]
    else:
        cmd = ["python3", "-m", "http.server", str(FRONTEND_PORT)]
    
    return subprocess.Popen(cmd)

def main():
    """
    主函数
    """
    print("=" * 60)
    print("Comic-Crawler 启动脚本")
    print("=" * 60)
    
    # 检查端口
    if not check_port(BACKEND_PORT):
        print(f"[ERROR] 后端端口 {BACKEND_PORT} 被占用")
        return
    
    if not check_port(FRONTEND_PORT):
        print(f"[ERROR] 前端端口 {FRONTEND_PORT} 被占用")
        return
    
    # 启动服务
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    # 等待服务启动
    time.sleep(2)
    
    # 打开浏览器
    url = f"http://localhost:{FRONTEND_PORT}"
    print(f"[INFO] 打开浏览器: {url}")
    webbrowser.open(url)
    
    print("\n" + "=" * 60)
    print("服务启动成功！")
    print(f"后端: http://localhost:{BACKEND_PORT}")
    print(f"前端: http://localhost:{FRONTEND_PORT}")
    print("=" * 60)
    print("按 Ctrl+C 停止服务")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] 停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait(timeout=5)
        frontend_process.wait(timeout=5)
        print("[INFO] 服务已停止")

if __name__ == "__main__":
    main()
