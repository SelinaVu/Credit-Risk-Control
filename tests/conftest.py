# -*- coding: utf-8 -*-
"""
conftest.py
-----------
Các fixture dùng chung cho bộ kiểm thử FinTrust EWS.
Đảm bảo toàn bộ test chạy trên cơ sở dữ liệu tạm cô lập, tuyệt đối không làm bẩn dữ liệu thật của team.
"""

import os
import sys
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


@pytest.fixture
def isolated_cloud_db(tmp_path, monkeypatch):
    """Cô lập SQLite của database_cloud vào thư mục tạm và tắt kết nối Supabase thật."""
    import src.core.database_cloud as db_cloud

    temp_db = str(tmp_path / "test_fintrust_cloud_cache.db")
    monkeypatch.setattr(db_cloud, "DEFAULT_SQLITE_PATH", temp_db)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("FINTRUST_TEAM_PASSCODE", raising=False)
    monkeypatch.setattr(db_cloud, "_read_supabase_credentials", lambda: (None, None))
    return db_cloud, temp_db


@pytest.fixture
def sample_extracted_data_vnd():
    """Dữ liệu BCTC chuẩn 2 năm (đơn vị: VNĐ) phục vụ test engine thẩm định và xuất PDF."""
    return {
        2023: {
            "Total_Assets": 60_500_000_000_000.0,
            "Current_Assets": 36_100_000_000_000.0,
            "Cash_Equivalents": 15_400_000_000_000.0,
            "Accounts_Receivable": 16_800_000_000_000.0,
            "Current_Receivables": 16_800_000_000_000.0,
            "Inventories": 7_500_000_000_000.0,
            "Total_Liabilities": 30_100_000_000_000.0,
            "Current_Liabilities": 25_200_000_000_000.0,
            "Short_Term_Debt": 12_500_000_000_000.0,
            "Payables": 8_200_000_000_000.0,
            "Equity": 30_400_000_000_000.0,
            "Retained_Earnings": 11_000_000_000_000.0,
            "Net_Sales": 52_600_000_000_000.0,
            "COGS": 32_800_000_000_000.0,
            "Gross_Profit": 19_800_000_000_000.0,
            "Interest_Expense": 1_050_000_000_000.0,
            "EBT": 6_900_000_000_000.0,
            "Net_Income": 5_600_000_000_000.0,
            "OCF": 8_900_000_000_000.0,
        },
        2024: {
            "Total_Assets": 72_000_000_000_000.0,
            "Current_Assets": 45_000_000_000_000.0,
            "Cash_Equivalents": 18_200_000_000_000.0,
            "Accounts_Receivable": 19_500_000_000_000.0,
            "Current_Receivables": 19_500_000_000_000.0,
            "Inventories": 8_200_000_000_000.0,
            "Total_Liabilities": 34_900_000_000_000.0,
            "Current_Liabilities": 29_400_000_000_000.0,
            "Short_Term_Debt": 15_200_000_000_000.0,
            "Payables": 9_400_000_000_000.0,
            "Equity": 37_100_000_000_000.0,
            "Retained_Earnings": 14_200_000_000_000.0,
            "Net_Sales": 62_800_000_000_000.0,
            "COGS": 38_900_000_000_000.0,
            "Gross_Profit": 23_900_000_000_000.0,
            "Interest_Expense": 1_120_000_000_000.0,
            "EBT": 8_200_000_000_000.0,
            "Net_Income": 6_100_000_000_000.0,
            "OCF": 10_500_000_000_000.0,
        },
    }


@pytest.fixture
def sample_ews_results():
    """Kết quả EWS chuẩn theo định dạng EWS_NAMES_VN cho pdf_report_generator và engine."""
    return {
        2023: {
            "Altman_Z_Prime": {"score": 3.85, "status": "normal"},
            "Beneish_M_Score": {"score": -2.75, "status": "normal"},
            "Dechow_F_Score": {"score": 0.72, "status": "normal"},
            "Abnormal_CFO": {"score": 0.03, "status": "normal"},
            "Abnormal_PROD": {"score": -0.02, "status": "normal"},
            "Abnormal_DISEXP": {"score": 0.01, "status": "normal"},
        },
        2024: {
            "Altman_Z_Prime": {"score": 4.18, "status": "normal"},
            "Beneish_M_Score": {"score": -2.92, "status": "normal"},
            "Dechow_F_Score": {"score": 0.65, "status": "normal"},
            "Abnormal_CFO": {"score": 0.045, "status": "normal"},
            "Abnormal_PROD": {"score": -0.012, "status": "normal"},
            "Abnormal_DISEXP": {"score": 0.008, "status": "normal"},
        },
    }


@pytest.fixture
def sample_override_rows():
    """Dữ liệu bảng Audit Trail mẫu có cả dòng giữ nguyên OCR và dòng hiệu chỉnh tay."""
    return [
        {
            "Mã Số": "110",
            "Khoản Mục Kế Toán": "Tiền và tương đương tiền",
            "Số Gốc OCR (tỷ VNĐ)": 18200.0,
            "Số Áp Dụng (tỷ VNĐ)": 18200.0,
            "Lý Do Điều Chỉnh (Remark)": "",
        },
        {
            "Mã Số": "130",
            "Khoản Mục Kế Toán": "Các khoản phải thu ngắn hạn",
            "Số Gốc OCR (tỷ VNĐ)": 1950.0,
            "Số Áp Dụng (tỷ VNĐ)": 19500.0,
            "Lý Do Điều Chỉnh (Remark)": "Đối chiếu trang 14 Thuyết minh BCTC",
        },
    ]
