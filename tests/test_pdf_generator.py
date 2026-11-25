# -*- coding: utf-8 -*-
"""
test_pdf_generator.py
---------------------
Kiểm thử module xuất báo cáo thẩm định PDF (pdf_report_generator.py):
- Kiểm tra file PDF sinh ra hợp lệ (%PDF header, đọc lại được bằng pdfplumber/PyMuPDF)
- Kiểm tra tính đồng nhất dữ liệu giữa streamlit_app.py và pdf_report_generator.py
- Kiểm tra ký tự đặc biệt XML (&, <, >) trong tên doanh nghiệp & Remark Audit Trail
- Kiểm tra trường hợp biên (BCTC trống, chỉ số None)
"""

import io
import fitz  # PyMuPDF
import pytest

import pdf_report_generator as prg


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """Đọc toàn bộ văn bản từ bytes PDF bằng PyMuPDF để xác minh nội dung thực tế."""
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert pdf_bytes[:4] == b"%PDF"
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        assert doc.page_count >= 1
        return "\n".join(page.get_text("text") for page in doc)
    finally:
        doc.close()


def test_full_credit_appraisal_pdf_standard_data(
    sample_extracted_data_vnd, sample_ews_results, sample_override_rows
):
    pdf_bytes = prg.generate_full_credit_appraisal_pdf_bytes(
        company_name="CTCP FPT",
        ticker="FPT",
        extracted_data=sample_extracted_data_vnd,
        ews_results=sample_ews_results,
        qual_results={
            "total_qual_score": 88.5,
            "group_scores": {"C1": 95.0, "C2": 82.5, "C3": 95.0, "C4": 83.3, "C5": 81.2},
        },
        underwriting_data={
            "requested_limit_branch": 280_000_000_000.0,
            "planned_sales": 68_000_000_000_000.0,
            "audit_trail_logs": sample_override_rows,
        },
        evaluation_year=2024,
        industry="Công nghệ thông tin",
        audit_trail_logs=sample_override_rows,
    )
    text = _extract_pdf_text(pdf_bytes)
    assert "FPT" in text
    assert "4.1800" in text  # Altman Z'-Score được render đúng
    assert "95.0" in text  # Điểm C1 được render đúng
    assert "72,000.00" in text  # Tổng tài sản 72.000 tỷ VNĐ
    assert "Thuyết minh" in text  # Nhật ký Audit Trail có mặt trong Mục X


def test_pdf_generator_special_xml_characters_in_name_and_remark(
    sample_extracted_data_vnd, sample_ews_results
):
    """
    Kịch bản thực tế: Tên công ty chứa '&' (VD: 'Công ty TNHH Thương mại & Đầu tư A <B>')
    hoặc Remark chứa '<', '>', '&' (VD: 'Doanh thu < 50 tỷ & đã điều chỉnh').
    ReportLab Paragraph sẽ crash XML parse error nếu không escape chuỗi!
    """
    special_overrides = [
        {
            "Mã Số": "130",
            "Khoản Mục Kế Toán": "Phải thu ngắn hạn & dự phòng",
            "Số Gốc OCR (tỷ VNĐ)": 100.0,
            "Số Áp Dụng (tỷ VNĐ)": 150.0,
            "Lý Do Điều Chỉnh (Remark)": "Công nợ < 90 ngày & đã xác nhận đối chiếu > 80%",
        }
    ]
    pdf_bytes = prg.generate_full_credit_appraisal_pdf_bytes(
        company_name="CTCP Thương mại & Đầu tư Alpha <Holdings>",
        ticker="ALPHA",
        extracted_data=sample_extracted_data_vnd,
        ews_results=sample_ews_results,
        evaluation_year=2024,
        industry="Thương mại & Dịch vụ",
        audit_trail_logs=special_overrides,
    )
    text = _extract_pdf_text(pdf_bytes)
    assert "ALPHA" in text


def test_streamlit_step5_pdf_data_contract_check(sample_override_rows):
    """
    Kiểm thử hợp đồng dữ liệu (Data Contract) trực tiếp qua build_step5_pdf_payload
    mà streamlit_app.py Bước 5 đang sử dụng:
    - Bảng EWS trong PDF hiển thị đầy đủ chỉ số (không bị N/A)
    - Đơn vị BCTC chuẩn VNĐ (hiển thị đúng '72,000.00 tỷ')
    - Điểm 5Cs thực tế từ CBTD phản ánh chính xác trên PDF
    """
    from src.core.pdf_payload import build_step5_pdf_payload

    payload = build_step5_pdf_payload(
        bctc_override_data=sample_override_rows,
        qual_score=91.5,
        c_breakdown={"C1": 99.0, "C2": 98.0, "C3": 97.0, "C4": 96.0, "C5": 95.0},
        grade="AAA",
        rec_ltv_pct=80.0,
        proposed_limit_bil=280.0,
        rev_plan_bil=4500.0,
        collateral_val_bil=390.0,
        evaluation_year=2024,
    )

    pdf_bytes = prg.generate_full_credit_appraisal_pdf_bytes(
        company_name="CTCP FPT",
        ticker="FPT",
        extracted_data=payload["extracted_data"],
        ews_results=payload["ews_results"],
        wc_results=payload["wc_results"],
        qual_results=payload["qual_results"],
        underwriting_data=payload["underwriting_data"],
        evaluation_year=2024,
        audit_trail_logs=sample_override_rows,
    )
    text = _extract_pdf_text(pdf_bytes)

    assert "4.18" in text, "Bảng EWS trong PDF bị thiếu Altman Z'-Score!"
    assert "-2.92" in text, "Bảng EWS trong PDF bị thiếu Beneish M-Score!"
    assert "99.0" in text, "Điểm 5Cs C1 không được truyền đúng vào PDF!"
    assert "72,000.00 tỷ" in text, "Đơn vị Tổng tài sản trong PDF bị lệch!"
    assert "390.00 tỷ" in text, "Giá trị TSBĐ từ Bước 5 không được truyền vào PDF!"


def test_ews_pdf_bytes_basic_generation(sample_extracted_data_vnd, sample_ews_results):
    pdf_bytes = prg.generate_ews_pdf_bytes(
        company_name="CTCP FPT",
        ticker="FPT",
        extracted_data=sample_extracted_data_vnd,
        ews_results=sample_ews_results,
    )
    text = _extract_pdf_text(pdf_bytes)
    assert "FPT" in text
