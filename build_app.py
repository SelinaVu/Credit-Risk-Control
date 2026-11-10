import os
import sys
import PyInstaller.__main__

def build():
    # Xác định thư mục hiện tại
    base_path = os.path.dirname(os.path.abspath(__file__))
    app_script = os.path.join(base_path, "desktop_wrapper.py")
    streamlit_script = os.path.join(base_path, "fintrust_app.py")
    
    # Định dạng dấu phân cách tài nguyên (; trên Windows, : trên macOS)
    separator = ";" if sys.platform == "win32" else ":"
    
    # Cấu hình các tham số cho PyInstaller
    args = [
        app_script,
        "--name=Fintrust_EWS",
        "--onefile",       # Đóng gói thành 1 file .exe duy nhất
        "--windowed",      # Chạy ẩn console (không hiển thị cửa sổ cmd đen)
        f"--add-data={streamlit_script}{separator}.", # Đính kèm file giao diện chính
        "--collect-all=webview",   # Thu thập toàn bộ tài nguyên của pywebview
        "--collect-all=streamlit", # Thu thập toàn bộ tài nguyên của streamlit
        "--copy-metadata=streamlit", # Thu thập metadata của streamlit phục vụ chạy run
        "--exclude-module=PySide6", # Loại trừ PySide6 tránh xung đột Qt
        "--exclude-module=PyQt5",   # Loại trừ PyQt5 tránh xung đột Qt
        "--exclude-module=PyQt6",   # Loại trừ PyQt6 tránh xung đột Qt
        "--exclude-module=PySide2",  # Loại trừ PySide2 tránh xung đột Qt
        "--clean",         # Xóa cache build cũ
    ]
    
    print(f"Khởi chạy PyInstaller với các tham số: {args}")
    PyInstaller.__main__.run(args)
    print("Đóng gói thành công! File cài đặt nằm trong thư mục 'dist/'.")

if __name__ == "__main__":
    build()
