import os
import sys
import time
import socket
import threading
import streamlit.web.cli as stcli
import webview

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_streamlit(app_path, port):
    # Thay đổi sys.argv để streamlit nhận diện đối số
    sys.argv = [
        "streamlit", "run",
        app_path,
        "--server.port", str(port),
        "--server.headless", "true",
        "--global.developmentMode", "false"
    ]
    try:
        stcli.main()
    except SystemExit:
        pass

def main():
    # 1. Tìm cổng trống để chạy local server
    port = find_free_port()
    url = f"http://localhost:{port}"
    
    # 2. Tìm đường dẫn file ứng dụng
    if hasattr(sys, '_MEIPASS'):
        # Chạy trong môi trường đóng gói PyInstaller
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    app_path = os.path.join(base_path, "fintrust_app.py")
    
    # Thiết lập biến môi trường chứa thư mục gốc thực tế của file exe để fintrust_app.py lưu database cục bộ
    if hasattr(sys, 'frozen'):
        real_exe_dir = os.path.dirname(sys.executable)
    else:
        real_exe_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["FINTRUST_EXE_DIR"] = real_exe_dir
    
    print(f"Starting Streamlit backend on port {port}...")
    
    # Khởi chạy streamlit trong luồng con (Thread) thay vì subprocess để tránh lỗi vòng lặp fork-bomb của exe
    t = threading.Thread(target=run_streamlit, args=(app_path, port))
    t.daemon = True
    t.start()
    
    # 3. Đợi cổng local server hoạt động
    connected = False
    for _ in range(30):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect(("localhost", port))
            s.close()
            connected = True
            break
        except Exception:
            time.sleep(0.5)
            
    if not connected:
        print("Failed to connect to Streamlit server.")
        sys.exit(1)
        
    # 4. Khởi chạy cửa sổ PyWebView Desktop
    print("Launching PyWebView frontend...")
    window = webview.create_window(
        title="FinTrust - Hệ thống Đánh giá Rủi ro Thông qua Phân tích Tài chính từ BCTC",
        url=url,
        width=1280,
        height=820,
        resizable=True
    )
    
    # Chạy giao diện desktop
    webview.start()
    print("Exiting application...")

if __name__ == "__main__":
    main()
