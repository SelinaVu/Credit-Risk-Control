# -*- coding: utf-8 -*-
"""
test_database_cloud.py
----------------------
Kiểm thử lớp lưu trữ đa người dùng (src/core/database_cloud.py):
- Lưu / Đọc / Liệt kê hồ sơ và Nhật ký Audit Trail trên SQLite cô lập
- Tự động fallback từ Supabase lỗi sang SQLite không mất dữ liệu
- Xuất / Nhập Gói Hồ Sơ (.json) và chống file JSON lỗi
- Lọc cấu hình placeholder & kiểm thử Team Passcode
- Ghi đồng thời nhiều luồng (mô phỏng nhiều cán bộ trong team cùng lưu)
"""

from concurrent.futures import ThreadPoolExecutor
import json
import pytest


def test_save_list_load_roundtrip_with_audit_trail(isolated_cloud_db, sample_override_rows):
    db_cloud, _ = isolated_cloud_db
    company = {
        "ticker": "fpt ",
        "name": "CTCP FPT",
        "industry": "Công nghệ",
        "age": 15,
        "quant_score": 89.2,
    }
    qual = {"c1_mgmt_exp": {"group": "C1", "val": 80}}
    uw = {"rev_plan": 5000.0, "proposed_limit": 300.0}

    ok, msg = db_cloud.save_company_profile(
        company=company,
        bctc_override_data=sample_override_rows,
        qual_criteria=qual,
        quant_w_pct=65,
        underwriting_inputs=uw,
        operator="Nguyễn Tùng (VN)",
        year=2024,
    )
    assert ok is True
    assert "FPT" in msg

    saved_list = db_cloud.list_saved_companies()
    assert len(saved_list) == 1
    assert saved_list[0]["ticker"] == "FPT"
    assert saved_list[0]["updated_by"] == "Nguyễn Tùng (VN)"

    loaded = db_cloud.load_company_profile("fpt", year=2024)
    assert loaded is not None
    assert loaded["company"]["name"] == "CTCP FPT"
    assert loaded["quant_w_pct"] == 65
    assert loaded["underwriting_inputs"]["proposed_limit"] == 300.0
    assert len(loaded["bctc_override_data"]) == 2

    # Kiểm tra vết Audit Trail được giữ nguyên vẹn
    row_130 = next(r for r in loaded["bctc_override_data"] if r["Mã Số"] == "130")
    assert row_130["Số Gốc OCR (tỷ VNĐ)"] == 1950.0
    assert row_130["Số Áp Dụng (tỷ VNĐ)"] == 19500.0
    assert "Thuyết minh" in row_130["Lý Do Điều Chỉnh (Remark)"]
    assert row_130["Cán Bộ Thao Tác"] == "Nguyễn Tùng (VN)"


def test_save_rejects_empty_ticker(isolated_cloud_db, sample_override_rows):
    db_cloud, _ = isolated_cloud_db
    ok, msg = db_cloud.save_company_profile(
        company={"ticker": "   ", "name": "No Ticker"},
        bctc_override_data=sample_override_rows,
        qual_criteria={},
        quant_w_pct=60,
    )
    assert ok is False
    assert "ticker" in msg.lower()


def test_supabase_failure_auto_fallbacks_to_sqlite(isolated_cloud_db, monkeypatch, sample_override_rows):
    """Mô phỏng Supabase mất mạng giữa chừng -> hệ thống tự lưu an toàn vào SQLite không mất dữ liệu."""
    db_cloud, _ = isolated_cloud_db

    class BrokenSupabaseClient:
        def table(self, _name):
            raise ConnectionError("Simulated Supabase timeout")

    monkeypatch.setattr(db_cloud, "get_supabase_client", lambda: BrokenSupabaseClient())

    ok, msg = db_cloud.save_company_profile(
        company={"ticker": "VNM", "name": "Vinamilk", "industry": "FMCG", "age": 22, "quant_score": 86.8},
        bctc_override_data=sample_override_rows,
        qual_criteria={},
        quant_w_pct=60,
        operator="Selina (JP)",
    )
    assert ok is True
    assert "SQLite" in msg

    # Tắt client lỗi để kiểm tra dữ liệu thực sự đã nằm trong SQLite
    monkeypatch.setattr(db_cloud, "get_supabase_client", lambda: None)
    loaded = db_cloud.load_company_profile("VNM")
    assert loaded is not None
    assert loaded["company"]["name"] == "Vinamilk"


def test_json_package_export_import_and_corrupt_inputs(isolated_cloud_db, sample_override_rows):
    db_cloud, _ = isolated_cloud_db
    raw_str = db_cloud.export_profile_package_json(
        company={"ticker": "HPG", "name": "Hòa Phát", "industry": "Thép", "age": 18, "quant_score": 79.5},
        bctc_override_data=sample_override_rows,
        qual_criteria={"c1_mgmt_exp": {"group": "C1", "val": 100}},
        quant_w_pct=70,
        operator="Tester",
    )
    parsed = db_cloud.parse_profile_package_json(raw_str.encode("utf-8"))
    assert parsed["schema_version"] == "fintrust_ews_v2.1"
    assert parsed["company"]["ticker"] == "HPG"
    assert parsed["quant_w_pct"] == 70

    # File JSON thiếu trường company
    with pytest.raises(ValueError):
        db_cloud.parse_profile_package_json(json.dumps({"hello": "world"}).encode("utf-8"))

    # File JSON hỏng cú pháp
    with pytest.raises(Exception):
        db_cloud.parse_profile_package_json(b"{not-valid-json")

    # File không phải UTF-8
    with pytest.raises(UnicodeDecodeError):
        db_cloud.parse_profile_package_json(b"\xff\xfe\x00\x01")


def test_placeholder_credentials_are_ignored(monkeypatch):
    import src.core.database_cloud as db_cloud

    monkeypatch.setenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "YOUR_ANON_KEY")
    # Đảm bảo không đọc nhầm secrets thật khi kiểm tra env placeholder
    monkeypatch.setattr(db_cloud.st, "secrets", {})
    url, key = db_cloud._read_supabase_credentials()
    assert url is None and key is None

    monkeypatch.setenv("FINTRUST_TEAM_PASSCODE", "SecretTeam2026")
    assert db_cloud.get_team_passcode() == "SecretTeam2026"


def test_concurrent_multi_user_saves_no_sqlite_lock_crash(isolated_cloud_db, sample_override_rows):
    """Mô phỏng 8 cán bộ thẩm định lưu hồ sơ song song lên cùng một CSDL."""
    db_cloud, _ = isolated_cloud_db

    def _worker(idx: int):
        return db_cloud.save_company_profile(
            company={
                "ticker": f"CORP{idx}",
                "name": f"Doanh nghiệp Thử nghiệm {idx}",
                "industry": "Sản xuất",
                "age": 5 + idx,
                "quant_score": 75.0 + idx,
            },
            bctc_override_data=sample_override_rows,
            qual_criteria={"c1_mgmt_exp": {"group": "C1", "val": 80}},
            quant_w_pct=60,
            operator=f"CBTD_{idx}",
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(_worker, range(8)))

    assert all(ok for ok, _ in results)
    saved = db_cloud.list_saved_companies()
    assert len(saved) == 8


def test_supabase_auth_helpers_offline_and_validation(isolated_cloud_db):
    """Kiểm tra helper xác thực Supabase Auth khi offline và validate đầu vào."""
    db_cloud, _ = isolated_cloud_db
    assert db_cloud.is_supabase_auth_active() is False
    assert db_cloud.list_team_users() == []

    ok, info, msg = db_cloud.authenticate_supabase_user("", "")
    assert ok is False and info == {} and "Email" in msg

    ok_pw, msg_pw = db_cloud.change_supabase_password("tok", "ref", "short")
    assert ok_pw is False and "8" in msg_pw

    ok_rst, msg_rst = db_cloud.send_supabase_password_reset("invalid-email")
    assert ok_rst is False and "hợp lệ" in msg_rst
