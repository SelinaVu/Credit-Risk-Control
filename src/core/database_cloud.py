"""
FinTrust EWS v2.1 - Lớp Lưu Trữ Cloud Đa Quốc Gia (Supabase PostgreSQL + Auto-Fallback SQLite)
- Tự động kết nối Supabase PostgreSQL khi có cấu hình st.secrets["supabase"] hoặc biến môi trường SUPABASE_URL / SUPABASE_KEY.
- Tự động lùi về SQLite cục bộ khi chạy offline trên máy cá nhân không cấu hình Cloud.
- Hỗ trợ lưu vết đầy đủ Audit Trail (Số gốc OCR, Số áp dụng, Lý do Remark, Cán bộ thao tác, Thời gian UTC).
- Hỗ trợ Xuất / Nhập Gói Hồ Sơ (.json) để chia sẻ nhanh hoặc sao lưu độc lập.
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

try:
    from supabase import Client, create_client
    HAS_SUPABASE_SDK = True
except ImportError:
    Client = Any  # type: ignore
    create_client = None
    HAS_SUPABASE_SDK = False


# ---------------------------------------------------------------------------
# CẤU HÌNH ĐƯỜNG DẪN & BÍ MẬT (KHÔNG HARDCODE CREDENTIALS)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "fintrust_cloud_cache.db")


def _read_supabase_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Đọc Supabase URL và Key từ st.secrets hoặc biến môi trường."""
    url: Optional[str] = None
    key: Optional[str] = None

    try:
        if "supabase" in st.secrets:
            sec = st.secrets["supabase"]
            url = str(sec.get("url", "")).strip() or None
            key = str(sec.get("key", "")).strip() or None
    except Exception:
        pass

    if not url:
        url = os.environ.get("SUPABASE_URL", "").strip() or None
    if not key:
        key = os.environ.get("SUPABASE_KEY", "").strip() or None

    # Bỏ qua giá trị placeholder mẫu chưa được thay thế
    if url and "YOUR_PROJECT" in url.upper():
        return None, None
    if key and "YOUR_ANON_KEY" in key.upper():
        return None, None

    return url, key


def get_team_passcode() -> Optional[str]:
    """Đọc mật khẩu truy cập chung của nhóm từ st.secrets['auth']['team_passcode'] hoặc env."""
    try:
        if "auth" in st.secrets:
            code = str(st.secrets["auth"].get("team_passcode", "")).strip()
            if code and code.upper() != "YOUR_TEAM_PASSCODE":
                return code
    except Exception:
        pass

    env_code = os.environ.get("FINTRUST_TEAM_PASSCODE", "").strip()
    return env_code or None


@st.cache_resource(show_spinner=False)
def _build_supabase_client(url: str, key: str) -> Optional[Client]:
    """Khởi tạo và cache kết nối Supabase Client dùng chung cho ứng dụng."""
    if not HAS_SUPABASE_SDK or create_client is None:
        return None
    return create_client(url, key)


def get_supabase_client() -> Optional[Client]:
    """Trả về Supabase Client nếu đã cấu hình đầy đủ, ngược lại trả None."""
    url, key = _read_supabase_credentials()
    if not url or not key or not HAS_SUPABASE_SDK:
        return None
    try:
        return _build_supabase_client(url, key)
    except Exception:
        return None


def get_storage_status() -> Dict[str, Any]:
    """Kiểm tra trạng thái kết nối kho lưu trữ hiện tại (Supabase Cloud hay SQLite Local)."""
    url, key = _read_supabase_credentials()
    if url and key:
        if not HAS_SUPABASE_SDK:
            return {
                "mode": "sqlite",
                "connected": False,
                "label": "SQLite Cục Bộ (thiếu thư viện supabase)",
                "detail": "Cần cài đặt `supabase>=2.0.0` để kích hoạt Cloud Database.",
            }
        client = get_supabase_client()
        if client is not None:
            try:
                client.table("companies").select("ticker").limit(1).execute()
                return {
                    "mode": "supabase",
                    "connected": True,
                    "label": "Supabase Cloud (PostgreSQL)",
                    "detail": "Đồng bộ thời gian thực đa quốc gia.",
                }
            except Exception as exc:
                return {
                    "mode": "sqlite",
                    "connected": False,
                    "label": "SQLite Dự Phòng (Supabase chưa sẵn sàng)",
                    "detail": f"Chưa truy vấn được bảng trên Supabase (hãy chạy file supabase_schema.sql): {exc}",
                }
    return {
        "mode": "sqlite",
        "connected": True,
        "label": "SQLite Cục Bộ (Chế độ Offline / Demo)",
        "detail": "Chưa cấu hình st.secrets['supabase']. Dữ liệu lưu tạm tại máy chủ cục bộ.",
    }


# ---------------------------------------------------------------------------
# LỚP SQLITE DỰ PHÒNG (OFFLINE / LOCAL FALLBACK)
# ---------------------------------------------------------------------------
def _get_sqlite_conn() -> sqlite3.Connection:
    """Mở kết nối SQLite cục bộ, tự fallback sang /tmp nếu thư mục gốc chỉ đọc (Cloud readonly)."""
    db_path = DEFAULT_SQLITE_PATH
    try:
        conn = sqlite3.connect(db_path, timeout=15.0)
        conn.execute("CREATE TABLE IF NOT EXISTS _healthcheck (id INTEGER PRIMARY KEY)")
    except sqlite3.OperationalError:
        db_path = os.path.join(tempfile.gettempdir(), "fintrust_cloud_cache.db")
        conn = sqlite3.connect(db_path, timeout=15.0)

    conn.row_factory = sqlite3.Row
    _ensure_sqlite_tables(conn)
    return conn


def _ensure_sqlite_tables(conn: sqlite3.Connection) -> None:
    """Khởi tạo 4 bảng tương đương schema Supabase trong SQLite cục bộ."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS companies (
            ticker TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            industry TEXT DEFAULT 'Khác',
            firm_age INTEGER DEFAULT 10,
            quant_score REAL DEFAULT 85.0,
            updated_by TEXT DEFAULT 'Cán bộ Thẩm định',
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS financial_data (
            ticker TEXT NOT NULL,
            year INTEGER NOT NULL,
            variable TEXT NOT NULL,
            value REAL,
            updated_at TEXT,
            PRIMARY KEY (ticker, year, variable)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS manual_overrides (
            ticker TEXT NOT NULL,
            year INTEGER NOT NULL,
            item_code TEXT NOT NULL,
            item_name TEXT NOT NULL,
            ocr_value REAL NOT NULL,
            applied_value REAL NOT NULL,
            remark TEXT DEFAULT '',
            operator TEXT DEFAULT 'Cán bộ Thẩm định',
            updated_at TEXT,
            PRIMARY KEY (ticker, year, item_code)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appraisal_profiles (
            ticker TEXT PRIMARY KEY,
            qual_criteria TEXT DEFAULT '{}',
            quant_weight_pct INTEGER DEFAULT 60,
            underwriting_inputs TEXT DEFAULT '{}',
            updated_by TEXT DEFAULT 'Cán bộ Thẩm định',
            updated_at TEXT
        )
        """
    )
    conn.commit()


# ---------------------------------------------------------------------------
# API ĐỌC / GHI HỒ SƠ THẨM ĐỊNH & NHẬT KÝ AUDIT TRAIL
# ---------------------------------------------------------------------------
def list_saved_companies() -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả hồ sơ doanh nghiệp đã lưu (ưu tiên Supabase Cloud)."""
    client = get_supabase_client()
    if client is not None:
        try:
            resp = (
                client.table("companies")
                .select("ticker, company_name, industry, firm_age, quant_score, updated_by, updated_at")
                .order("updated_at", desc=True)
                .execute()
            )
            rows = resp.data or []
            return [
                {
                    "ticker": r["ticker"],
                    "name": r["company_name"],
                    "industry": r.get("industry") or "Khác",
                    "age": int(r.get("firm_age") or 10),
                    "quant_score": float(r.get("quant_score") or 85.0),
                    "updated_by": r.get("updated_by") or "N/A",
                    "updated_at": r.get("updated_at") or "",
                    "source": "Supabase Cloud",
                }
                for r in rows
            ]
        except Exception:
            pass

    conn = _get_sqlite_conn()
    try:
        rows = conn.execute(
            """
            SELECT ticker, company_name, industry, firm_age, quant_score, updated_by, updated_at
            FROM companies
            ORDER BY updated_at DESC
            """
        ).fetchall()
        return [
            {
                "ticker": r["ticker"],
                "name": r["company_name"],
                "industry": r["industry"] or "Khác",
                "age": int(r["firm_age"] or 10),
                "quant_score": float(r["quant_score"] or 85.0),
                "updated_by": r["updated_by"] or "N/A",
                "updated_at": r["updated_at"] or "",
                "source": "SQLite Cục Bộ",
            }
            for r in rows
        ]
    finally:
        conn.close()


def save_company_profile(
    company: Dict[str, Any],
    bctc_override_data: List[Dict[str, Any]],
    qual_criteria: Dict[str, Any],
    quant_w_pct: int,
    underwriting_inputs: Optional[Dict[str, Any]] = None,
    operator: str = "Cán bộ Thẩm định",
    year: int = 2024,
) -> Tuple[bool, str]:
    """Lưu toàn bộ hồ sơ doanh nghiệp, nhật ký Audit Trail hiệu chỉnh tay và điểm 5Cs lên Cloud/SQLite."""
    ticker = str(company.get("ticker", "")).strip().upper()
    if not ticker:
        return False, "Thiếu mã doanh nghiệp (ticker)."

    now_iso = datetime.now(timezone.utc).isoformat()
    company_payload = {
        "ticker": ticker,
        "company_name": str(company.get("name", ticker)),
        "industry": str(company.get("industry", "Khác")),
        "firm_age": int(company.get("age", 10)),
        "quant_score": float(company.get("quant_score", 85.0)),
        "updated_by": operator,
        "updated_at": now_iso,
    }

    override_rows: List[Dict[str, Any]] = []
    fin_rows: List[Dict[str, Any]] = []
    for row in bctc_override_data:
        code = str(row.get("Mã Số", "")).strip()
        name = str(row.get("Khoản Mục Kế Toán", "")).strip()
        ocr_val = float(row.get("Số Gốc OCR (tỷ VNĐ)", 0.0))
        app_val = float(row.get("Số Áp Dụng (tỷ VNĐ)", 0.0))
        remark = str(row.get("Lý Do Điều Chỉnh (Remark)", "") or "").strip()
        override_rows.append(
            {
                "ticker": ticker,
                "year": int(year),
                "item_code": code,
                "item_name": name,
                "ocr_value": ocr_val,
                "applied_value": app_val,
                "remark": remark,
                "operator": operator,
                "updated_at": now_iso,
            }
        )
        fin_rows.append(
            {
                "ticker": ticker,
                "year": int(year),
                "variable": f"{code}_{name}",
                "value": app_val,
                "updated_at": now_iso,
            }
        )

    profile_payload = {
        "ticker": ticker,
        "qual_criteria": qual_criteria,
        "quant_weight_pct": int(quant_w_pct),
        "underwriting_inputs": underwriting_inputs or {},
        "updated_by": operator,
        "updated_at": now_iso,
    }

    # 1. Thử lưu lên Supabase Cloud trước
    client = get_supabase_client()
    if client is not None:
        try:
            client.table("companies").upsert(company_payload, on_conflict="ticker").execute()
            if override_rows:
                client.table("manual_overrides").upsert(
                    override_rows, on_conflict="ticker,year,item_code"
                ).execute()
            if fin_rows:
                client.table("financial_data").upsert(
                    fin_rows, on_conflict="ticker,year,variable"
                ).execute()
            client.table("appraisal_profiles").upsert(
                profile_payload, on_conflict="ticker"
            ).execute()
            return True, f"☁️ Đã đồng bộ hồ sơ **{ticker}** và vết Audit Trail lên **Supabase Cloud** (Cán bộ: {operator})."
        except Exception as exc:
            # Dự phòng lưu cục bộ để không mất dữ liệu của cán bộ thẩm định
            _save_to_sqlite(company_payload, override_rows, fin_rows, profile_payload)
            return (
                True,
                f"⚠️ Supabase tạm lỗi ({exc}). Hệ thống đã lưu an toàn vào **SQLite dự phòng**.",
            )

    # 2. Chế độ Local SQLite
    _save_to_sqlite(company_payload, override_rows, fin_rows, profile_payload)
    return True, f"💾 Đã lưu hồ sơ **{ticker}** và vết Audit Trail vào **SQLite cục bộ** (Cán bộ: {operator})."


def _save_to_sqlite(
    company_payload: Dict[str, Any],
    override_rows: List[Dict[str, Any]],
    fin_rows: List[Dict[str, Any]],
    profile_payload: Dict[str, Any],
) -> None:
    """Ghi đồng bộ 4 bảng vào SQLite cục bộ."""
    conn = _get_sqlite_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO companies
            (ticker, company_name, industry, firm_age, quant_score, updated_by, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_payload["ticker"],
                company_payload["company_name"],
                company_payload["industry"],
                company_payload["firm_age"],
                company_payload["quant_score"],
                company_payload["updated_by"],
                company_payload["updated_at"],
            ),
        )
        for r in override_rows:
            cur.execute(
                """
                INSERT OR REPLACE INTO manual_overrides
                (ticker, year, item_code, item_name, ocr_value, applied_value, remark, operator, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r["ticker"],
                    r["year"],
                    r["item_code"],
                    r["item_name"],
                    r["ocr_value"],
                    r["applied_value"],
                    r["remark"],
                    r["operator"],
                    r["updated_at"],
                ),
            )
        for f in fin_rows:
            cur.execute(
                """
                INSERT OR REPLACE INTO financial_data
                (ticker, year, variable, value, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (f["ticker"], f["year"], f["variable"], f["value"], f["updated_at"]),
            )
        cur.execute(
            """
            INSERT OR REPLACE INTO appraisal_profiles
            (ticker, qual_criteria, quant_weight_pct, underwriting_inputs, updated_by, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                profile_payload["ticker"],
                json.dumps(profile_payload["qual_criteria"], ensure_ascii=False),
                profile_payload["quant_weight_pct"],
                json.dumps(profile_payload["underwriting_inputs"], ensure_ascii=False),
                profile_payload["updated_by"],
                profile_payload["updated_at"],
            ),
        )
        conn.commit()
    finally:
        conn.close()


def load_company_profile(ticker: str, year: int = 2024) -> Optional[Dict[str, Any]]:
    """Tải đầy đủ hồ sơ doanh nghiệp + dữ liệu hiệu chỉnh tay + 5Cs từ Supabase Cloud (hoặc SQLite)."""
    ticker = str(ticker).strip().upper()
    if not ticker:
        return None

    client = get_supabase_client()
    if client is not None:
        try:
            comp_resp = client.table("companies").select("*").eq("ticker", ticker).limit(1).execute()
            if comp_resp.data:
                comp = comp_resp.data[0]
                ov_resp = (
                    client.table("manual_overrides")
                    .select("*")
                    .eq("ticker", ticker)
                    .eq("year", int(year))
                    .execute()
                )
                prof_resp = (
                    client.table("appraisal_profiles")
                    .select("*")
                    .eq("ticker", ticker)
                    .limit(1)
                    .execute()
                )
                prof = prof_resp.data[0] if prof_resp.data else {}
                overrides = [
                    {
                        "Mã Số": r["item_code"],
                        "Khoản Mục Kế Toán": r["item_name"],
                        "Số Gốc OCR (tỷ VNĐ)": float(r["ocr_value"]),
                        "Số Áp Dụng (tỷ VNĐ)": float(r["applied_value"]),
                        "Lý Do Điều Chỉnh (Remark)": r.get("remark") or "",
                        "Cán Bộ Thao Tác": r.get("operator") or comp.get("updated_by") or "Cán bộ Thẩm định",
                        "Cập Nhật Lúc (UTC)": r.get("updated_at") or "",
                    }
                    for r in (ov_resp.data or [])
                ]
                return {
                    "company": {
                        "ticker": comp["ticker"],
                        "name": comp["company_name"],
                        "industry": comp.get("industry") or "Khác",
                        "age": int(comp.get("firm_age") or 10),
                        "quant_score": float(comp.get("quant_score") or 85.0),
                    },
                    "bctc_override_data": overrides,
                    "qual_criteria_state": prof.get("qual_criteria") or {},
                    "quant_w_pct": int(prof.get("quant_weight_pct") or 60),
                    "underwriting_inputs": prof.get("underwriting_inputs") or {},
                    "updated_by": comp.get("updated_by") or "N/A",
                    "updated_at": comp.get("updated_at") or "",
                    "source": "Supabase Cloud",
                }
        except Exception:
            pass

    # Fallback SQLite cục bộ
    conn = _get_sqlite_conn()
    try:
        comp = conn.execute("SELECT * FROM companies WHERE ticker = ?", (ticker,)).fetchone()
        if not comp:
            return None
        ov_rows = conn.execute(
            "SELECT * FROM manual_overrides WHERE ticker = ? AND year = ?",
            (ticker, int(year)),
        ).fetchall()
        prof = conn.execute(
            "SELECT * FROM appraisal_profiles WHERE ticker = ?", (ticker,)
        ).fetchone()

        overrides = [
            {
                "Mã Số": r["item_code"],
                "Khoản Mục Kế Toán": r["item_name"],
                "Số Gốc OCR (tỷ VNĐ)": float(r["ocr_value"]),
                "Số Áp Dụng (tỷ VNĐ)": float(r["applied_value"]),
                "Lý Do Điều Chỉnh (Remark)": r["remark"] or "",
                "Cán Bộ Thao Tác": r["operator"] or comp["updated_by"] or "Cán bộ Thẩm định",
                "Cập Nhật Lúc (UTC)": r["updated_at"] or "",
            }
            for r in ov_rows
        ]
        return {
            "company": {
                "ticker": comp["ticker"],
                "name": comp["company_name"],
                "industry": comp["industry"] or "Khác",
                "age": int(comp["firm_age"] or 10),
                "quant_score": float(comp["quant_score"] or 85.0),
            },
            "bctc_override_data": overrides,
            "qual_criteria_state": json.loads(prof["qual_criteria"]) if prof and prof["qual_criteria"] else {},
            "quant_w_pct": int(prof["quant_weight_pct"]) if prof and prof["quant_weight_pct"] else 60,
            "underwriting_inputs": (
                json.loads(prof["underwriting_inputs"]) if prof and prof["underwriting_inputs"] else {}
            ),
            "updated_by": comp["updated_by"] or "N/A",
            "updated_at": comp["updated_at"] or "",
            "source": "SQLite Cục Bộ",
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# XUẤT / NHẬP GÓI HỒ SƠ JSON (BACKUP & CHIA SẺ QUA EMAIL/CHAT)
# ---------------------------------------------------------------------------
def export_profile_package_json(
    company: Dict[str, Any],
    bctc_override_data: List[Dict[str, Any]],
    qual_criteria: Dict[str, Any],
    quant_w_pct: int,
    operator: str,
) -> str:
    """Đóng gói toàn bộ hồ sơ thẩm định + vết Audit Trail thành chuỗi JSON chuẩn UTF-8."""
    package = {
        "schema_version": "fintrust_ews_v2.1",
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "exported_by": operator,
        "company": company,
        "bctc_override_data": bctc_override_data,
        "qual_criteria_state": qual_criteria,
        "quant_w_pct": int(quant_w_pct),
    }
    return json.dumps(package, ensure_ascii=False, indent=2)


def parse_profile_package_json(raw_bytes: bytes) -> Dict[str, Any]:
    """Đọc và kiểm tra tính hợp lệ của file Gói Hồ Sơ (.json) khi đồng nghiệp nhập vào."""
    data = json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(data, dict) or "company" not in data:
        raise ValueError("Tệp JSON không đúng định dạng Gói Hồ Sơ FinTrust EWS.")
    return data
