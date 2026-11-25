# -*- coding: utf-8 -*-
"""
test_underwriting_engine.py
---------------------------
Kiểm thử đơn vị và kiểm thử sinh dữ liệu biên (Hypothesis Fuzzing) cho credit_underwriting_engine.py.
Phát hiện sớm các lỗi chia cho 0, NaN, thiếu import, hoặc sai ngưỡng thẩm quyền phê duyệt.
"""

import math
import pytest
from hypothesis import given, settings, strategies as st

import credit_underwriting_engine as cue


# =========================================================================
# 1. KIỂM THỬ TÍNH NHU CẦU VỐN LƯU ĐỘNG (WORKING CAPITAL SIZING)
# =========================================================================
def test_working_capital_normal_case(sample_extracted_data_vnd):
    res = cue.calculate_working_capital_need(sample_extracted_data_vnd, selected_year=2024)
    assert res["planned_sales"] > res["curr_sales"]
    assert 1.2 <= res["wc_turnover"] <= 12.0
    assert res["recommended_credit_limit"] >= 0.0
    assert res["recommended_credit_limit"] % 100_000_000.0 == 0
    assert 2 <= res["recommended_ku_tenor_months"] <= 5


def test_working_capital_zero_financials_no_crash():
    """Kịch bản BCTC trắng hoặc doanh thu / giá vốn / tài sản đều bằng 0."""
    empty_data = {2024: {"Net_Sales": 0.0, "COGS": 0.0, "Current_Assets": 0.0, "Current_Liabilities": 0.0}}
    res = cue.calculate_working_capital_need(empty_data, selected_year=2024)
    assert math.isfinite(res["recommended_credit_limit"])
    assert math.isfinite(res["ccc"])
    assert res["recommended_credit_limit"] >= 0.0


def test_working_capital_invalid_selected_year_fallback(sample_extracted_data_vnd):
    """Kịch bản truyền selected_year không phải số nguyên (VD: None hoặc '2024 Q4') không được crash NameError."""
    res = cue.calculate_working_capital_need(sample_extracted_data_vnd, selected_year="2024 Q4")
    assert res["recommended_credit_limit"] >= 0.0
    assert math.isfinite(res["wc_turnover"])


def test_working_capital_negative_receivables_and_inventory():
    """Kịch bản dữ liệu bị ghi âm bất thường do lỗi OCR/mapping."""
    weird_data = {
        2024: {
            "Net_Sales": 100_000_000_000.0,
            "COGS": 80_000_000_000.0,
            "Accounts_Receivable": -5_000_000_000.0,
            "Inventories": -2_000_000_000.0,
            "Current_Assets": 10_000_000_000.0,
            "Current_Liabilities": 50_000_000_000.0,
        }
    }
    res = cue.calculate_working_capital_need(weird_data, selected_year=2024)
    assert math.isfinite(res["recommended_credit_limit"])
    assert res["recommended_credit_limit"] >= 0.0


@pytest.mark.fuzz
@settings(max_examples=120, deadline=None)
@given(
    sales=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
    cogs=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
    rec=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
    inv=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
    pay=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
    ca=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
    cl=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
    growth=st.floats(min_value=-0.8, max_value=3.0, allow_nan=False, allow_infinity=False),
    eq_pct=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_fuzz_working_capital_never_produces_nan_or_crash(
    sales, cogs, rec, inv, pay, ca, cl, growth, eq_pct
):
    """Fuzz testing 120 bộ số liệu ngẫu nhiên đảm bảo không bao giờ crash hay trả về NaN/Inf."""
    data = {
        2024: {
            "Net_Sales": sales,
            "COGS": cogs,
            "Accounts_Receivable": rec,
            "Inventories": inv,
            "Payables": pay,
            "Current_Assets": ca,
            "Current_Liabilities": cl,
        }
    }
    res = cue.calculate_working_capital_need(
        data,
        selected_year=2024,
        expected_sales_growth=growth,
        equity_contribution_pct=eq_pct,
    )
    for key in ("planned_sales", "wc_turnover", "total_wc_need", "recommended_credit_limit", "ccc"):
        assert math.isfinite(res[key]), f"{key} không hữu hạn: {res[key]}"
    assert res["recommended_credit_limit"] >= 0.0
    assert 1.2 <= res["wc_turnover"] <= 12.0


# =========================================================================
# 2. KIỂM THỬ THẨM ĐỊNH TÀI SẢN BẢO ĐẢM (COLLATERAL & LTV)
# =========================================================================
def test_evaluate_collaterals_empty_uses_safe_default():
    res = cue.evaluate_collaterals([], total_requested_limit=50_000_000_000.0)
    assert len(res["items"]) == 1
    assert res["secured_ratio"] == pytest.approx(0.825, abs=1e-3)
    assert res["meets_80_secured_rule"] is True


def test_evaluate_collaterals_zero_requested_limit():
    res = cue.evaluate_collaterals(
        [{"type": "BĐS", "description": "Nhà phố", "market_value": 10e9, "ltv_rate": 0.75}],
        total_requested_limit=0.0,
    )
    assert res["secured_facility_amount"] == 0.0
    assert res["unsecured_facility_amount"] == 0.0
    assert res["coverage_ratio"] == 0.0


@pytest.mark.fuzz
@settings(max_examples=80, deadline=None)
@given(
    market_value=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
    ltv_rate=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    requested=st.floats(min_value=0.0, max_value=1e15, allow_nan=False, allow_infinity=False),
)
def test_fuzz_evaluate_collaterals_invariants(market_value, ltv_rate, requested):
    """Tổng phần có TSBĐ + phần tín chấp luôn bằng hạn mức đề xuất và không âm."""
    res = cue.evaluate_collaterals(
        [{"type": "BĐS", "description": "TS1", "market_value": market_value, "ltv_rate": ltv_rate}],
        total_requested_limit=requested,
    )
    assert res["secured_facility_amount"] >= 0.0
    assert res["unsecured_facility_amount"] >= 0.0
    assert res["secured_facility_amount"] + res["unsecured_facility_amount"] == pytest.approx(requested, rel=1e-6)
    assert 0.0 <= res["secured_ratio"] <= 1.0 + 1e-9
    assert 0.0 <= res["unsecured_ratio"] <= 1.0 + 1e-9


# =========================================================================
# 3. KIỂM THỬ SINH ĐIỀU KIỆN TÍN DỤNG, MA TRẬN RỦI RO & PHÂN CẤP THẨM QUYỀN
# =========================================================================
def test_smart_covenants_triggers_red_flags_on_high_risk():
    high_risk_ews = {
        "Beneish_M_Score": {"score": -0.5},
        "Dechow_F_Score": {"score": 2.4},
        "Abnormal_PROD": {"score": 0.12},
        "Abnormal_CFO": {"score": -0.15},
        "Altman_Z_Prime": {"score": 0.9},
    }
    wc = {"debt_to_wc_assets_ratio": 1.35, "curr_st_debt": 200e9, "wc_assets": 140e9, "ccc": 120.0}

    covs = cue.generate_smart_credit_covenants("RISK", "CTY RỦI RO", 2024, high_risk_ews, wc)
    pre_codes = {c["code"] for c in covs["pre_conditions"]}
    post_codes = {c["code"] for c in covs["post_conditions"]}
    fin_codes = {c["code"] for c in covs["financial_covenants"]}

    assert "EWS-PRE-FRAUD" in pre_codes
    assert {"EWS-POST-AUDIT", "EWS-POST-INV", "EWS-POST-REC"}.issubset(post_codes)
    assert {"COV-01-DIVIDEND", "COV-02-LEVERAGE", "COV-03-DEBT-LIMIT"}.issubset(fin_codes)

    matrix = cue.build_credit_risk_matrix(high_risk_ews, wc, {"secured_ratio": 0.6, "unsecured_ratio": 0.4, "unsecured_facility_amount": 20e9})
    categories = {m["category"] for m in matrix}
    assert "Rủi ro Tính Xác thực BCTC" in categories
    assert "Rủi ro Khả năng Trả nợ & Phá sản" in categories
    assert "Rủi ro Tài sản Bảo đảm" in categories


def test_smart_covenants_handles_missing_ews_scores():
    covs = cue.generate_smart_credit_covenants("EMPTY", "CTY TRỐNG", 2024, {}, {})
    assert len(covs["pre_conditions"]) >= 2
    assert len(covs["post_conditions"]) >= 2
    assert len(covs["financial_covenants"]) >= 2


@pytest.mark.parametrize(
    "total_bil,unsec_bil,expected_keyword",
    [
        (5.0, 0.0, "Giám đốc Chi nhánh"),
        (15.0, 0.0, "Cấp 1 (C1)"),
        (35.0, 0.0, "Cấp 2 (C2)"),
        (12.0, 2.0, "Cấp 2 (C2)"),
        (75.0, 0.0, "Cấp 3 (C3)"),
        (25.0, 15.0, "Cấp 3 (C3)"),
        (150.0, 0.0, "Hội đồng Tín dụng"),
        (40.0, 25.0, "Hội đồng Tín dụng"),
    ],
)
def test_determine_approval_authority_tiers(total_bil, unsec_bil, expected_keyword):
    res = cue.determine_approval_authority(total_bil * 1e9, unsec_bil * 1e9)
    assert expected_keyword in res["approval_authority"]
