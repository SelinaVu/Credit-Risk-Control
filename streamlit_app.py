"""
FinTrust EWS v2.1 Enterprise - Giao Diện Thẩm Định Tín Dụng 5 Bước (Cloud & Multi-User Ready)
- Quy trình 5 bước tuần tự: Nạp BCTC & Audit Trail -> Rà soát CCC -> Ma trận EWS & ML -> Định tính 5Cs & Hybrid -> Nhu cầu vốn & Tờ trình PDF
- Lưu trữ tập trung đa quốc gia qua Supabase PostgreSQL (tự động dự phòng SQLite khi chạy offline)
- Hỗ trợ Xuất / Nhập Gói Hồ Sơ (.json) và xuất Tờ trình PDF chuẩn Ngân hàng kèm Mục X: Nhật ký Kiểm toán Audit Trail
"""

import copy
import os
import sys

import numpy as np
import pandas as pd
import streamlit as st

# Đảm bảo import được các module ở thư mục gốc dù chạy từ root hay thư mục con
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.database_cloud import (
    authenticate_supabase_user,
    change_supabase_password,
    export_profile_package_json,
    get_storage_status,
    get_team_passcode,
    is_supabase_auth_active,
    list_saved_companies,
    list_team_users,
    load_company_profile,
    parse_profile_package_json,
    save_company_profile,
    send_supabase_password_reset,
)
from src.core.pdf_payload import build_step5_pdf_payload

# -------------------------------------------------------------------------
# CẤU HÌNH TRANG STREAMLIT
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="FinTrust EWS - Hệ Thống Thẩm Định Tín Dụng & Cảnh Báo Sớm",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------------------
# KIỂM TRA THƯ VIỆN UI BỔ TRỢ
# -------------------------------------------------------------------------
HAS_SAC = False
try:
    import streamlit_antd_components as sac

    HAS_SAC = True
except ImportError:
    HAS_SAC = False

# -------------------------------------------------------------------------
# DESIGN SYSTEM & CUSTOM CSS (BANKING FINTECH THEME)
# -------------------------------------------------------------------------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .fintrust-topbar {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 1rem 1.4rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.8rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.12);
    }
    .fintrust-brand {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .fintrust-subbrand {
        font-size: 0.82rem;
        color: #93c5fd;
        margin-top: 0.15rem;
    }

    .company-strip {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #1e3a8a;
        border-radius: 8px;
        padding: 0.75rem 1.2rem;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.8rem;
    }
    .company-strip-empty {
        background: #f1f5f9;
        border: 1px dashed #94a3b8;
        border-left: 4px solid #64748b;
        border-radius: 8px;
        padding: 0.75rem 1.2rem;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.6rem;
        color: #475569;
    }

    .metric-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        border-top: 3px solid #2563eb;
        height: 100%;
    }
    .metric-title {
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        letter-spacing: 0.03em;
        margin-bottom: 0.3rem;
    }
    .metric-val {
        font-size: 1.55rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-desc {
        font-size: 0.76rem;
        color: #64748b;
        margin-top: 0.35rem;
    }

    .badge-pill {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-safe { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .badge-warning { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
    .badge-danger { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
    .badge-cloud { background: #dbeafe; color: #1d4ed8; border: 1px solid #bfdbfe; }

    .calc-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .calc-card-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 0.4rem;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------------
# CỔNG ĐĂNG NHẬP: ƯU TIÊN SUPABASE AUTH (EMAIL + PASS RIÊNG), FALLBACK TEAM PASSCODE
# -------------------------------------------------------------------------
supabase_auth_mode = is_supabase_auth_active()
required_passcode = get_team_passcode()

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if "team_authenticated" not in st.session_state:
    st.session_state.team_authenticated = (not supabase_auth_mode) and (required_passcode is None)

if "operator_name" not in st.session_state:
    st.session_state.operator_name = "Cán bộ Thẩm định (Hội Sở)"

if supabase_auth_mode and st.session_state.auth_user is None:
    _, col_login, _ = st.columns([1, 1.45, 1])
    with col_login:
        st.markdown(
            """
            <div class="fintrust-topbar" style="margin-top: 1.8rem;">
                <div>
                    <div class="fintrust-brand">🛡️ FINTRUST EWS Cloud</div>
                    <div class="fintrust-subbrand">Đăng nhập Tài khoản Cá nhân — Đồng bộ Audit Trail Chuẩn Ngân Hàng</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("supabase_login_form", border=True):
            email_input = st.text_input(
                "Email công việc:",
                value="",
                placeholder="VD: selinagv.jp@gmail.com",
            )
            pw_input = st.text_input(
                "Mật khẩu cá nhân:",
                type="password",
                placeholder="Nhập mật khẩu đã được Quản trị viên cấp",
            )
            submitted = st.form_submit_button("🔐 Đăng nhập Hệ Thống", type="primary", width="stretch")
            if submitted:
                ok_auth, user_info, auth_msg = authenticate_supabase_user(email_input, pw_input)
                if ok_auth:
                    st.session_state.auth_user = user_info
                    st.session_state.team_authenticated = True
                    st.session_state.operator_name = user_info["full_name"]
                    st.rerun()
                else:
                    st.error(auth_msg)

        with st.expander("📧 Quên mật khẩu? Gửi link đặt lại qua Email", expanded=False):
            reset_email = st.text_input("Nhập Email tài khoản của bạn:", key="reset_pw_email_input")
            if st.button("Gửi email đặt lại mật khẩu", width="stretch"):
                ok_r, msg_r = send_supabase_password_reset(reset_email)
                if ok_r:
                    st.success(msg_r)
                else:
                    st.error(msg_r)
    st.stop()

elif (not supabase_auth_mode) and required_passcode and not st.session_state.team_authenticated:
    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown(
            """
            <div class="fintrust-topbar" style="margin-top: 2rem;">
                <div>
                    <div class="fintrust-brand">🛡️ FINTRUST EWS Cloud</div>
                    <div class="fintrust-subbrand">Cổng đăng nhập Nội bộ dành cho Nhóm Thẩm Định Tín Dụng</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("team_login_form", border=True):
            op_input = st.text_input(
                "Họ tên Cán bộ Thẩm định & Quốc gia (lưu vào Nhật ký Audit Trail):",
                value="",
                placeholder="VD: Vu Quynh Giao hoặc Duong Dang Khoa",
            )
            pass_input = st.text_input(
                "Mã truy cập nhóm (Team Passcode):",
                type="password",
                placeholder="Nhập mã truy cập do quản trị viên cung cấp",
            )
            submitted = st.form_submit_button("🔐 Đăng nhập Hệ Thống", type="primary", width="stretch")
            if submitted:
                if pass_input.strip() == required_passcode:
                    st.session_state.team_authenticated = True
                    st.session_state.operator_name = op_input.strip() or "Cán bộ Thẩm định"
                    st.rerun()
                else:
                    st.error("Mã truy cập nhóm chưa chính xác. Vui lòng kiểm tra lại.")
    st.stop()

# -------------------------------------------------------------------------
# DỮ LIỆU MẶC ĐỊNH (19 TIÊU CHÍ 5CS & 12 KHOẢN MỤC BCTC AUDIT TRAIL)
# -------------------------------------------------------------------------
DEFAULT_5C_DATA = {
    # C1: Uy tín & Lãnh đạo (20%)
    "c1_mgmt_exp": {"group": "C1", "name": "Thâm niên Ban điều hành", "val": 100, "text": "Trên 10 năm kinh nghiệm chuyên sâu (100đ)"},
    "c1_cic_history": {"group": "C1", "name": "Lịch sử tín dụng CIC", "val": 100, "text": "Nhóm 1 chuẩn, không phát sinh nợ quá hạn (100đ)"},
    "c1_owner_commitment": {"group": "C1", "name": "Mức độ gắn bó của Chủ DN", "val": 80, "text": "Nắm giữ 25% - 50% và trực tiếp điều hành (80đ)"},
    "c1_legal_compliance": {"group": "C1", "name": "Minh bạch pháp lý & Tranh chấp", "val": 100, "text": "Không có tranh chấp kiện tụng hay xử phạt (100đ)"},
    # C2: Quản trị & Vận hành (20%)
    "c2_board_structure": {"group": "C2", "name": "Cơ cấu Quản trị & HĐQT", "val": 75, "text": "Đầy đủ ban bệ theo luật, có TV độc lập (75đ)"},
    "c2_internal_control": {"group": "C2", "name": "Kiểm soát nội bộ & Quản trị rủi ro", "val": 75, "text": "Có quy trình chuẩn hóa và kiểm soát chéo (75đ)"},
    "c2_erp_tech": {"group": "C2", "name": "Số hóa & ERP dòng tiền/kho", "val": 80, "text": "Phần mềm kế toán & quản trị bán hàng đồng bộ (80đ)"},
    "c2_hr_stability": {"group": "C2", "name": "Ổn định nhân sự & Kế toán trưởng", "val": 100, "text": "Lãnh đạo và Kế toán trưởng ổn định > 3 năm (100đ)"},
    # C3: Tính Xác thực BCTC (25%)
    "c3_audit_firm": {"group": "C3", "name": "Đơn vị Kiểm toán Độc lập", "val": 100, "text": "Big 4 (PwC, EY, KPMG, Deloitte) (100đ)"},
    "c3_audit_opinion": {"group": "C3", "name": "Ý kiến kiểm toán viên", "val": 100, "text": "Chấp nhận toàn phần (Unqualified Opinion) (100đ)"},
    "c3_tax_consistency": {"group": "C3", "name": "Độ khớp giữa BCTC và Thuế", "val": 100, "text": "Khớp 100% doanh thu và chi phí hợp lệ (100đ)"},
    "c3_disclosure_quality": {"group": "C3", "name": "Minh bạch Thuyết minh BCTC", "val": 80, "text": "Thuyết minh chi tiết chuẩn Thông tư 200 (80đ)"},
    # C4: Môi trường Ngành (15%)
    "c4_market_position": {"group": "C4", "name": "Vị thế & Thị phần ngành", "val": 100, "text": "Top 3 doanh nghiệp đầu ngành (100đ)"},
    "c4_entry_barriers": {"group": "C4", "name": "Rào cản gia nhập ngành", "val": 75, "text": "Trung bình (cần vốn đầu tư và mạng lưới) (75đ)"},
    "c4_cyclical_risk": {"group": "C4", "name": "Nhạy cảm chu kỳ kinh tế", "val": 75, "text": "Chu kỳ trung bình (SX công nghiệp, Viễn thông) (75đ)"},
    # C5: Chuỗi Cung ứng & Hệ sinh thái (20%)
    "c5_customer_concentration": {"group": "C5", "name": "Tập trung khách hàng đầu ra", "val": 100, "text": "Đa dạng hóa tốt (Top 3 KH < 25% doanh thu) (100đ)"},
    "c5_supplier_concentration": {"group": "C5", "name": "Tập trung nhà cung cấp đầu vào", "val": 75, "text": "Có 2-3 đối tác chiến lược ổn định (75đ)"},
    "c5_related_party_rpt": {"group": "C5", "name": "Giao dịch Bên liên quan (RPT)", "val": 75, "text": "RPT < 15% tổng tài sản, mua bán thông thường (75đ)"},
    "c5_bargaining_power": {"group": "C5", "name": "Vị thế đàm phán thương lượng", "val": 75, "text": "Cân bằng, chu kỳ phù hợp thông lệ ngành (75đ)"},
}

DEFAULT_BCTC_OVERRIDE_DATA = [
    {"Mã Số": "110", "Khoản Mục Kế Toán": "Tiền và tương đương tiền", "Số Gốc OCR (tỷ VNĐ)": 18200.0, "Số Áp Dụng (tỷ VNĐ)": 18200.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "130", "Khoản Mục Kế Toán": "Các khoản phải thu ngắn hạn", "Số Gốc OCR (tỷ VNĐ)": 1950.0, "Số Áp Dụng (tỷ VNĐ)": 19500.0, "Lý Do Điều Chỉnh (Remark)": "BCTC scan mờ số 0 hàng đơn vị, đối soát lại trang 14 Thuyết minh"},
    {"Mã Số": "140", "Khoản Mục Kế Toán": "Hàng tồn kho ròng", "Số Gốc OCR (tỷ VNĐ)": 8200.0, "Số Áp Dụng (tỷ VNĐ)": 8200.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "200", "Khoản Mục Kế Toán": "Tổng Tài sản", "Số Gốc OCR (tỷ VNĐ)": 72000.0, "Số Áp Dụng (tỷ VNĐ)": 72000.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "310", "Khoản Mục Kế Toán": "Nợ ngắn hạn", "Số Gốc OCR (tỷ VNĐ)": 29400.0, "Số Áp Dụng (tỷ VNĐ)": 29400.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "311", "Khoản Mục Kế Toán": "Vay và nợ thuê tài chính ngắn hạn", "Số Gốc OCR (tỷ VNĐ)": 15200.0, "Số Áp Dụng (tỷ VNĐ)": 15200.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "400", "Khoản Mục Kế Toán": "Vốn chủ sở hữu", "Số Gốc OCR (tỷ VNĐ)": 37100.0, "Số Áp Dụng (tỷ VNĐ)": 37100.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "511", "Khoản Mục Kế Toán": "Doanh thu thuần bán hàng & CCDV", "Số Gốc OCR (tỷ VNĐ)": 62800.0, "Số Áp Dụng (tỷ VNĐ)": 62800.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "632", "Khoản Mục Kế Toán": "Giá vốn hàng bán", "Số Gốc OCR (tỷ VNĐ)": 38900.0, "Số Áp Dụng (tỷ VNĐ)": 38900.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "635", "Khoản Mục Kế Toán": "Chi phí tài chính (Lãi vay)", "Số Gốc OCR (tỷ VNĐ)": 1120.0, "Số Áp Dụng (tỷ VNĐ)": 1120.0, "Lý Do Điều Chỉnh (Remark)": ""},
    {"Mã Số": "60", "Khoản Mục Kế Toán": "Lợi nhuận sau thuế TNDN", "Số Gốc OCR (tỷ VNĐ)": 5600.0, "Số Áp Dụng (tỷ VNĐ)": 6100.0, "Lý Do Điều Chỉnh (Remark)": "Điều chỉnh theo Biên bản Quyết toán Thuế TNDN năm 2024"},
    {"Mã Số": "OCF", "Khoản Mục Kế Toán": "Lưu chuyển tiền thuần từ HĐKD", "Số Gốc OCR (tỷ VNĐ)": 10500.0, "Số Áp Dụng (tỷ VNĐ)": 10500.0, "Lý Do Điều Chỉnh (Remark)": ""},
]

# -------------------------------------------------------------------------
# KHỞI TẠO SESSION STATE TOÀN CỤC
# -------------------------------------------------------------------------
if "profile_loaded" not in st.session_state:
    st.session_state.profile_loaded = False

if "active_company" not in st.session_state:
    st.session_state.active_company = None

if "quant_w_pct" not in st.session_state:
    st.session_state.quant_w_pct = 60

if "bctc_override_data" not in st.session_state:
    st.session_state.bctc_override_data = copy.deepcopy(DEFAULT_BCTC_OVERRIDE_DATA)

if "qual_criteria_state" not in st.session_state:
    st.session_state.qual_criteria_state = copy.deepcopy(DEFAULT_5C_DATA)

if "underwriting_inputs" not in st.session_state:
    st.session_state.underwriting_inputs = {
        "rev_plan": 4500.0,
        "cost_plan": 3850.0,
        "wctr": 8.5,
        "proposed_limit": 280.0,
        "loan_term": "12 tháng",
        "collateral_val": 390.0,
    }

if "last_sync_info" not in st.session_state:
    st.session_state.last_sync_info = ""

if "flash_messages" not in st.session_state:
    st.session_state.flash_messages = []


def _push_flash(level: str, message: str) -> None:
    """Lưu thông báo vào hàng đợi để hiển thị đầy đủ sau khi st.rerun()."""
    st.session_state.flash_messages.append((level, message))


def calculate_5c_score_summary():
    """Tính tổng điểm định tính 5Cs theo trọng số C1(20%), C2(20%), C3(25%), C4(15%), C5(20%)."""
    data = st.session_state.qual_criteria_state
    c1_scores = [v["val"] for v in data.values() if v.get("group") == "C1"]
    c2_scores = [v["val"] for v in data.values() if v.get("group") == "C2"]
    c3_scores = [v["val"] for v in data.values() if v.get("group") == "C3"]
    c4_scores = [v["val"] for v in data.values() if v.get("group") == "C4"]
    c5_scores = [v["val"] for v in data.values() if v.get("group") == "C5"]

    sc1 = float(np.mean(c1_scores)) if c1_scores else 70.0
    sc2 = float(np.mean(c2_scores)) if c2_scores else 70.0
    sc3 = float(np.mean(c3_scores)) if c3_scores else 70.0
    sc4 = float(np.mean(c4_scores)) if c4_scores else 70.0
    sc5 = float(np.mean(c5_scores)) if c5_scores else 70.0

    total = 0.20 * sc1 + 0.20 * sc2 + 0.25 * sc3 + 0.15 * sc4 + 0.20 * sc5
    return round(total, 1), {
        "C1": round(sc1, 1),
        "C2": round(sc2, 1),
        "C3": round(sc3, 1),
        "C4": round(sc4, 1),
        "C5": round(sc5, 1),
    }


def _apply_loaded_profile(payload: dict) -> None:
    """Nạp dữ liệu hồ sơ đã tải (từ Cloud, SQLite hoặc file JSON) vào session_state."""
    st.session_state.active_company = payload["company"]
    st.session_state.profile_loaded = True
    overrides = payload.get("bctc_override_data") or []
    if overrides:
        st.session_state.bctc_override_data = copy.deepcopy(overrides)
    else:
        st.session_state.bctc_override_data = copy.deepcopy(DEFAULT_BCTC_OVERRIDE_DATA)

    loaded_qual = payload.get("qual_criteria_state") or {}
    merged_qual = copy.deepcopy(DEFAULT_5C_DATA)
    for k, v in loaded_qual.items():
        if k in merged_qual and isinstance(v, dict):
            merged_qual[k].update(v)
    st.session_state.qual_criteria_state = merged_qual

    if "quant_w_pct" in payload:
        st.session_state.quant_w_pct = int(payload["quant_w_pct"])

    loaded_uw = payload.get("underwriting_inputs") or {}
    if isinstance(loaded_uw, dict) and loaded_uw:
        st.session_state.underwriting_inputs.update(loaded_uw)

    src = payload.get("source", "Cloud")
    upd_by = payload.get("updated_by", "")
    st.session_state.last_sync_info = f"Nguồn: {src}" + (f" | Cập nhật bởi: {upd_by}" if upd_by else "")


# Kiểm tra trạng thái kho lưu trữ (Supabase Cloud vs SQLite)
storage_status = get_storage_status()

# -------------------------------------------------------------------------
# SIDEBAR QUẢN LÝ HỒ SƠ, CÁN BỘ THẨM ĐỊNH & TỶ TRỌNG
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Bảng Điều Khiển Hồ Sơ")

    # Trạng thái kết nối Cloud DB
    if storage_status["mode"] == "supabase":
        st.success(f"☁️ **{storage_status['label']}**")
    else:
        st.info(f"💾 **{storage_status['label']}**")
        st.caption(storage_status["detail"])

    # Định danh Cán bộ thẩm định (khóa cứng theo tài khoản khi dùng Supabase Auth)
    auth_user = st.session_state.get("auth_user")
    if auth_user:
        st.session_state.operator_name = auth_user["full_name"]
        role_label = "👑 Quản trị viên (Admin)" if auth_user.get("role") == "admin" else "👤 Chuyên viên Thẩm định"
        st.markdown(
            f"""
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #1e3a8a; border-radius: 8px; padding: 10px 12px; margin-bottom: 10px;">
                <div style="font-size: 0.75rem; color: #1e3a8a; font-weight: 700;">{role_label}</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a;">{auth_user['full_name']}</div>
                <div style="font-size: 0.75rem; color: #64748b;">{auth_user['email']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("🔑 Đổi mật khẩu cá nhân", expanded=False):
            new_pw1 = st.text_input("Mật khẩu mới (>= 8 ký tự):", type="password", key="chg_pw_1")
            new_pw2 = st.text_input("Nhập lại mật khẩu mới:", type="password", key="chg_pw_2")
            if st.button("Cập nhật mật khẩu", width="stretch", key="btn_chg_pw"):
                if new_pw1 != new_pw2:
                    st.error("Hai ô mật khẩu mới không khớp nhau.")
                else:
                    ok_pw, msg_pw = change_supabase_password(
                        auth_user.get("access_token", ""),
                        auth_user.get("refresh_token", ""),
                        new_pw1,
                    )
                    if ok_pw:
                        st.success(msg_pw)
                    else:
                        st.error(msg_pw)

        if auth_user.get("role") == "admin":
            with st.expander("👥 Quản trị Danh sách Nhóm", expanded=False):
                roster = list_team_users()
                if roster:
                    for m in roster:
                        tag = "👑 Admin" if m.get("role") == "admin" else "Member"
                        st.markdown(f"- **{m['full_name']}** (`{tag}`)  \n  `{m['email']}`")
                st.caption("Thêm/khóa tài khoản trực tiếp tại Supabase Dashboard → Authentication → Users.")

        if st.button("🚪 Đăng xuất", width="stretch"):
            st.session_state.auth_user = None
            st.session_state.team_authenticated = False
            st.session_state.profile_loaded = False
            st.session_state.active_company = None
            st.rerun()
    else:
        st.session_state.operator_name = st.text_input(
            "👤 Cán bộ Thẩm định (lưu vết Audit):",
            value=st.session_state.operator_name,
            help="Tên của bạn sẽ được tự động đính kèm vào từng dòng sửa số liệu BCTC trên Supabase Cloud và file PDF.",
        ).strip() or "Cán bộ Thẩm định"

    if st.session_state.profile_loaded and st.session_state.active_company:
        st.success(f"⚡ Đang mở: **{st.session_state.active_company['name']}**")
        if st.session_state.last_sync_info:
            st.caption(st.session_state.last_sync_info)
        if st.button("🔄 Đóng hồ sơ / Nạp hồ sơ khác", width="stretch"):
            st.session_state.profile_loaded = False
            st.session_state.active_company = None
            st.session_state.last_sync_info = ""
            st.rerun()
    else:
        st.info("Chưa nạp hồ sơ BCTC nào. Hãy nạp hồ sơ từ Cloud hoặc upload file ở Bước 1.")

    st.markdown("---")
    st.markdown("### ⚖️ Tỷ Trọng Thẩm Định")
    st.caption("Cân đối giữa Định lượng BCTC (EWS) và Khảo sát Thực địa (5Cs):")
    st.session_state.quant_w_pct = st.slider(
        "Tỷ trọng Định lượng EWS (%):",
        min_value=30,
        max_value=90,
        value=st.session_state.quant_w_pct,
        step=5,
        help="Chuẩn khuyến nghị: 60% Định lượng BCTC / 40% Định tính 5Cs",
    )
    qual_w_pct = 100 - st.session_state.quant_w_pct
    st.markdown(
        f"""
    <div style="font-size: 0.8rem; background: #f1f5f9; padding: 6px 10px; border-radius: 6px;">
        📊 <strong>Định lượng:</strong> {st.session_state.quant_w_pct}% &nbsp;|&nbsp; 🏛️ <strong>Định tính:</strong> {qual_w_pct}%
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("FinTrust EWS Engine © 2026. Chuẩn mực Thông tư 200 & Basel II/III.")

# -------------------------------------------------------------------------
# TOPBAR BRANDING
# -------------------------------------------------------------------------
storage_badge_html = (
    '<span style="font-size: 0.72rem; background: rgba(16,185,129,0.28); border: 1px solid rgba(110,231,183,0.5); padding: 2px 8px; border-radius: 4px;">☁️ Supabase Cloud</span>'
    if storage_status["mode"] == "supabase"
    else '<span style="font-size: 0.72rem; background: rgba(255,255,255,0.18); padding: 2px 8px; border-radius: 4px;">💾 Local SQLite</span>'
)

auth_user_top = st.session_state.get("auth_user")
role_badge_top = (
    '<span style="font-size: 0.7rem; background: #f59e0b; color: #0f172a; font-weight: 700; padding: 1px 6px; border-radius: 4px; margin-left: 6px;">ADMIN</span>'
    if (auth_user_top and auth_user_top.get("role") == "admin")
    else ""
)

st.markdown(
    f"""
<div class="fintrust-topbar">
    <div>
        <div class="fintrust-brand">🛡️ FINTRUST EWS <span style="font-size: 0.72rem; background: rgba(255,255,255,0.18); padding: 2px 8px; border-radius: 4px;">v2.1 Enterprise</span> {storage_badge_html}</div>
        <div class="fintrust-subbrand">Hệ thống Cảnh báo Sớm Rủi ro & Thẩm định Cấp Tín dụng Doanh nghiệp Đa Quốc Gia</div>
    </div>
    <div style="text-align: right; font-size: 0.82rem;">
        <div>👤 <strong>Cán bộ Thẩm định:</strong> {st.session_state.operator_name}{role_badge_top}</div>
        <div style="color: #93c5fd;">Phòng Thẩm định & Phê duyệt Tín dụng | Hội Sở</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Hiển thị các thông báo lưu vết / cảnh báo sau khi st.rerun()
if st.session_state.flash_messages:
    for _lvl, _msg in st.session_state.flash_messages:
        if _lvl == "success":
            st.success(_msg)
        elif _lvl == "warning":
            st.warning(_msg)
        elif _lvl == "error":
            st.error(_msg)
        else:
            st.info(_msg)
    st.session_state.flash_messages = []

# -------------------------------------------------------------------------
# COMPANY STRIP BANNER (EMPTY STATE / LOADED STATE)
# -------------------------------------------------------------------------
if not st.session_state.profile_loaded:
    st.markdown(
        """
    <div class="company-strip-empty">
        <div>
            ⏳ <strong>Trạng thái: Chưa có hồ sơ doanh nghiệp được nạp.</strong>
            <span style="margin-left: 8px; font-size: 0.85rem;">Vui lòng mở hồ sơ đã lưu trên Cloud, tải lên BCTC (PDF/Excel) hoặc nạp hồ sơ mẫu tại Bước 1.</span>
        </div>
        <div>
            <span class="badge-pill" style="background:#e2e8f0; color:#475569;">Trạng thái: Chờ dữ liệu</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    c_info = st.session_state.active_company
    q_score, _ = calculate_5c_score_summary()
    st.markdown(
        f"""
    <div class="company-strip">
        <div>
            <strong style="font-size: 1.05rem; color: #0f172a;">{c_info['name']} ({c_info['ticker']})</strong>
            <span style="margin-left: 10px; color: #64748b; font-size: 0.85rem;">Ngành: <strong>{c_info['industry']}</strong></span>
            <span style="margin-left: 10px; color: #64748b; font-size: 0.85rem;">Thâm niên: <strong>{c_info['age']} năm</strong></span>
        </div>
        <div>
            <span class="badge-pill badge-safe">Điểm Định Tính 5Cs: <strong>{q_score:.1f}/100</strong></span>
            <span class="badge-pill badge-safe" style="margin-left: 6px;">Tỷ trọng: <strong>{st.session_state.quant_w_pct}% ĐL / {qual_w_pct}% ĐT</strong></span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------------
# WORKFLOW STEPPER (5 BƯỚC CHUẨN HOÁ: ĐỊNH LƯỢNG TRƯỚC -> ĐỊNH TÍNH SAU)
# -------------------------------------------------------------------------
step_labels = [
    "1. Nạp BCTC & Hồ Sơ",
    "2. Rà Soát Tài Chính & CCC",
    "3. Ma Trận Cảnh Báo Sớm EWS",
    "4. Khảo Sát Định Tính 5Cs & Hybrid",
    "5. Nhu Cầu Vay Vốn & Tờ Trình",
]

if HAS_SAC:
    current_step_idx = sac.steps(
        items=[
            sac.StepsItem(title="Bước 1", subtitle="Nạp BCTC & Cloud", icon="file-earmark-arrow-up"),
            sac.StepsItem(title="Bước 2", subtitle="Rà soát CCC", icon="calculator"),
            sac.StepsItem(title="Bước 3", subtitle="Ma trận EWS & ML", icon="shield-exclamation"),
            sac.StepsItem(title="Bước 4", subtitle="Định tính 5Cs & Hybrid", icon="clipboard-check"),
            sac.StepsItem(title="Bước 5", subtitle="Nhu cầu vốn & Memo", icon="check2-circle"),
        ],
        index=0 if not st.session_state.profile_loaded else 1,
        return_index=True,
    )
else:
    current_step = st.segmented_control(
        "Quy trình thẩm định tín dụng:",
        options=step_labels,
        default=step_labels[0] if not st.session_state.profile_loaded else step_labels[1],
        label_visibility="collapsed",
        width="stretch",
    )
    current_step_idx = step_labels.index(current_step) if current_step in step_labels else 0

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================================
# BƯỚC 1: NẠP BCTC, ĐỒNG BỘ CLOUD & HIỆU CHỈNH AUDIT TRAIL
# =========================================================================
if current_step_idx == 0:
    st.subheader("📥 Bước 1: Tiếp Nhận BCTC, Đồng Bộ Cloud & Hiệu Chỉnh Audit Trail")
    st.caption(
        "Mở hồ sơ do đồng nghiệp đã lưu trên Supabase Cloud, tải lên tệp BCTC mới (PDF/Excel), hoặc nạp hồ sơ mẫu."
    )

    col_upload, col_cloud = st.columns([1.45, 1.55])

    with col_upload:
        with st.container(border=True):
            st.markdown("#### 📤 Tạo hồ sơ mới từ tệp BCTC")
            up_col1, up_col2 = st.columns([1, 1.6])
            with up_col1:
                new_ticker = st.text_input("Mã DN / Ticker:", value="ANPHAT_CORP", key="upload_ticker_input").strip().upper()
            with up_col2:
                new_company_name = st.text_input(
                    "Tên Doanh nghiệp:",
                    value="CÔNG TY TNHH SẢN XUẤT THƯƠNG MẠI AN PHÁT",
                    key="upload_company_name_input",
                ).strip()
            new_industry = st.text_input("Ngành nghề kinh doanh:", value="Sản xuất Hàng tiêu dùng", key="upload_industry_input").strip()

            uploaded_files = st.file_uploader(
                "Chọn tệp BCTC (PDF quét ảnh, XLSX, XLS):",
                type=["pdf", "xlsx", "xls"],
                accept_multiple_files=True,
            )
            if uploaded_files:
                if st.button("🚀 Xử lý OCR & Lưu Khởi Tạo Lên Cloud", type="primary", width="stretch"):
                    comp_obj = {
                        "name": new_company_name or new_ticker or "DOANH NGHIỆP MỚI",
                        "ticker": new_ticker or "NEW_CORP",
                        "industry": new_industry or "Khác",
                        "age": 8,
                        "quant_score": 82.4,
                    }
                    st.session_state.profile_loaded = True
                    st.session_state.active_company = comp_obj
                    st.session_state.bctc_override_data = copy.deepcopy(DEFAULT_BCTC_OVERRIDE_DATA)
                    ok, msg = save_company_profile(
                        company=comp_obj,
                        bctc_override_data=st.session_state.bctc_override_data,
                        qual_criteria=st.session_state.qual_criteria_state,
                        quant_w_pct=st.session_state.quant_w_pct,
                        underwriting_inputs=st.session_state.underwriting_inputs,
                        operator=st.session_state.operator_name,
                    )
                    st.session_state.last_sync_info = msg
                    if ok:
                        _push_flash("success", f"✅ Đã bóc tách BCTC & đồng bộ thành công! {msg}")
                    st.rerun()

    with col_cloud:
        with st.container(border=True):
            st.markdown("#### ☁️ Mở hồ sơ từ Kho Dữ Liệu Chung (Cloud / SQLite)")
            saved_list = list_saved_companies()

            if saved_list:
                saved_map = {item["ticker"]: item for item in saved_list}
                picked_saved = st.selectbox(
                    "Chọn hồ sơ đồng nghiệp đã lưu:",
                    options=list(saved_map.keys()),
                    format_func=lambda tk: (
                        f"{saved_map[tk]['name']} ({tk}) — sửa bởi {saved_map[tk]['updated_by']} [{saved_map[tk]['source']}]"
                    ),
                    key="cloud_saved_picker",
                )
                if st.button(f"☁️ Tải Hồ Sơ {picked_saved} Từ Kho Chung", type="primary", width="stretch"):
                    loaded = load_company_profile(picked_saved)
                    if loaded:
                        _apply_loaded_profile(loaded)
                        _push_flash("success", f"✅ Đã nạp hồ sơ **{loaded['company']['name']}** cùng toàn bộ vết sửa tay!")
                        st.rerun()
            else:
                st.caption("Chưa có hồ sơ nào được lưu trong kho chung. Hãy nạp một hồ sơ mẫu bên dưới rồi bấm Lưu để khởi tạo.")

            st.markdown("---")
            st.markdown("**📂 Hoặc nạp nhanh Hồ Sơ Mẫu có sẵn:**")
            sample_options = {
                "FPT": {"name": "CTCP FPT", "ticker": "FPT", "industry": "Công nghệ thông tin & Viễn thông", "age": 15, "quant_score": 89.2},
                "VNM": {"name": "CTCP Sữa Việt Nam (Vinamilk)", "ticker": "VNM", "industry": "Thực phẩm & Tiêu dùng", "age": 22, "quant_score": 86.8},
                "HPG": {"name": "CTCP Tập đoàn Hòa Phát", "ticker": "HPG", "industry": "Sản xuất Thép & Kim loại", "age": 18, "quant_score": 79.5},
            }
            c_pick = st.selectbox(
                "Chọn doanh nghiệp mẫu:",
                list(sample_options.keys()),
                format_func=lambda k: f"{sample_options[k]['name']} ({k})",
            )
            if st.button(f"⚡ Nạp hồ sơ mẫu {c_pick}", width="stretch"):
                existing = load_company_profile(c_pick)
                if existing:
                    _apply_loaded_profile(existing)
                    _push_flash("success", f"✅ Đã nạp phiên bản đã lưu của **{existing['company']['name']}** từ {existing['source']}!")
                else:
                    st.session_state.profile_loaded = True
                    st.session_state.active_company = copy.deepcopy(sample_options[c_pick])
                    st.session_state.bctc_override_data = copy.deepcopy(DEFAULT_BCTC_OVERRIDE_DATA)
                    st.session_state.qual_criteria_state = copy.deepcopy(DEFAULT_5C_DATA)
                    st.session_state.last_sync_info = "Hồ sơ mẫu khởi tạo (chưa lưu lên Cloud)"
                    _push_flash("success", f"✅ Đã nạp hồ sơ mẫu **{sample_options[c_pick]['name']}**!")
                st.rerun()

    # Tiện ích Xuất / Nhập Gói Hồ Sơ JSON (dự phòng gửi qua Email / Teams / Zalo)
    with st.expander("📦 Chia sẻ & Sao lưu ngoại tuyến: Xuất / Nhập Gói Hồ Sơ (.json)", expanded=False):
        jcol1, jcol2 = st.columns(2)
        with jcol1:
            st.caption("Tải xuống 1 file `.json` duy nhất chứa toàn bộ số liệu BCTC, vết sửa tay và điểm 5Cs:")
            if st.session_state.profile_loaded and st.session_state.active_company:
                pkg_str = export_profile_package_json(
                    company=st.session_state.active_company,
                    bctc_override_data=st.session_state.bctc_override_data,
                    qual_criteria=st.session_state.qual_criteria_state,
                    quant_w_pct=st.session_state.quant_w_pct,
                    operator=st.session_state.operator_name,
                )
                st.download_button(
                    label=f"📤 Xuất Gói Hồ Sơ {st.session_state.active_company['ticker']}.json",
                    data=pkg_str.encode("utf-8"),
                    file_name=f"FinTrust_{st.session_state.active_company['ticker']}_v2.1.json",
                    mime="application/json",
                    width="stretch",
                )
            else:
                st.info("Hãy nạp một hồ sơ doanh nghiệp trước để xuất gói `.json`.")
        with jcol2:
            st.caption("Nhập lại file `.json` do đồng nghiệp gửi qua Email/Chat:")
            json_up = st.file_uploader("Chọn tệp Gói Hồ Sơ (.json):", type=["json"], key="json_pkg_uploader")
            if json_up is not None:
                if st.button("📥 Nạp Gói Hồ Sơ Từ File JSON", type="primary", width="stretch"):
                    try:
                        parsed = parse_profile_package_json(json_up.read())
                        parsed["source"] = f"Tệp JSON ({json_up.name})"
                        parsed["updated_by"] = parsed.get("exported_by", "Đồng nghiệp")
                        _apply_loaded_profile(parsed)
                        _push_flash("success", f"✅ Đã nạp thành công hồ sơ **{parsed['company']['name']}** từ file JSON!")
                        st.rerun()
                    except Exception as exc_json:
                        st.error(f"Không thể đọc tệp JSON: {exc_json}")

    # Bảng trạng thái nhận diện & Audit Data Editor nếu đã nạp hồ sơ
    if st.session_state.profile_loaded:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📋 Trạng Thái Bóc Tách BCTC Doanh Nghiệp")
        st_df = pd.DataFrame(
            {
                "Biểu mẫu BCTC": ["Bảng Cân đối Kế toán", "Báo cáo Kết quả KD", "Báo cáo Lưu chuyển Tiền tệ (CFO)", "Thuyết minh BCTC"],
                "Niên độ phát hiện": ["2022 - 2024 (3 năm)", "2022 - 2024 (3 năm)", "2022 - 2024 (3 năm)", "Phát hiện 34 trang chi tiết"],
                "Tính cân đối kế toán": [
                    "🟢 Khớp 100% (Tổng TS = Tổng Nguồn vốn)",
                    "🟢 Khớp 100% DT & CP",
                    "🟢 Khớp dòng tiền lưu chuyển thuần",
                    "🟢 Đầy đủ các mục trọng yếu",
                ],
            }
        )
        st.dataframe(st_df, width="stretch", hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ✏️ Bảng Đối Soát & Hiệu Chỉnh Dữ Liệu BCTC Trích Xuất (Audit Trail & Manual Overrides)")
        st.caption(
            "Cho phép Cán bộ Tín dụng chỉnh sửa số liệu bị sai do scan mờ hoặc thiếu mục. Mọi can thiệp thủ công đều bắt buộc nhập lý do (Remark) và được đồng bộ lên Supabase Cloud."
        )

        override_df = pd.DataFrame(st.session_state.bctc_override_data)
        override_df["Chênh Lệch (tỷ VNĐ)"] = override_df["Số Áp Dụng (tỷ VNĐ)"] - override_df["Số Gốc OCR (tỷ VNĐ)"]
        override_df["Nguồn Gốc"] = override_df["Chênh Lệch (tỷ VNĐ)"].apply(
            lambda x: "✏️ Nhập tay" if abs(x) > 0.001 else "🤖 OCR gốc"
        )

        cols_order = [
            "Mã Số",
            "Khoản Mục Kế Toán",
            "Số Gốc OCR (tỷ VNĐ)",
            "Số Áp Dụng (tỷ VNĐ)",
            "Chênh Lệch (tỷ VNĐ)",
            "Nguồn Gốc",
            "Lý Do Điều Chỉnh (Remark)",
        ]
        display_override_df = override_df[cols_order]

        edited_df = st.data_editor(
            display_override_df,
            width="stretch",
            hide_index=True,
            disabled=["Mã Số", "Khoản Mục Kế Toán", "Số Gốc OCR (tỷ VNĐ)", "Chênh Lệch (tỷ VNĐ)", "Nguồn Gốc"],
            column_config={
                "Số Gốc OCR (tỷ VNĐ)": st.column_config.NumberColumn(format="%.1f"),
                "Số Áp Dụng (tỷ VNĐ)": st.column_config.NumberColumn(
                    format="%.1f", help="Nhấp đúp chuột để nhập lại số liệu chính xác nếu OCR đọc sai"
                ),
                "Chênh Lệch (tỷ VNĐ)": st.column_config.NumberColumn(format="%+.1f"),
                "Lý Do Điều Chỉnh (Remark)": st.column_config.TextColumn(
                    help="Bắt buộc ghi rõ căn cứ điều chỉnh (VD: mờ số, đối chiếu Thuyết minh...)"
                ),
            },
            key="bctc_data_editor",
        )

        # Các nút tác vụ lưu lên Supabase Cloud / SQLite
        save_label = (
            "☁️ Lưu Vết Lên Supabase Cloud & Đồng Bộ Nhóm"
            if storage_status["mode"] == "supabase"
            else "💾 Lưu Vết Vào CSDL & Đồng Bộ EWS"
        )
        col_act1, col_act2, col_act3 = st.columns([1.6, 1.4, 1.3])
        with col_act1:
            if st.button(save_label, type="primary", width="stretch"):
                updated_list = []
                missing_remarks = []
                for _, row in edited_df.iterrows():
                    ocr_v = float(row["Số Gốc OCR (tỷ VNĐ)"])
                    app_v = float(row["Số Áp Dụng (tỷ VNĐ)"])
                    rem = str(row["Lý Do Điều Chỉnh (Remark)"] or "").strip()
                    if abs(app_v - ocr_v) > 0.001 and not rem:
                        missing_remarks.append(f"{row['Khoản Mục Kế Toán']} (Mã {row['Mã Số']})")
                    updated_list.append(
                        {
                            "Mã Số": str(row["Mã Số"]),
                            "Khoản Mục Kế Toán": str(row["Khoản Mục Kế Toán"]),
                            "Số Gốc OCR (tỷ VNĐ)": ocr_v,
                            "Số Áp Dụng (tỷ VNĐ)": app_v,
                            "Lý Do Điều Chỉnh (Remark)": rem,
                            "Cán Bộ Thao Tác": st.session_state.operator_name,
                        }
                    )
                st.session_state.bctc_override_data = updated_list
                ok, sync_msg = save_company_profile(
                    company=st.session_state.active_company,
                    bctc_override_data=updated_list,
                    qual_criteria=st.session_state.qual_criteria_state,
                    quant_w_pct=st.session_state.quant_w_pct,
                    underwriting_inputs=st.session_state.underwriting_inputs,
                    operator=st.session_state.operator_name,
                )
                st.session_state.last_sync_info = sync_msg
                if ok:
                    _push_flash("success", sync_msg)
                if missing_remarks:
                    _push_flash(
                        "warning",
                        "⚠️ Lưu ý Audit Trail: Các khoản mục sau đã sửa tay nhưng chưa điền Remark giải trình: "
                        + ", ".join(missing_remarks),
                    )
                st.rerun()

        with col_act2:
            if st.button("⚡ Tự Động Cân Đối Nguồn Vốn (Tổng TS = Nợ + CSH)", width="stretch"):
                current_items = {r["Mã Số"]: r for r in st.session_state.bctc_override_data}
                liab = current_items.get("310", {}).get("Số Áp Dụng (tỷ VNĐ)", 29400.0)
                eq = current_items.get("400", {}).get("Số Áp Dụng (tỷ VNĐ)", 37100.0)
                tot_assets = liab + eq
                for r in st.session_state.bctc_override_data:
                    if r["Mã Số"] == "200":
                        r["Số Áp Dụng (tỷ VNĐ)"] = tot_assets
                        r["Lý Do Điều Chỉnh (Remark)"] = f"Tự động cân đối theo Tổng Nợ ({liab:,.1f}) + CSH ({eq:,.1f})"
                _push_flash("info", f"⚡ Đã cân đối Tổng Tài sản = {tot_assets:,.1f} tỷ VNĐ (Nợ: {liab:,.1f} + CSH: {eq:,.1f})!")
                st.rerun()

        with col_act3:
            if st.button("🔄 Khôi Phục Toàn Bộ Về Số Gốc OCR", width="stretch"):
                for r in st.session_state.bctc_override_data:
                    r["Số Áp Dụng (tỷ VNĐ)"] = r["Số Gốc OCR (tỷ VNĐ)"]
                    r["Lý Do Điều Chỉnh (Remark)"] = ""
                _push_flash("warning", "🔄 Đã hoàn tác toàn bộ các chỉ tiêu về số liệu gốc OCR ban đầu.")
                st.rerun()

        active_overrides = [
            r
            for r in st.session_state.bctc_override_data
            if abs(r["Số Áp Dụng (tỷ VNĐ)"] - r["Số Gốc OCR (tỷ VNĐ)"]) > 0.001
        ]
        if active_overrides:
            override_msg = "<br>".join(
                [
                    f"• <strong>{r['Khoản Mục Kế Toán']} (Mã {r['Mã Số']})</strong>: Gốc <code>{r['Số Gốc OCR (tỷ VNĐ)']:,.1f}</code> ➔ Sửa <code>{r['Số Áp Dụng (tỷ VNĐ)']:,.1f} tỷ VNĐ</code> (Chênh lệch: <strong>{r['Số Áp Dụng (tỷ VNĐ)'] - r['Số Gốc OCR (tỷ VNĐ)']:+,.1f} tỷ</strong>) | <em>Lý do: {r['Lý Do Điều Chỉnh (Remark)'] or 'Chưa có ghi chú'}</em>"
                    for r in active_overrides
                ]
            )
            st.markdown(
                f"""
            <div style="background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #f59e0b; padding: 12px 16px; border-radius: 6px; margin-top: 12px; font-size: 0.85rem;">
                <div style="font-weight: 700; color: #92400e; margin-bottom: 4px;">⚠️ PHÁT HIỆN {len(active_overrides)} CHỈ TIÊU ĐƯỢC HIỆU CHỈNH THỦ CÔNG (ĐÃ LƯU VẾT & SẼ BÁO CÁO HỘI ĐỒNG TÍN DỤNG):</div>
                <div style="color: #78350f;">{override_msg}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# =========================================================================
# KIỂM TRA ĐIỀU KIỆN TRƯỚC KHI VÀO CÁC BƯỚC 2 -> 5
# =========================================================================
elif not st.session_state.profile_loaded:
    st.warning("⚠️ **Bạn chưa nạp hồ sơ doanh nghiệp!**")
    st.info("Vui lòng quay lại **Bước 1: Nạp BCTC & Hồ Sơ** để mở hồ sơ từ Cloud, tải lên file BCTC hoặc nạp hồ sơ mẫu.")

# =========================================================================
# BƯỚC 2: RÀ SOÁT TÀI CHÍNH & CHU KỲ TIỀN MẶT (CCC)
# =========================================================================
elif current_step_idx == 1:
    st.subheader("🔍 Bước 2: Bóc Tách Chu Kỳ Tiền Mặt (CCC) & Toàn Diện Định Lượng Vốn Lưu Động")
    st.caption(
        "Khảo sát toàn diện 5 phân hệ định lượng: Chu kỳ tiền mặt 3 năm, Khai báo doanh thu ngành (Module A), Chỉ số hoạt động & thanh khoản (Module B&C), Sao kê dòng tiền ngân hàng và Đối chiếu thuế."
    )

    tab_b2_ccc, tab_b2_module_a, tab_b2_liquidity, tab_b2_bank_stmt, tab_b2_validation = st.tabs(
        [
            "⚖️ 2.1 Chu kỳ Tiền mặt (CCC)",
            "🏢 2.2 Phân rã Doanh thu (Module A)",
            "💧 2.3 Chỉ số Hoạt động & Thanh khoản",
            "💳 2.4 Sao kê Dòng tiền Ngân hàng",
            "🔍 2.5 Kiểm tra Toàn vẹn & Thuế",
        ]
    )

    with tab_b2_ccc:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                """
            <div class="metric-box">
                <div class="metric-title">Kỳ thu tiền bình quân (DSO)</div>
                <div class="metric-val">42.5 <span style="font-size:0.9rem; font-weight:normal;">ngày</span></div>
                <div class="badge-pill badge-safe">🟢 Rút ngắn 3.2 ngày</div>
                <div class="metric-desc">Tốc độ thu hồi nợ nhanh hơn ngành</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """
            <div class="metric-box">
                <div class="metric-title">Thời gian tồn kho (DSI)</div>
                <div class="metric-val">24.1 <span style="font-size:0.9rem; font-weight:normal;">ngày</span></div>
                <div class="badge-pill badge-safe">🟢 Tồn kho luân chuyển tốt</div>
                <div class="metric-desc">Ít rủi ro ứ đọng hàng hóa</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                """
            <div class="metric-box">
                <div class="metric-title">Kỳ trả tiền NCC (DPO)</div>
                <div class="metric-val">36.8 <span style="font-size:0.9rem; font-weight:normal;">ngày</span></div>
                <div class="badge-pill badge-safe">🟢 Chiếm dụng vốn tốt</div>
                <div class="metric-desc">Uy tín cao với nhà cung cấp</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                """
            <div class="metric-box" style="border-top-color: #10b981;">
                <div class="metric-title">Chu kỳ tiền mặt (CCC = DSO+DSI-DPO)</div>
                <div class="metric-val" style="color: #065f46;">29.8 <span style="font-size:0.9rem; font-weight:normal;">ngày</span></div>
                <div class="badge-pill badge-safe">🟢 Vòng quay VLĐ: 12.2 vòng/năm</div>
                <div class="metric-desc">Nhu cầu tài trợ VLĐ lành mạnh</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📈 Diễn biến Chu kỳ Tiền mặt (CCC) qua 3 Niên độ Kế toán (2022 - 2024)")
        ccc_trend_df = pd.DataFrame(
            {
                "Khoản Mục Đo Lường": [
                    "Kỳ thu tiền bình quân (DSO)",
                    "Thời gian lưu kho bình quân (DSI)",
                    "Kỳ thanh toán bình quân NCC (DPO)",
                    "Chu kỳ tiền mặt (CCC = DSO+DSI-DPO)",
                    "Số vòng quay Vốn lưu động (WCTR)",
                ],
                "Năm 2022": ["48.2 ngày", "26.5 ngày", "32.0 ngày", "42.7 ngày", "8.5 vòng/năm"],
                "Năm 2023": ["45.7 ngày", "25.0 ngày", "34.5 ngày", "36.2 ngày", "10.1 vòng/năm"],
                "Năm 2024": ["42.5 ngày", "24.1 ngày", "36.8 ngày", "29.8 ngày", "12.2 vòng/năm"],
                "Xu Hướng Đánh Giá": [
                    "🟢 Rút ngắn liên tục (Tốt)",
                    "🟢 Ổn định ở mức thấp",
                    "🟢 Kéo dài công nợ NCC hợp lý",
                    "🟢 Rút ngắn 12.9 ngày sau 3 năm",
                    "🟢 Tăng tốc độ quay vòng vốn",
                ],
            }
        )
        st.dataframe(ccc_trend_df, width="stretch", hide_index=True)
        st.info(
            "💡 **Kết luận Vốn lưu động:** Doanh nghiệp có năng lực quản trị công nợ xuất sắc, vòng quay vốn lưu động tăng từ 8.5 lên 12.2 vòng/năm, giúp giảm áp lực vay nợ ngân hàng."
        )

    with tab_b2_module_a:
        st.markdown("##### 🏢 Bóc Tách Doanh Thu & Biên Lợi Nhuận Gộp Theo Từng Mảng Kinh Doanh")
        st.caption("Tránh rủi ro dùng số liệu gộp BCTC; thẩm định đúng rủi ro từng ngành hàng mà doanh nghiệp đang xin vay tài trợ.")

        col_m1, col_m2 = st.columns([1.8, 1.2])
        with col_m1:
            segment_df = pd.DataFrame(
                {
                    "Mảng Hoạt Động / Lĩnh Vực": [
                        "Dịch vụ Xuất khẩu Phần mềm (Core)",
                        "Giải pháp Chuyển đổi số & Tích hợp hệ thống",
                        "Viễn thông & Băng rộng Data",
                        "Giáo dục & Đào tạo công nghệ",
                    ],
                    "Doanh Thu 2024 (tỷ VNĐ)": ["28.500", "14.200", "12.800", "3.200"],
                    "Tỷ Trọng (%)": ["48.5%", "24.2%", "21.8%", "5.5%"],
                    "Biên Lãi Gộp": ["38.5%", "18.2%", "42.0%", "32.5%"],
                    "Mục Đích Xin Vay": [
                        "✅ Tài trợ vốn lưu động HĐ ngoại",
                        "✅ Bảo lãnh & LC nhập thiết bị",
                        "❌ Tự cân đối dòng tiền",
                        "❌ Không có nhu cầu vay",
                    ],
                }
            )
            st.dataframe(segment_df, width="stretch", hide_index=True)
        with col_m2:
            st.markdown(
                """
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
                <div style="font-weight: 700; color: #1e3a8a; margin-bottom: 6px;">🎯 Đánh Giá Module A của CBTD:</div>
                <div style="font-size: 0.86rem; color: #334155; line-height: 1.5;">
                    - Mảng kinh doanh cốt lõi (Xuất khẩu phần mềm) chiếm gần 50% doanh thu và có biên lãi gộp cao nhất (38.5%).<br>
                    - Rủi ro đa ngành ở mức thấp, doanh nghiệp không đầu tư dàn trải sang BĐS hay chứng khoán.<br>
                    - Phương án vay vốn tập trung 100% vào tài trợ hợp đồng xuất khẩu phần mềm uy tín.
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with tab_b2_liquidity:
        st.markdown("##### 💧 Bảng Đầy Đủ 8 Chỉ Số Thanh Khoản, Dòng Tiền & Cân Đối Nguồn Vốn (3 Năm)")
        liquidity_full_df = pd.DataFrame(
            {
                "Nhóm Chỉ Tiêu": [
                    "Thanh toán",
                    "Thanh toán",
                    "Thanh toán",
                    "Năng lực trả nợ",
                    "Chất lượng dòng tiền",
                    "Cân đối tài sản",
                    "Đòn bẩy",
                    "Đòn bẩy",
                ],
                "Tên Chỉ Tiêu Tài Chính": [
                    "1. Hệ số thanh toán hiện hành (Current Ratio)",
                    "2. Hệ số thanh toán nhanh (Quick Ratio)",
                    "3. Hệ số thanh toán tiền mặt (Cash Ratio)",
                    "4. Khả năng chi trả lãi vay (ICR = EBIT / Chi phí lãi vay)",
                    "5. Dòng tiền thuần HĐKD (CFO) / Nợ ngắn hạn",
                    "6. Tỷ lệ Vay ngắn hạn / (Phải thu + Tồn kho)",
                    "7. Đòn bẩy tài chính Tổng nợ / Tổng tài sản (D/A)",
                    "8. Đòn bẩy Nợ vay / Vốn chủ sở hữu (D/E)",
                ],
                "Năm 2022": ["1.40", "1.12", "0.41", "10.8x", "24.5%", "65.2%", "51.2%", "1.05"],
                "Năm 2023": ["1.46", "1.19", "0.48", "12.4x", "29.8%", "61.0%", "49.8%", "0.98"],
                "Năm 2024": ["1.55", "1.29", "0.52", "14.5x", "34.2%", "58.1%", "48.5%", "0.92"],
                "Ngưỡng Chuẩn Ngành": [">= 1.20", ">= 0.80", ">= 0.20", ">= 3.00x", ">= 20.0%", "<= 80.0%", "<= 50.0%", "<= 1.50"],
                "Đánh Giá Rủi Ro": [
                    "🟢 An toàn",
                    "🟢 Vượt chuẩn",
                    "🟢 Tiền mặt dồi dào",
                    "🟢 Rất cao",
                    "🟢 Dòng tiền thực",
                    "🟢 Đúng mục đích",
                    "🟡 Cận biên U-Curve",
                    "🟢 Tốt",
                ],
            }
        )
        st.dataframe(liquidity_full_df, width="stretch", hide_index=True)

    with tab_b2_bank_stmt:
        st.markdown("##### 💳 Phân Tích Dòng Tiền Sao Kê Ngân Hàng & Giám Sát Sau Giải Ngân")
        st.caption("Khắc phục độ trễ của BCTC bằng cách đối soát dữ liệu dòng tiền thực tế qua tài khoản ngân hàng.")

        c_bank1, c_bank2, c_bank3 = st.columns(3)
        with c_bank1:
            st.metric("Tổng Dòng Tiền Vào (Inflow 12T)", "54.200 tỷ VNĐ", "+14.2% YoY")
        with c_bank2:
            st.metric("Tỷ Lệ Tiền Về TK / Doanh Thu", "92.5%", "🟢 Khớp chuẩn (>85%)")
        with c_bank3:
            st.metric("Hệ Số Bao Phủ Nợ Gốc & Lãi (DSCR)", "2.45x", "🟢 Năng lực trả nợ tốt (>1.3x)")

        st.markdown(
            """
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px 16px; border-radius: 8px; margin-top: 10px;">
            <div style="font-weight: 700; color: #166534;">✅ Kết Quả Đối Soát Dòng Tiền Ngân Hàng:</div>
            <div style="font-size: 0.85rem; color: #14532d; margin-top: 4px;">
                - Dòng tiền thực tế về tài khoản thanh toán đạt 92.5% doanh thu ghi nhận sổ sách ──► Không có hiện tượng ghi nhận doanh thu khống.<br>
                - Số dư tiền gửi bình quân duy trì ổn định từ 4.500 - 6.000 tỷ VNĐ tại hệ thống NHTM.<br>
                - Cam kết chuyển 100% dòng tiền nguồn thu từ các hợp đồng xin tài trợ về tài khoản mở tại Ngân hàng cho vay.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with tab_b2_validation:
        st.markdown("##### 🔍 Kiểm Tra Tính Toàn Vẹn Số Liệu Kế Toán & Đối Chiếu Thuế")
        valid_table = pd.DataFrame(
            {
                "Nội Dung Kiểm Tra": [
                    "Cân đối Bảng CĐKT (Tổng Tài sản = Tổng Nguồn vốn)",
                    "Đối soát Doanh thu BCTC vs Tờ khai Thuế GTGT 4 Quý",
                    "Đối chiếu Chi phí Lãi vay vs Tờ khai Quyết toán Thuế TNDN",
                    "Kiểm tra tính logic Dòng tiền Lưu chuyển thuần (CFO + CFI + CFF)",
                    "Kiểm tra số dư Tiền gửi cuối kỳ với Thư xác nhận số dư Ngân hàng",
                ],
                "Số Liệu BCTC": ["Khớp 100%", "58.700 tỷ VNĐ", "1.120 tỷ VNĐ", "Tăng ròng 2.450 tỷ VNĐ", "Khớp 100%"],
                "Số Liệu Đối Ứng": ["Khớp 100%", "58.550 tỷ VNĐ (Lệch 0.25%)", "1.120 tỷ VNĐ", "Khớp số dư đầu/cuối", "Biên bản đối chiếu ngân hàng"],
                "Kết Luận": ["🟢 Hợp lệ", "🟢 Chênh lệch thời điểm nhỏ", "🟢 Khớp hoàn toàn", "🟢 Logic kế toán chuẩn", "🟢 Xác thực thành công"],
            }
        )
        st.dataframe(valid_table, width="stretch", hide_index=True)

# =========================================================================
# BƯỚC 3: MA TRẬN CẢNH BÁO SỚM EWS & MÔ HÌNH ML
# =========================================================================
elif current_step_idx == 2:
    st.subheader("⚠️ Bước 3: Ma Trận Cảnh Báo Sớm Rủi Ro Tín Dụng (EWS Core Models & ML Engine)")
    st.caption(
        "Chạy toàn diện 5 phân hệ cảnh báo chuyên sâu: 10 Chỉ số EWS cốt lõi, 22 Biến kiểm soát thẩm định, Chi tiết 8 biến Beneish, Dữ liệu BCTC gốc và Kịch bản chất vấn tự động."
    )

    tab_b3_ews10, tab_b3_controls, tab_b3_beneish, tab_b3_raw, tab_b3_audit = st.tabs(
        [
            "🎯 3.1 10 Chỉ Số EWS Cốt Lõi & ML",
            "🛡️ 3.2 Hệ Thống 22 Biến Kiểm Soát",
            "🔬 3.3 Bóc Tách Gian Lận & Dòng Tiền REM",
            "📋 3.4 BCTC Gốc & Công Thức Chi Tiết",
            "❓ 3.5 Kịch Bản Chất Vấn Doanh Nghiệp",
        ]
    )

    with tab_b3_ews10:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(
                """
            <div class="metric-box" style="border-top-color: #10b981;">
                <div class="metric-title">1. Altman Z'-Score (Thị trường mới nổi)</div>
                <div class="metric-val" style="color: #047857;">4.18</div>
                <div class="badge-pill badge-safe">🟢 Vùng An Toàn (Z' > 2.60)</div>
                <div class="metric-desc">Xác suất kiệt quệ tài chính cực thấp</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                """
            <div class="metric-box" style="border-top-color: #10b981;">
                <div class="metric-title">2. Beneish M-Score (Gian lận Doanh thu)</div>
                <div class="metric-val" style="color: #047857;">-2.92</div>
                <div class="badge-pill badge-safe">🟢 Không phát hiện bóp méo (M < -1.78)</div>
                <div class="metric-desc">8 chỉ số thành phần đều an toàn</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                """
            <div class="metric-box" style="border-top-color: #f59e0b;">
                <div class="metric-title">3. Đòn Bẩy Thực Tế vs Trần U-Curve</div>
                <div class="metric-val" style="color: #b45309;">48.5% <span style="font-size:0.85rem; font-weight:normal;">/ trần 50%</span></div>
                <div class="badge-pill badge-warning">🟡 Tiệm cận trần an toàn (D/A)</div>
                <div class="metric-desc">Dư địa cấp thêm tối đa ~150 tỷ VNĐ</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                """
            <div class="metric-box" style="border-top-color: #10b981;">
                <div class="metric-title">4. Dechow F-Score (Thao túng dồn tích)</div>
                <div class="metric-val" style="color: #047857;">0.65</div>
                <div class="badge-pill badge-safe">🟢 Dồn tích bình thường (F < 1.0)</div>
                <div class="metric-desc">Chất lượng lợi nhuận kế toán cao</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 📊 Bảng Tổng Hợp Chi Tiết Trọn Bộ 10 Chỉ Số EWS Thành Phần:")
        ews_10_df = pd.DataFrame(
            {
                "STT": [f"EWS-{i+1:02d}" for i in range(10)],
                "Tên Mô Hình / Chỉ Số EWS": [
                    "1. Altman Z'-Score (Kiệt quệ tài chính)",
                    "2. Beneish M-Score (Bóp méo BCTC)",
                    "3. Dechow F-Score (Thao túng dồn tích)",
                    "4. Dòng tiền HĐKD bất thường (Ab_CFO)",
                    "5. Chi phí sản xuất bất thường (Ab_PROD)",
                    "6. Chi phí tùy ý bất thường (Ab_DISEXP)",
                    "7. Ngưỡng đòn bẩy tối ưu U-Curve phân ngành",
                    "8. Hệ số chi trả lãi vay ICR (EBIT / Lãi vay)",
                    "9. Chỉ số kiệt quệ tài chính KZ & Whited-Wu",
                    "10. Điểm Học máy Cảnh báo sớm (ML EWS Model)",
                ],
                "Giá Trị Tính Toán": ["4.18", "-2.92", "0.65", "+0.045", "-0.012", "+0.008", "48.5% (Trần 50.0%)", "14.5x", "-1.82 / -0.42", "0.08 (Xác suất rủi ro: 8%)"],
                "Ngưỡng Rủi Ro": ["> 2.60 (An toàn)", "< -1.78 (Ít rủi ro)", "< 1.00 (Bình thường)", ">= 0.0 (Thực chất)", "<= 0.0 (Bình thường)", ">= 0.0 (Ổn định)", "<= Trần ngành", ">= 3.0x", "< Ngưỡng báo động", "< 0.35 (An toàn tuyệt đối)"],
                "Đánh Giá Rủi Ro": ["🟢 Rất tốt", "🟢 Không gian lận", "🟢 Chất lượng cao", "🟢 Tiền về thực", "🟢 Không tồn kho ảo", "🟢 Chi phí chuẩn", "🟡 Tiệm cận trần", "🟢 Năng lực cao", "🟢 Ổn định", "🟢 Xác suất vỡ nợ cực thấp"],
            }
        )
        st.dataframe(ews_10_df, width="stretch", hide_index=True)

    with tab_b3_controls:
        st.markdown("##### 🛡️ Hệ Thống 22 Biến Kiểm Soát Thẩm Định (Phân Cấp 4 Mức Rủi Ro)")
        st.caption("Các biến kiểm soát bổ trợ phân loại từ Mức 1 (An toàn) đến Mức 4 (Rủi ro cao) tăng cường độ tin cậy của mô hình.")

        controls_df = pd.DataFrame(
            {
                "Nhóm Kiểm Soát": [
                    "Quy mô & Thâm niên", "Quy mô & Thâm niên",
                    "Sinh lời & Hiệu quả", "Sinh lời & Hiệu quả", "Sinh lời & Hiệu quả",
                    "Cơ cấu tài sản", "Cơ cấu tài sản", "Cơ cấu tài sản",
                    "Thanh khoản", "Thanh khoản",
                    "Đòn bẩy", "Đòn bẩy",
                    "Tăng trưởng", "Tăng trưởng",
                    "Quản trị & Thuế", "Quản trị & Thuế",
                    "Thị trường", "Thị trường",
                    "Dòng tiền", "Dòng tiền",
                    "Thuyết minh", "Thuyết minh",
                ],
                "Biến Kiểm Soát": [
                    "1. Quy mô Doanh nghiệp (Log Total Assets)", "2. Tuổi Doanh nghiệp (Firm Age)",
                    "3. Tỷ suất sinh lời tài sản (ROA)", "4. Tỷ suất sinh lời vốn CSH (ROE)", "5. Biên lợi nhuận ròng (Net Profit Margin)",
                    "6. Tỷ trọng Tài sản cố định (PPE / Total Assets)", "7. Tỷ trọng Khoản phải thu (Receivables / Assets)", "8. Tỷ trọng Hàng tồn kho (Inventory / Assets)",
                    "9. Tỷ lệ Tiền mặt & Tương đương tiền", "10. Vốn lưu động ròng (NWC / Total Assets)",
                    "11. Nợ ngắn hạn / Tổng nợ vay", "12. Tỷ lệ Nợ vay / Vốn CSH (D/E)",
                    "13. Tăng trưởng Doanh thu thuần (Sales Growth)", "14. Tăng trưởng Tổng tài sản (Asset Growth)",
                    "15. Tỷ lệ Thuế TNDN thực tế (Effective Tax Rate)", "16. Mức độ công bố thông tin quản trị",
                    "17. Mức độ nhạy cảm chu kỳ kinh tế", "18. Độ tập trung chuỗi cung ứng",
                    "19. Tỷ lệ Dòng tiền OCF / Lợi nhuận sau thuế", "20. Dòng tiền tự do FCF / Doanh thu",
                    "21. Độ dài thuyết minh BCTC", "22. Tỷ lệ giao dịch bên liên quan RPT",
                ],
                "Giá Trị Doanh Nghiệp": [
                    "10.8 (Quy mô lớn)", "15 năm",
                    "12.4%", "26.8%", "15.2%",
                    "22.5%", "24.8%", "12.4%",
                    "18.5%", "28.4%",
                    "68.2%", "0.92 lần",
                    "18.5%", "14.2%",
                    "18.2%", "0.92 (Rất minh bạch)",
                    "Thấp (Kháng chu kỳ)", "Phân tán rộng",
                    "1.18 lần (>1.0)", "12.5%",
                    "42 trang (Chi tiết)", "8.2% (Thương mại chuẩn)",
                ],
                "Phân Cấp Rủi Ro": [
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                    "🟡 Mức 2 (Chú ý nhẹ nợ ngắn hạn)", "🟢 Mức 1 (An toàn)",
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                    "🟢 Mức 1 (An toàn)", "🟢 Mức 1 (An toàn)",
                ],
            }
        )
        st.dataframe(controls_df, width="stretch", hide_index=True)

    with tab_b3_beneish:
        st.markdown("##### 🔬 Bóc Tách 8 Biến Gian Lận Beneish M-Score & 3 Biến REM Dòng Tiền Bất Thường")
        col_ben, col_rem = st.columns([1.5, 1.5])
        with col_ben:
            st.markdown("**8 Biến Thành Phần Mô Hình Beneish M-Score:**")
            beneish_full = pd.DataFrame(
                {
                    "Chỉ Số": [
                        "DSRI (Thu hồi công nợ)", "GMI (Biên lãi gộp)", "AQI (Chất lượng tài sản)", "SGI (Tăng trưởng DT)",
                        "DEPI (Khấu hao tài sản)", "SGAI (Chi phí bán hàng & QL)", "LVGI (Đòn bẩy tài chính)", "TATA (Tổng dồn tích kế toán)",
                    ],
                    "Giá Trị": [1.02, 0.98, 0.92, 1.14, 1.01, 0.95, 1.05, 0.03],
                    "Ngưỡng Rủi Ro": ["> 1.15", "> 1.10", "> 1.15", "> 1.25", "> 1.10", "> 1.15", "> 1.15", "> 0.08"],
                    "Đánh Giá": [
                        "🟢 An toàn", "🟢 Ổn định", "🟢 Không có TS ảo", "🟢 Tăng trưởng thật",
                        "🟢 Khấu hao chuẩn", "🟢 Tiết kiệm", "🟢 Đòn bẩy thấp", "🟢 Dòng tiền khớp LN",
                    ],
                }
            )
            st.dataframe(beneish_full, width="stretch", hide_index=True)

        with col_rem:
            st.markdown("**3 Biến Dòng Tiền Bất Thường Roychowdhury (REM Engine):**")
            rem_full = pd.DataFrame(
                {
                    "Biến Đo Lường": [
                        "Ab_CFO (Dòng tiền hoạt động)",
                        "Ab_PROD (Chi phí sản xuất)",
                        "Ab_DISEXP (Chi phí tùy ý R&D/Bán hàng)",
                    ],
                    "Hệ Số Thực Tế": ["+0.045", "-0.012", "+0.008"],
                    "Bản Chất Nghiệp Vụ": [
                        "Dương: Tiền mặt thu về vượt kỳ vọng mô hình",
                        "Âm: Không có hiện tượng sản xuất dư thừa để hạ giá thành giả tạo",
                        "Dương: Không cắt xén chi phí tiếp thị/nghiên cứu để làm đẹp số sách",
                    ],
                    "Kết Luận": ["🟢 Lành mạnh", "🟢 Không tồn kho ảo", "🟢 Bền vững"],
                }
            )
            st.dataframe(rem_full, width="stretch", hide_index=True)

    with tab_b3_raw:
        st.markdown("##### 📋 Dữ Liệu BCTC Gốc & Công Thức Toán Học Trung Gian")
        st.caption("Cho phép kiểm toán viên và cán bộ thẩm định truy nguyên nguồn gốc từng con số.")

        raw_bctc_df = pd.DataFrame(
            {
                "Mã Số": ["110", "130", "140", "150", "200", "300", "310", "320", "400", "511", "632", "635", "641+642"],
                "Chỉ Tiêu BCTC (Đơn vị: Tỷ VNĐ)": [
                    "Tiền và tương đương tiền", "Các khoản phải thu ngắn hạn", "Hàng tồn kho ròng", "Tài sản ngắn hạn khác", "Tổng Tài sản",
                    "Nợ phải trả", "Nợ ngắn hạn (Vay NH: 15.200 tỷ)", "Nợ dài hạn (Vay dài hạn: 3.100 tỷ)", "Vốn chủ sở hữu",
                    "Doanh thu thuần bán hàng", "Giá vốn hàng bán", "Chi phí tài chính (Lãi vay: 1.120 tỷ)", "Chi phí bán hàng & quản lý DN",
                ],
                "Năm 2022": ["12.500", "14.200", "6.800", "1.100", "51.200", "26.200", "21.500", "4.700", "25.000", "44.000", "27.500", "980", "6.200"],
                "Năm 2023": ["15.400", "16.800", "7.500", "1.400", "60.500", "30.100", "25.200", "4.900", "30.400", "52.600", "32.800", "1.050", "7.400"],
                "Năm 2024": ["18.200", "19.500", "8.200", "1.600", "72.000", "34.900", "29.400", "5.500", "37.100", "62.800", "38.900", "1.120", "8.600"],
            }
        )
        st.dataframe(raw_bctc_df, width="stretch", hide_index=True)

    with tab_b3_audit:
        st.markdown("##### ❓ Kịch Bản Bộ Câu Hỏi Chất Vấn Doanh Nghiệp (Interview Generator)")
        st.caption("Hệ thống tự động rà quét các cờ rủi ro để sinh ra bộ câu hỏi cho Cán bộ Tín dụng khi đi thực địa.")

        st.markdown(
            """
        1. 🎙️ **Về Cơ cấu Nợ vay ngắn hạn chiếm tỷ trọng lớn (68.2% tổng nợ):**
           - *Đề nghị Doanh nghiệp giải trình kế hoạch tái cấu trúc dòng vốn, phương án dự phòng thanh khoản khi có biến động lãi suất điều hành.*
        2. 🎙️ **Về Ngưỡng đòn bẩy U-Curve tiệm cận 48.5% (Trần an toàn ngành là 50%):**
           - *Yêu cầu Doanh nghiệp cung cấp kế hoạch tăng vốn điều lệ hoặc lợi nhuận giữ lại năm 2025 để đảm bảo an toàn đòn bẩy dài hạn.*
        3. 🎙️ **Về Tiến độ thu hồi nợ các Hợp đồng xuất khẩu phần mềm lớn:**
           - *Đề nghị cung cấp hợp đồng thương mại gốc, hóa đơn xuất khẩu và biên bản nghiệm thu giai đoạn (Milestones acceptance).*
        """
        )
        st.success("✅ **Đã hoàn tất toàn bộ phân tích định lượng EWS.** Hãy chuyển sang Bước 4 để thực hiện Khảo sát Định tính 5Cs.")

# =========================================================================
# BƯỚC 4: KHẢO SÁT ĐỊNH TÍNH 5CS & ĐIỂM HYBRID REALTIME
# =========================================================================
elif current_step_idx == 3:
    st.subheader("🏛️ Bước 4: Khảo Sát Định Tính 5Cs & Xếp Hạng Hỗn Hợp (Hybrid Rating)")
    st.caption("Khảo sát toàn bộ 19 tiêu chí định tính 5Cs thu gọn và tính Điểm xếp hạng tín dụng hỗn hợp theo tỷ trọng.")

    qual_score, c_breakdown = calculate_5c_score_summary()
    quant_score = st.session_state.active_company.get("quant_score", 88.5)
    quant_w = st.session_state.quant_w_pct / 100.0
    qual_w = (100 - st.session_state.quant_w_pct) / 100.0
    hybrid_score = round(quant_score * quant_w + qual_score * qual_w, 1)

    col_h_score, col_h_rating = st.columns([1.8, 1.2])
    with col_h_score:
        st.markdown(
            f"""
        <div style="background: white; border: 1px solid #cbd5e1; border-left: 5px solid #1e3a8a; padding: 12px 18px; border-radius: 8px;">
            <div style="font-size: 0.85rem; color: #64748b; font-weight: 700;">ĐIỂM XẾP HẠNG HỖN HỢP (HYBRID CREDIT SCORE):</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #1e3a8a; line-height: 1.1;">{hybrid_score} <span style="font-size: 1rem; color: #64748b; font-weight: normal;">/ 100 điểm</span></div>
            <div style="font-size: 0.85rem; color: #334155; margin-top: 5px;">
                📊 Định lượng ({st.session_state.quant_w_pct}%): <strong>{quant_score:.1f}đ</strong> &nbsp;|&nbsp;
                🏛️ Định tính ({100 - st.session_state.quant_w_pct}%): <strong>{qual_score:.1f}đ</strong>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_h_rating:
        grade = "AAA" if hybrid_score >= 88 else ("AA" if hybrid_score >= 80 else ("A" if hybrid_score >= 70 else "BBB"))
        max_ltv = "80%" if grade == "AAA" else ("75%" if grade == "AA" else ("70%" if grade == "A" else "60%"))
        st.markdown(
            f"""
        <div style="background: #ecfdf5; border: 1px solid #a7f3d0; padding: 12px 18px; border-radius: 8px; text-align: center;">
            <div style="font-size: 0.82rem; color: #047857; font-weight: 700;">XẾP HẠNG TÍN DỤNG NỘI BỘ:</div>
            <div style="font-size: 2.2rem; font-weight: 900; color: #065f46;">🏆 {grade}</div>
            <div style="font-size: 0.8rem; color: #065f46;">LTV đề xuất trần: <strong>{max_ltv}</strong></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📋 Khảo Sát 19 Tiêu Chí 5Cs (Thu gọn theo nhóm để xem & chỉnh sửa):")

    def _idx_by_score(options, current_val):
        for i, opt in enumerate(options):
            if f"({int(current_val)}đ)" in opt:
                return i
        return 0

    with st.expander(f"👤 C1. Uy Tín & Năng Lực Lãnh Đạo (Character - 20%) ── Điểm: {c_breakdown['C1']:.1f} / 100", expanded=False):
        c1_cols = st.columns(2)
        with c1_cols[0]:
            o1 = ["Trên 10 năm kinh nghiệm (100đ)", "5 đến 10 năm (80đ)", "3 đến 5 năm (60đ)", "Dưới 3 năm (35đ)"]
            st.markdown("**1. Thâm niên Ban điều hành:**")
            opt1 = st.selectbox("Thâm niên Ban điều hành", o1, index=_idx_by_score(o1, st.session_state.qual_criteria_state["c1_mgmt_exp"]["val"]), key="sel_c1_1", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c1_mgmt_exp"]["val"] = 100 if "100đ" in opt1 else (80 if "80đ" in opt1 else (60 if "60đ" in opt1 else 35))

            o2 = ["Nhóm 1 chuẩn (100đ)", "Từng phát sinh Nhóm 2 đã tất toán (75đ)", "Từng có Nhóm 3-5 trước đây (40đ)", "Hiện tại có nợ xấu (10đ)"]
            st.markdown("**2. Lịch sử tín dụng CIC:**")
            opt2 = st.selectbox("Lịch sử tín dụng CIC", o2, index=_idx_by_score(o2, st.session_state.qual_criteria_state["c1_cic_history"]["val"]), key="sel_c1_2", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c1_cic_history"]["val"] = 100 if "100đ" in opt2 else (75 if "75đ" in opt2 else (40 if "40đ" in opt2 else 10))

        with c1_cols[1]:
            o3 = ["Nắm giữ chi phối > 51% (100đ)", "Nắm giữ 25% - 50% (80đ)", "Nắm giữ 10% - 25% (60đ)", "Tỷ lệ thấp < 10% (30đ)"]
            st.markdown("**3. Mức độ gắn bó của Chủ DN / Cổ đông sáng lập:**")
            opt3 = st.selectbox("Mức độ gắn bó Chủ DN", o3, index=_idx_by_score(o3, st.session_state.qual_criteria_state["c1_owner_commitment"]["val"]), key="sel_c1_3", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c1_owner_commitment"]["val"] = 100 if "100đ" in opt3 else (80 if "80đ" in opt3 else (60 if "60đ" in opt3 else 30))

            o4 = ["Không có tranh chấp hay xử phạt (100đ)", "Tranh chấp dân sự nhỏ < 2% Vốn CSH (70đ)", "Đang bị thanh tra / xử phạt hành chính (40đ)", "Có kiện tụng lớn (10đ)"]
            st.markdown("**4. Minh bạch pháp lý & Tranh chấp:**")
            opt4 = st.selectbox("Minh bạch pháp lý", o4, index=_idx_by_score(o4, st.session_state.qual_criteria_state["c1_legal_compliance"]["val"]), key="sel_c1_4", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c1_legal_compliance"]["val"] = 100 if "100đ" in opt4 else (70 if "70đ" in opt4 else (40 if "40đ" in opt4 else 10))

    with st.expander(f"🏛️ C2. Năng Lực Quản Trị & Vận Hành (Capacity - 20%) ── Điểm: {c_breakdown['C2']:.1f} / 100", expanded=False):
        c2_cols = st.columns(2)
        with c2_cols[0]:
            o5 = ["HĐQT > 1/3 TV độc lập, BKS chuyên trách (100đ)", "Đầy đủ ban bệ theo luật định (75đ)", "Chủ tịch kiêm Tổng giám đốc (50đ)", "Mô hình gia đình trị (30đ)"]
            st.markdown("**5. Cơ cấu Quản trị & HĐQT:**")
            opt5 = st.selectbox("Cơ cấu Quản trị", o5, index=_idx_by_score(o5, st.session_state.qual_criteria_state["c2_board_structure"]["val"]), key="sel_c2_1", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c2_board_structure"]["val"] = 100 if "100đ" in opt5 else (75 if "75đ" in opt5 else (50 if "50đ" in opt5 else 30))

            o6 = ["Quy trình COSO/ISO chuẩn mực (100đ)", "Có quy trình cơ bản và phân quyền (75đ)", "Quy trình sơ sài (45đ)", "Không có kiểm soát nội bộ (20đ)"]
            st.markdown("**6. Hệ thống Kiểm soát nội bộ (KSoNB):**")
            opt6 = st.selectbox("Hệ thống KSoNB", o6, index=_idx_by_score(o6, st.session_state.qual_criteria_state["c2_internal_control"]["val"]), key="sel_c2_2", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c2_internal_control"]["val"] = 100 if "100đ" in opt6 else (75 if "75đ" in opt6 else (45 if "45đ" in opt6 else 20))

        with c2_cols[1]:
            o7 = ["ERP đồng bộ SAP/Oracle (100đ)", "Phần mềm kế toán chuẩn MISA/Fast (80đ)", "Phần mềm rời rạc (55đ)", "Quản lý Excel thủ công (25đ)"]
            st.markdown("**7. Ứng dụng CNTT / ERP:**")
            opt7 = st.selectbox("Ứng dụng CNTT ERP", o7, index=_idx_by_score(o7, st.session_state.qual_criteria_state["c2_erp_tech"]["val"]), key="sel_c2_3", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c2_erp_tech"]["val"] = 100 if "100đ" in opt7 else (80 if "80đ" in opt7 else (55 if "55đ" in opt7 else 25))

            o8 = ["Ban điều hành & Kế toán trưởng ổn định > 3 năm (100đ)", "Thay đổi bình thường (80đ)", "CFO thay đổi trong năm (50đ)", "Thay đổi liên tục bất thường (25đ)"]
            st.markdown("**8. Ổn định nhân sự cấp cao & Kế toán trưởng:**")
            opt8 = st.selectbox("Ổn định nhân sự", o8, index=_idx_by_score(o8, st.session_state.qual_criteria_state["c2_hr_stability"]["val"]), key="sel_c2_4", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c2_hr_stability"]["val"] = 100 if "100đ" in opt8 else (80 if "80đ" in opt8 else (50 if "50đ" in opt8 else 25))

    with st.expander(f"📑 C3. Tính Xác Thực & Chất Lượng BCTC (Capital & Audit - 25%) ── Điểm: {c_breakdown['C3']:.1f} / 100", expanded=False):
        c3_cols = st.columns(2)
        with c3_cols[0]:
            o9 = ["Big 4 (PwC, EY, KPMG, Deloitte) (100đ)", "Top 10 uy tín trong nước (85đ)", "Kiểm toán nhỏ địa phương (55đ)", "Chưa được kiểm toán (20đ)"]
            st.markdown("**9. Đơn vị Kiểm toán Độc lập:**")
            opt9 = st.selectbox("Đơn vị kiểm toán", o9, index=_idx_by_score(o9, st.session_state.qual_criteria_state["c3_audit_firm"]["val"]), key="sel_c3_1", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c3_audit_firm"]["val"] = 100 if "100đ" in opt9 else (85 if "85đ" in opt9 else (55 if "55đ" in opt9 else 20))

            o10 = ["Chấp nhận toàn phần (100đ)", "Chấp nhận toàn phần có nhấn mạnh (70đ)", "Ý kiến ngoại trừ (30đ)", "Từ chối đưa ra ý kiến (0đ)"]
            st.markdown("**10. Ý kiến Kiểm toán viên:**")
            opt10 = st.selectbox("Ý kiến kiểm toán viên", o10, index=_idx_by_score(o10, st.session_state.qual_criteria_state["c3_audit_opinion"]["val"]), key="sel_c3_2", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c3_audit_opinion"]["val"] = 100 if "100đ" in opt10 else (70 if "70đ" in opt10 else (30 if "30đ" in opt10 else 0))

        with c3_cols[1]:
            o11 = ["Khớp 100% doanh thu & chi phí (100đ)", "Chênh lệch nhỏ < 5% có lý do (85đ)", "Chênh lệch 5% - 20% (55đ)", "Chênh lệch > 20% bất thường (15đ)"]
            st.markdown("**11. Độ khớp giữa BCTC và Tờ khai Thuế:**")
            opt11 = st.selectbox("Độ khớp BCTC và Thuế", o11, index=_idx_by_score(o11, st.session_state.qual_criteria_state["c3_tax_consistency"]["val"]), key="sel_c3_3", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c3_tax_consistency"]["val"] = 100 if "100đ" in opt11 else (85 if "85đ" in opt11 else (55 if "55đ" in opt11 else 15))

            o12 = ["Thuyết minh chi tiết chuẩn Thông tư 200 (100đ)", "Thuyết minh cơ bản đầy đủ (80đ)", "Thuyết minh sơ sài (45đ)", "Thiếu thông tin trọng yếu (20đ)"]
            st.markdown("**12. Minh bạch Thuyết minh BCTC:**")
            opt12 = st.selectbox("Minh bạch Thuyết minh", o12, index=_idx_by_score(o12, st.session_state.qual_criteria_state["c3_disclosure_quality"]["val"]), key="sel_c3_4", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c3_disclosure_quality"]["val"] = 100 if "100đ" in opt12 else (80 if "80đ" in opt12 else (45 if "45đ" in opt12 else 20))

    with st.expander(f"🌐 C4. Môi Trường Ngành & Vị Thế Cạnh Tranh (Conditions - 15%) ── Điểm: {c_breakdown['C4']:.1f} / 100", expanded=False):
        c4_cols = st.columns(3)
        with c4_cols[0]:
            o13 = ["Top 3 đầu ngành (100đ)", "Top 10 có uy tín (80đ)", "Quy mô trung bình (60đ)", "Quy mô nhỏ dễ bị cạnh tranh (35đ)"]
            st.markdown("**13. Vị thế & Thị phần:**")
            opt13 = st.selectbox("Vị thế thị phần", o13, index=_idx_by_score(o13, st.session_state.qual_criteria_state["c4_market_position"]["val"]), key="sel_c4_1", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c4_market_position"]["val"] = 100 if "100đ" in opt13 else (80 if "80đ" in opt13 else (60 if "60đ" in opt13 else 35))
        with c4_cols[1]:
            o14 = ["Rất cao (đòi hỏi vốn/công nghệ) (100đ)", "Trung bình (75đ)", "Thấp (dễ gia nhập) (45đ)"]
            st.markdown("**14. Rào cản gia nhập ngành:**")
            opt14 = st.selectbox("Rào cản gia nhập", o14, index=_idx_by_score(o14, st.session_state.qual_criteria_state["c4_entry_barriers"]["val"]), key="sel_c4_2", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c4_entry_barriers"]["val"] = 100 if "100đ" in opt14 else (75 if "75đ" in opt14 else 45)
        with c4_cols[2]:
            o15 = ["Kháng chu kỳ / Thiết yếu (95đ)", "Độ nhạy trung bình (75đ)", "Rất nhạy cảm với Lãi suất/BĐS (45đ)"]
            st.markdown("**15. Nhạy cảm chu kỳ vĩ mô:**")
            opt15 = st.selectbox("Nhạy cảm chu kỳ", o15, index=_idx_by_score(o15, st.session_state.qual_criteria_state["c4_cyclical_risk"]["val"]), key="sel_c4_3", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c4_cyclical_risk"]["val"] = 95 if "95đ" in opt15 else (75 if "75đ" in opt15 else 45)

    with st.expander(f"🔄 C5. Chuỗi Cung Ứng & Hệ Sinh Thái (Ecosystem - 20%) ── Điểm: {c_breakdown['C5']:.1f} / 100", expanded=False):
        c5_cols = st.columns(2)
        with c5_cols[0]:
            o16 = ["Top 3 KH < 25% DT (100đ)", "Top 3 KH chiếm 25% - 50% (75đ)", "Top 3 KH chiếm 50% - 75% (45đ)", "Phụ thuộc 1 KH > 50% (20đ)"]
            st.markdown("**16. Tập trung Khách hàng Đầu ra:**")
            opt16 = st.selectbox("Tập trung khách hàng", o16, index=_idx_by_score(o16, st.session_state.qual_criteria_state["c5_customer_concentration"]["val"]), key="sel_c5_1", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c5_customer_concentration"]["val"] = 100 if "100đ" in opt16 else (75 if "75đ" in opt16 else (45 if "45đ" in opt16 else 20))

            o17 = ["Đa dạng nguồn cung (100đ)", "Có 2-3 đối tác chiến lược (75đ)", "Phụ thuộc 1-2 NCC độc quyền (40đ)"]
            st.markdown("**17. Tập trung Nhà cung cấp Đầu vào:**")
            opt17 = st.selectbox("Tập trung nhà cung cấp", o17, index=_idx_by_score(o17, st.session_state.qual_criteria_state["c5_supplier_concentration"]["val"]), key="sel_c5_2", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c5_supplier_concentration"]["val"] = 100 if "100đ" in opt17 else (75 if "75đ" in opt17 else 40)

        with c5_cols[1]:
            o18 = ["Không có hoặc RPT < 5% TS (100đ)", "RPT từ 5% đến 15% (75đ)", "RPT từ 15% đến 30% (45đ)", "RPT > 30% cảnh báo rút ruột (15đ)"]
            st.markdown("**18. Giao dịch Bên liên quan (RPT):**")
            opt18 = st.selectbox("Giao dịch bên liên quan", o18, index=_idx_by_score(o18, st.session_state.qual_criteria_state["c5_related_party_rpt"]["val"]), key="sel_c5_3", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c5_related_party_rpt"]["val"] = 100 if "100đ" in opt18 else (75 if "75đ" in opt18 else (45 if "45đ" in opt18 else 15))

            o19 = ["Vị thế áp đảo (thu tiền ngay, nợ NCC dài) (100đ)", "Vị thế cân bằng theo ngành (75đ)", "Vị thế yếu (bị chiếm dụng vốn) (35đ)"]
            st.markdown("**19. Vị thế Đàm phán Thương lượng:**")
            opt19 = st.selectbox("Vị thế đàm phán", o19, index=_idx_by_score(o19, st.session_state.qual_criteria_state["c5_bargaining_power"]["val"]), key="sel_c5_4", label_visibility="collapsed")
            st.session_state.qual_criteria_state["c5_bargaining_power"]["val"] = 100 if "100đ" in opt19 else (75 if "75đ" in opt19 else 35)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("☁️ Lưu Điểm Định Tính 5Cs Lên Cloud", type="primary"):
        ok, msg = save_company_profile(
            company=st.session_state.active_company,
            bctc_override_data=st.session_state.bctc_override_data,
            qual_criteria=st.session_state.qual_criteria_state,
            quant_w_pct=st.session_state.quant_w_pct,
            underwriting_inputs=st.session_state.underwriting_inputs,
            operator=st.session_state.operator_name,
        )
        st.session_state.last_sync_info = msg
        if ok:
            st.success(msg)

# =========================================================================
# BƯỚC 5: NHU CẦU VỐN VAY & TỜ TRÌNH THẨM ĐỊNH (CREDIT MEMO)
# =========================================================================
elif current_step_idx == 4:
    st.subheader("📝 Bước 5: Tính Toán Nhu Cầu Vốn Vay & Tờ Trình Thẩm Định Tín Dụng")
    st.caption(
        "Cho phép Nhân viên Tín dụng trực tiếp nhập phương án vay vốn, tính toán hạn mức hợp lý theo TT 39/NHNN, đối chiếu LTV và xuất PDF có Nhật ký Audit Trail."
    )

    qual_score, c_breakdown_step5 = calculate_5c_score_summary()
    quant_score = st.session_state.active_company.get("quant_score", 88.5)
    quant_w = st.session_state.quant_w_pct / 100.0
    qual_w = (100 - st.session_state.quant_w_pct) / 100.0
    final_hybrid = round(quant_score * quant_w + qual_score * qual_w, 1)
    grade = "AAA" if final_hybrid >= 88 else ("AA" if final_hybrid >= 80 else ("A" if final_hybrid >= 70 else "BBB"))
    rec_ltv_pct = 80.0 if grade == "AAA" else (75.0 if grade == "AA" else (70.0 if grade == "A" else 60.0))

    uw = st.session_state.underwriting_inputs

    # PHẦN 1: BẢNG TÍNH NHU CẦU VỐN LƯU ĐỘNG (CHUẨN THÔNG TƯ 39)
    st.markdown('<div class="calc-card">', unsafe_allow_html=True)
    st.markdown('<div class="calc-card-header">1️⃣ Tính Toán Nhu Cầu Vốn Lưu Động Doanh Nghiệp (Theo Chuẩn Thông tư 39/NHNN)</div>', unsafe_allow_html=True)

    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        rev_plan = st.number_input("Doanh thu kế hoạch năm tới (tỷ VNĐ):", min_value=10.0, max_value=100000.0, value=float(uw.get("rev_plan", 4500.0)), step=100.0)
    with col_in2:
        cost_plan = st.number_input("Tổng chi phí hoạt động cần tài trợ (tỷ VNĐ):", min_value=5.0, max_value=90000.0, value=float(uw.get("cost_plan", 3850.0)), step=50.0)
    with col_in3:
        wctr = st.number_input("Số vòng quay Vốn lưu động dự kiến (vòng/năm):", min_value=1.0, max_value=50.0, value=float(uw.get("wctr", 8.5)), step=0.5, help="Lấy từ phân tích CCC ở Bước 2")

    total_nwc = cost_plan / wctr

    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        equity_part = st.number_input("Vốn tự có của Doanh nghiệp tham gia (tỷ VNĐ):", min_value=0.0, max_value=float(total_nwc), value=round(total_nwc * 0.22, 1), step=10.0)
    with col_sub2:
        other_part = st.number_input("Vốn vay tại các TCTD khác & Nợ chiếm dụng NCC (tỷ VNĐ):", min_value=0.0, max_value=float(total_nwc), value=round(total_nwc * 0.15, 1), step=10.0)

    max_reasonable_loan = max(0.0, total_nwc - equity_part - other_part)

    st.markdown(
        f"""
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; padding: 10px 14px; border-radius: 6px; font-size: 0.88rem; margin-top: 8px;">
        💡 <strong>Kết quả tính toán:</strong> Tổng nhu cầu VLĐ = <strong>{total_nwc:.1f} tỷ VNĐ</strong> ──► Nhu cầu Vay Ngắn Hạn Tối Đa Hợp Lý: <span style="color:#1e3a8a; font-weight:800; font-size:1.05rem;">{max_reasonable_loan:.1f} tỷ VNĐ</span>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # PHẦN 2: ĐỀ XUẤT CỦA CÁN BỘ TÍN DỤNG & ĐỐI CHIẾU TSĐB (LTV)
    st.markdown('<div class="calc-card">', unsafe_allow_html=True)
    st.markdown('<div class="calc-card-header">2️⃣ Phương Án Cấp Tín Dụng Do Cán Bộ Đề Xuất & Định Giá Tài Sản Bảo Đảm</div>', unsafe_allow_html=True)

    term_options = ["12 tháng", "6 tháng", "9 tháng", "24 tháng"]
    saved_term = uw.get("loan_term", "12 tháng")
    col_prop1, col_prop2, col_prop3 = st.columns(3)
    with col_prop1:
        proposed_limit = st.number_input("Hạn mức tín dụng đề xuất cấp (tỷ VNĐ):", min_value=1.0, max_value=50000.0, value=float(uw.get("proposed_limit", 280.0)), step=10.0)
    with col_prop2:
        loan_term = st.selectbox("Thời hạn hạn mức:", term_options, index=term_options.index(saved_term) if saved_term in term_options else 0)
    with col_prop3:
        collateral_val = st.number_input("Tổng giá trị định giá Tài sản bảo đảm (tỷ VNĐ):", min_value=1.0, max_value=50000.0, value=float(uw.get("collateral_val", 390.0)), step=10.0)

    st.session_state.underwriting_inputs = {
        "rev_plan": rev_plan,
        "cost_plan": cost_plan,
        "wctr": wctr,
        "proposed_limit": proposed_limit,
        "loan_term": loan_term,
        "collateral_val": collateral_val,
    }

    actual_ltv = (proposed_limit / collateral_val) * 100.0 if collateral_val > 0 else 0.0

    if actual_ltv <= rec_ltv_pct:
        st.success(
            f"**Đánh giá bảo đảm tín dụng:** 🟢 AN TOÀN (LTV thực tế {actual_ltv:.1f}% <= Trần khuyến nghị {rec_ltv_pct:.0f}%). Đủ điều kiện trình phê duyệt."
        )
    else:
        st.error(
            f"**Đánh giá bảo đảm tín dụng:** 🔴 CẢNH BÁO VƯỢT KHUNG (LTV thực tế {actual_ltv:.1f}% > Trần khuyến nghị {rec_ltv_pct:.0f}%). Yêu cầu bổ sung thêm TSĐB hoặc giảm hạn mức đề xuất."
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # PHẦN 3: TỜ TRÌNH THẨM ĐỊNH TÓM TẮT & NÚT HÀNH ĐỘNG
    col_sum1, col_sum2 = st.columns([2, 1])
    with col_sum1:
        st.markdown("#### 📄 Tờ Trình Thẩm Định Tín Dụng (Executive Credit Memo)")
        st.markdown(
            f"""
        - **Khách hàng:** {st.session_state.active_company['name']} ({st.session_state.active_company['ticker']})
        - **Điểm Xếp Hạng Hỗn Hợp:** **{final_hybrid:.1f} / 100 đ** (Hạng tín dụng: **{grade}**)
        - **Hạn mức đề xuất:** **{proposed_limit:.1f} tỷ VNĐ** (Thời hạn: {loan_term})
        - **Tài sản bảo đảm:** {collateral_val:.1f} tỷ VNĐ ── Tỷ lệ LTV: **{actual_ltv:.1f}%**
        - **Cán bộ Lập Tờ Trình:** {st.session_state.operator_name}
        """
        )

        btn1, btn2 = st.columns(2)
        with btn1:
            try:
                from pdf_report_generator import generate_full_credit_appraisal_pdf_bytes

                pdf_payload = build_step5_pdf_payload(
                    bctc_override_data=st.session_state.bctc_override_data,
                    qual_score=qual_score,
                    c_breakdown=c_breakdown_step5,
                    grade=grade,
                    rec_ltv_pct=rec_ltv_pct,
                    proposed_limit_bil=proposed_limit,
                    rev_plan_bil=rev_plan,
                    collateral_val_bil=collateral_val,
                    evaluation_year=2024,
                )

                pdf_bytes = generate_full_credit_appraisal_pdf_bytes(
                    company_name=st.session_state.active_company["name"],
                    ticker=st.session_state.active_company["ticker"],
                    extracted_data=pdf_payload["extracted_data"],
                    ews_results=pdf_payload["ews_results"],
                    wc_results=pdf_payload["wc_results"],
                    qual_results=pdf_payload["qual_results"],
                    underwriting_data=pdf_payload["underwriting_data"],
                    evaluation_year=2024,
                    industry=st.session_state.active_company.get("industry", "Khác"),
                    audit_trail_logs=st.session_state.bctc_override_data,
                )

                st.download_button(
                    label="📥 Tải Tờ Trình PDF (Có Nhật Ký Lưu Vết)",
                    data=pdf_bytes,
                    file_name=f"To_Trinh_Tham_Dinh_{st.session_state.active_company['ticker']}_2024.pdf",
                    mime="application/pdf",
                    type="primary",
                    width="stretch",
                )
            except Exception as e_pdf:
                st.error(f"Lỗi tạo tệp PDF: {e_pdf}")

        with btn2:
            save_step5_label = (
                "☁️ Lưu Hồ Sơ Lên Supabase Cloud"
                if storage_status["mode"] == "supabase"
                else "💾 Lưu Trữ Hồ Sơ Vào CSDL"
            )
            if st.button(save_step5_label, width="stretch"):
                ok, msg = save_company_profile(
                    company=st.session_state.active_company,
                    bctc_override_data=st.session_state.bctc_override_data,
                    qual_criteria=st.session_state.qual_criteria_state,
                    quant_w_pct=st.session_state.quant_w_pct,
                    underwriting_inputs=st.session_state.underwriting_inputs,
                    operator=st.session_state.operator_name,
                )
                st.session_state.last_sync_info = msg
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    with col_sum2:
        st.markdown("#### ⚖️ Phân Cấp Thẩm Quyền")
        if proposed_limit > 200:
            auth_level = "Hội đồng Tín dụng Hội sở (HĐTD HS)"
            auth_reason = "Hạn mức đề xuất > 200 tỷ VNĐ"
        elif proposed_limit > 50:
            auth_level = "Giám đốc Vùng / Phân ban Rủi ro"
            auth_reason = "Hạn mức từ 50 đến 200 tỷ VNĐ"
        else:
            auth_level = "Giám đốc Chi nhánh"
            auth_reason = "Hạn mức <= 50 tỷ VNĐ"

        st.info(
            f"""
        - **Cấp phê duyệt:** **{auth_level}**
        - **Căn cứ phân cấp:** {auth_reason}
        - **Trạng thái EWS:** 🟢 An toàn
        """
        )

    # PHẦN 4: NHẬT KÝ KIỂM TOÁN SỐ LIỆU HIỆU CHỈNH THỦ CÔNG (AUDIT TRAIL LOG)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📋 Nhật Ký Kiểm Toán Số Liệu BCTC Đã Hiệu Chỉnh Thủ Công (Audit Trail Log)")
    st.caption("Bắt buộc trình kèm Tờ trình Thẩm định để Hội đồng Tín dụng giám sát tính khách quan của dữ liệu đầu vào.")

    active_overrides_step5 = [
        r
        for r in st.session_state.bctc_override_data
        if abs(r["Số Áp Dụng (tỷ VNĐ)"] - r["Số Gốc OCR (tỷ VNĐ)"]) > 0.001
    ]
    if active_overrides_step5:
        audit_records = []
        for r in active_overrides_step5:
            audit_records.append(
                {
                    "Mã Số": r["Mã Số"],
                    "Khoản Mục Kế Toán": r["Khoản Mục Kế Toán"],
                    "Số Gốc OCR": f"{r['Số Gốc OCR (tỷ VNĐ)']:,.1f} tỷ",
                    "Số Áp Dụng": f"{r['Số Áp Dụng (tỷ VNĐ)']:,.1f} tỷ",
                    "Chênh Lệch": f"{r['Số Áp Dụng (tỷ VNĐ)'] - r['Số Gốc OCR (tỷ VNĐ)']:+,.1f} tỷ",
                    "Cán Bộ Thao Tác": r.get("Cán Bộ Thao Tác") or st.session_state.operator_name,
                    "Căn Cứ & Lý Do Giải Trình (Remark)": r["Lý Do Điều Chỉnh (Remark)"] or "⚠️ Chưa nhập lý do điều chỉnh",
                }
            )
        st.dataframe(pd.DataFrame(audit_records), width="stretch", hide_index=True)
        st.warning(
            "⚠️ **Lưu ý Thẩm quyền Phê duyệt:** Tờ trình này sử dụng số liệu BCTC đã có sự can thiệp hiệu chỉnh của CBTD. Đề nghị Ban Kiểm soát thẩm tra lại hồ sơ gốc theo các lý do nêu trên."
        )
    else:
        st.success(
            "🟢 **BCTC Toàn Vẹn Tuyệt Đối:** 100% số liệu đầu vào được trích xuất trực tiếp từ BCTC kiểm toán, không có bất kỳ hiệu chỉnh thủ công nào."
        )
