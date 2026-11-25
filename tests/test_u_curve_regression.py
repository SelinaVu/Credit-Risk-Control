# -*- coding: utf-8 -*-
"""
test_u_curve_regression.py
--------------------------
Kiểm thử mô hình hồi quy chữ U (U-Curve Regression) trong u_curve_regression.py.
"""

import math
import numpy as np
import pandas as pd
import pytest

import u_curve_regression as ucr


def test_run_ols_regression_recovers_quadratic_curve():
    """Hồi quy OLS khôi phục chính xác tham số parabol bậc hai."""
    rng = np.random.default_rng(42)
    lev = np.linspace(0.1, 0.9, 60)
    # y = 1.5 + 4.0 * lev - 5.0 * lev^2 + nhiễu nhỏ (đỉnh tại lev = 0.4)
    y = 1.5 + 4.0 * lev - 5.0 * (lev ** 2) + rng.normal(0, 0.01, size=len(lev))
    X = np.column_stack([lev, lev ** 2])

    res = ucr.run_ols_regression(X, y)
    assert res["n"] == 60
    assert res["r2"] > 0.99
    assert res["beta"][1] == pytest.approx(4.0, abs=0.1)
    assert res["beta"][2] == pytest.approx(-5.0, abs=0.1)
    opt_lev = -res["beta"][1] / (2 * res["beta"][2])
    assert opt_lev == pytest.approx(0.4, abs=0.02)


def test_run_ols_regression_singular_matrix_fallback():
    """Ma trận suy biến (cột trùng lặp / dữ liệu đồng nhất) không được gây crash LinAlgError."""
    X = np.ones((20, 2))
    y = np.full(20, 2.5)
    res = ucr.run_ols_regression(X, y)
    assert res["n"] == 20
    assert all(math.isfinite(b) for b in res["beta"])


def test_process_and_run_regressions_synthetic_csv(tmp_path):
    """Kiểm thử pipeline đọc CSV -> ánh xạ ngành -> tính Z'-Score -> hồi quy từng ngành."""
    rows = []
    rng = np.random.default_rng(7)
    for i in range(30):
        ta = 1000.0 + i * 20.0
        lev = 0.2 + (i / 30.0) * 0.6
        liab = ta * lev
        eq = ta - liab
        # Thiết kế doanh thu & EBT tạo hình chữ U ngược rõ rệt (b2 < 0) theo đòn bẩy lev
        inverted_u = 3.0 - 8.0 * (lev - 0.5) ** 2 + rng.normal(0, 0.02)
        rows.append(
            {
                "Mã chứng khoán": "FPT",
                "Total_Assets": ta,
                "Total_Liabilities": liab,
                "Current_Assets": ta * 0.5,
                "Current_Liabilities": liab * 0.6,
                "Retained_Earnings": eq * 0.4,
                "EBT": ta * inverted_u * 0.5,
                "Interest_Expense": liab * 0.05,
                "Equity": eq,
                "Net_Sales": ta * max(0.2, inverted_u),
            }
        )
    csv_path = tmp_path / "panel_test.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    results = ucr.process_and_run_regressions(str(csv_path))
    assert "Technology (Công nghệ)" in results
    tech = results["Technology (Công nghệ)"]
    assert tech["n"] == 30
    assert tech["b2"] < 0
    assert math.isfinite(tech["opt_lev"])


def test_process_and_run_regressions_rejects_empty_invalid_file(tmp_path):
    """File không có dữ liệu hợp lệ phải báo ValueError rõ ràng thay vì crash lạ."""
    bad_csv = tmp_path / "bad.csv"
    pd.DataFrame({"foo": [1, 2], "bar": [3, 4]}).to_csv(bad_csv, index=False)
    with pytest.raises(ValueError):
        ucr.process_and_run_regressions(str(bad_csv))
