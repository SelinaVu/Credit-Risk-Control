# -*- coding: utf-8 -*-
"""
test_streamlit_app.py
---------------------
Kiểm thử kịch bản giao diện (Headless UI Scenario Testing) bằng Streamlit AppTest cho:
1. streamlit_app.py (FinTrust EWS v2.1 Enterprise - quy trình 5 bước & Team Passcode)
2. fintrust_app.py (Ứng dụng phân tích sâu BCTC & EWS - smoke test khởi động)
"""

import os
import pytest
from streamlit.testing.v1 import AppTest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STREAMLIT_APP_PATH = os.path.join(ROOT_DIR, "streamlit_app.py")
FINTRUST_APP_PATH = os.path.join(ROOT_DIR, "fintrust_app.py")


@pytest.mark.slow
def test_streamlit_app_boots_cleanly_without_passcode(isolated_cloud_db):
    """Kịch bản 1: Mở ứng dụng lần đầu ở chế độ không mật khẩu -> không có bất kỳ exception nào."""
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception, f"App bị lỗi khi khởi động: {at.exception}"
    assert at.session_state["profile_loaded"] is False


@pytest.mark.slow
def test_team_passcode_gate_blocks_wrong_and_accepts_right_code(isolated_cloud_db, monkeypatch):
    """Kịch bản 2: Bật Team Passcode -> nhập sai bị chặn, nhập đúng mở khóa & lưu tên CBTD."""
    monkeypatch.setenv("FINTRUST_TEAM_PASSCODE", "BankTest2026")
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
    assert at.session_state["team_authenticated"] is False

    # Nhập sai mật khẩu
    at.text_input[0].set_value("Nguyễn Tùng (VN)")
    at.text_input[1].set_value("SaiMatKhau")
    at.button[0].click().run()
    assert not at.exception
    assert at.session_state["team_authenticated"] is False
    assert any("chưa chính xác" in e.value for e in at.error)

    # Nhập đúng mật khẩu
    at.text_input[0].set_value("Nguyễn Tùng (VN)")
    at.text_input[1].set_value("BankTest2026")
    at.button[0].click().run()
    assert not at.exception
    assert at.session_state["team_authenticated"] is True
    assert at.session_state["operator_name"] == "Nguyễn Tùng (VN)"


@pytest.mark.slow
def test_guardrail_blocks_steps_2_to_5_before_loading_profile(isolated_cloud_db):
    """Kịch bản 3: Chưa nạp hồ sơ nhưng chuyển thẳng sang Bước 2..5 -> hiển thị cảnh báo sạch, không crash."""
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    step_options = [
        "2. Rà Soát Tài Chính & CCC",
        "3. Ma Trận Cảnh Báo Sớm EWS",
        "4. Khảo Sát Định Tính 5Cs & Hybrid",
        "5. Nhu Cầu Vay Vốn & Tờ Trình",
    ]
    # Kiểm tra nút điều hướng segmented_control nếu tồn tại
    if hasattr(at, "segmented_control") and len(at.segmented_control) > 0:
        for label in step_options:
            at.segmented_control[0].set_value(label).run()
            assert not at.exception, f"Crash khi mở '{label}' lúc chưa có hồ sơ: {at.exception}"
            assert any("chưa nạp hồ sơ" in w.value.lower() for w in at.warning)


@pytest.mark.slow
def test_full_5_step_credit_appraisal_workflow(isolated_cloud_db):
    """
    Kịch bản 4 (E2E trọng tâm): Đi trọn quy trình 5 bước của CBTD:
    Bước 1: Nạp hồ sơ mẫu FPT -> Lưu Audit Trail vào CSDL cô lập
    Bước 2: Xem Chu kỳ tiền mặt CCC & 5 tab định lượng
    Bước 3: Xem Ma trận EWS & 22 biến kiểm soát
    Bước 4: Chấm điểm 5Cs, đổi tỷ trọng ĐL/ĐT, lưu hồ sơ
    Bước 5: Tính nhu cầu VLĐ, kiểm tra cảnh báo LTV vượt trần, tạo Tờ trình PDF
    """
    db_cloud, _ = isolated_cloud_db
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    # Bước 1: Bấm nút "⚡ Nạp hồ sơ mẫu FPT"
    load_btn = next((b for b in at.button if "Nạp hồ sơ mẫu" in b.label), None)
    assert load_btn is not None, "Không tìm thấy nút Nạp hồ sơ mẫu ở Bước 1"
    load_btn.click().run()
    assert not at.exception, f"Lỗi khi nạp hồ sơ mẫu: {at.exception}"
    assert at.session_state["profile_loaded"] is True
    assert at.session_state["active_company"]["ticker"] == "FPT"

    # Quay lại Bước 1 để test nút Lưu vết Audit Trail & Cân đối nguồn vốn
    if hasattr(at, "segmented_control") and len(at.segmented_control) > 0:
        at.segmented_control[0].set_value("1. Nạp BCTC & Hồ Sơ").run()
        assert not at.exception

        save_btn = next((b for b in at.button if "Lưu Vết" in b.label), None)
        assert save_btn is not None
        save_btn.click().run()
        assert not at.exception
        # Xác nhận đã ghi vào SQLite cô lập và thông báo lưu vết vẫn hiển thị sau st.rerun()
        assert len(db_cloud.list_saved_companies()) == 1
        assert any("Đã lưu hồ sơ" in s.value or "đồng bộ" in s.value for s in at.success)

        # Bước 2
        at.segmented_control[0].set_value("2. Rà Soát Tài Chính & CCC").run()
        assert not at.exception

        # Bước 3
        at.segmented_control[0].set_value("3. Ma Trận Cảnh Báo Sớm EWS").run()
        assert not at.exception

        # Bước 4: Đổi tiêu chí C1 và lưu điểm 5Cs
        at.segmented_control[0].set_value("4. Khảo Sát Định Tính 5Cs & Hybrid").run()
        assert not at.exception
        save_5c_btn = next((b for b in at.button if "Lưu Điểm Định Tính 5Cs" in b.label), None)
        assert save_5c_btn is not None
        save_5c_btn.click().run()
        assert not at.exception

        # Bước 5: Kiểm tra tạo PDF không bị st.error
        at.segmented_control[0].set_value("5. Nhu Cầu Vay Vốn & Tờ Trình").run()
        assert not at.exception
        pdf_errors = [e.value for e in at.error if "Lỗi tạo tệp PDF" in e.value]
        assert not pdf_errors, f"Bước 5 bị lỗi khi tạo PDF: {pdf_errors}"

        # Kiểm tra kịch bản LTV vượt trần: đặt Hạn mức đề xuất rất cao (500 tỷ) > TSBĐ (390 tỷ)
        prop_input = next(
            (n for n in at.number_input if "Hạn mức tín dụng đề xuất" in n.label), None
        )
        assert prop_input is not None
        prop_input.set_value(500.0).run()
        assert not at.exception
        assert any("VƯỢT KHUNG" in e.value for e in at.error)

        # Kiểm tra kịch bản biên: Tổng chi phí rất thấp (5 tỷ) và vòng quay rất cao (50 vòng/năm) -> total_nwc = 0.1
        cost_input = next(
            (n for n in at.number_input if "Tổng chi phí hoạt động" in n.label), None
        )
        wctr_input = next(
            (n for n in at.number_input if "Số vòng quay Vốn lưu động" in n.label), None
        )
        cost_input.set_value(5.0)
        wctr_input.set_value(50.0)
        at.run()
        assert not at.exception, f"Crash ở Bước 5 khi total_nwc rất nhỏ (0.1 tỷ): {at.exception}"


@pytest.mark.slow
def test_step5_pdf_with_special_xml_chars_in_company_name(isolated_cloud_db):
    """Kịch bản 5: Doanh nghiệp có tên chứa ký tự '&' (rất phổ biến ở VN: 'Thương mại & Dịch vụ') tại Bước 5."""
    at = AppTest.from_file(STREAMLIT_APP_PATH, default_timeout=30)
    at.run()
    at.session_state["profile_loaded"] = True
    at.session_state["active_company"] = {
        "name": "CTCP Thương mại & Đầu tư Minh Phát <Group>",
        "ticker": "MPH",
        "industry": "Thương mại & Phân phối",
        "age": 12,
        "quant_score": 84.0,
    }
    at.run()
    if hasattr(at, "segmented_control") and len(at.segmented_control) > 0:
        at.segmented_control[0].set_value("5. Nhu Cầu Vay Vốn & Tờ Trình").run()
        assert not at.exception
        pdf_errors = [e.value for e in at.error if "Lỗi tạo tệp PDF" in e.value]
        assert not pdf_errors, f"Lỗi tạo PDF khi tên công ty chứa '&' hoặc '<': {pdf_errors}"


@pytest.mark.slow
def test_fintrust_app_legacy_boots_without_exception(tmp_path, monkeypatch):
    """Kịch bản 6: Smoke test ứng dụng fintrust_app.py khởi động sạch trên thư mục dữ liệu cô lập."""
    monkeypatch.setenv("FINTRUST_EXE_DIR", str(tmp_path))
    at = AppTest.from_file(FINTRUST_APP_PATH, default_timeout=45)
    at.run()
    assert not at.exception, f"fintrust_app.py bị lỗi khi khởi động: {at.exception}"
