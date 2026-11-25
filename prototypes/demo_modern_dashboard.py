"""
FinTrust EWS v2.1 - Entry point tương thích cho đường dẫn cũ prototypes/demo_modern_dashboard.py.
Tự động điều hướng sang giao diện chính thức ở thư mục gốc (streamlit_app.py) để đảm bảo đồng bộ mã nguồn.
"""

import os
import runpy
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

runpy.run_path(os.path.join(ROOT_DIR, "streamlit_app.py"), run_name="__main__")
