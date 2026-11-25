-- ============================================================================
-- FINTRUST EWS v2.1 - SUPABASE POSTGRESQL SCHEMA (PHƯƠNG ÁN 1: CLOUD DATABASE)
-- Hướng dẫn: Copy toàn bộ nội dung file này -> Dán vào Supabase SQL Editor -> Bấm RUN
-- ============================================================================

-- 1. Bảng danh mục Doanh nghiệp đã thẩm định
CREATE TABLE IF NOT EXISTS public.companies (
    ticker TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    industry TEXT DEFAULT 'Khác',
    firm_age INTEGER DEFAULT 10,
    quant_score DOUBLE PRECISION DEFAULT 85.0,
    updated_by TEXT DEFAULT 'Cán bộ Thẩm định',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Bảng số liệu BCTC chuẩn hóa (đồng bộ với giá trị áp dụng mới nhất)
CREATE TABLE IF NOT EXISTS public.financial_data (
    ticker TEXT NOT NULL REFERENCES public.companies(ticker) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    variable TEXT NOT NULL,
    value DOUBLE PRECISION,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (ticker, year, variable)
);

-- 3. Bảng Nhật ký Kiểm toán & Hiệu chỉnh Thủ công (Audit Trail & Manual Overrides)
CREATE TABLE IF NOT EXISTS public.manual_overrides (
    ticker TEXT NOT NULL REFERENCES public.companies(ticker) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    item_code TEXT NOT NULL,
    item_name TEXT NOT NULL,
    ocr_value DOUBLE PRECISION NOT NULL,
    applied_value DOUBLE PRECISION NOT NULL,
    remark TEXT DEFAULT '',
    operator TEXT DEFAULT 'Cán bộ Thẩm định',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (ticker, year, item_code)
);

-- 4. Bảng Lưu trạng thái Hồ sơ Thẩm định (5Cs Định tính, Tỷ trọng Hybrid, Phương án vay)
CREATE TABLE IF NOT EXISTS public.appraisal_profiles (
    ticker TEXT PRIMARY KEY REFERENCES public.companies(ticker) ON DELETE CASCADE,
    qual_criteria JSONB DEFAULT '{}'::jsonb,
    quant_weight_pct INTEGER DEFAULT 60,
    underwriting_inputs JSONB DEFAULT '{}'::jsonb,
    updated_by TEXT DEFAULT 'Cán bộ Thẩm định',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chỉ mục tăng tốc truy vấn Audit Trail & danh sách hồ sơ mới cập nhật
CREATE INDEX IF NOT EXISTS idx_companies_updated_at
    ON public.companies (updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_manual_overrides_ticker_updated
    ON public.manual_overrides (ticker, updated_at DESC);

-- ============================================================================
-- PHÂN QUYỀN TRUY CẬP API CHO STREAMLIT CLOUD (ANON / AUTHENTICATED ROLE)
-- Lưu ý: Ứng dụng bảo vệ truy cập bằng Team Passcode cấu hình trong Streamlit Secrets.
-- ============================================================================
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.financial_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.manual_overrides ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appraisal_profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "fintrust_team_all_companies" ON public.companies;
CREATE POLICY "fintrust_team_all_companies"
    ON public.companies FOR ALL
    TO anon, authenticated
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "fintrust_team_all_financial_data" ON public.financial_data;
CREATE POLICY "fintrust_team_all_financial_data"
    ON public.financial_data FOR ALL
    TO anon, authenticated
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "fintrust_team_all_manual_overrides" ON public.manual_overrides;
CREATE POLICY "fintrust_team_all_manual_overrides"
    ON public.manual_overrides FOR ALL
    TO anon, authenticated
    USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "fintrust_team_all_appraisal_profiles" ON public.appraisal_profiles;
CREATE POLICY "fintrust_team_all_appraisal_profiles"
    ON public.appraisal_profiles FOR ALL
    TO anon, authenticated
    USING (true) WITH CHECK (true);

-- ============================================================================
-- 5. Bảng Danh sách Nhân sự & Phân quyền (Admin / Member) gắn với Supabase Auth
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.team_users (
    email TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.team_users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "fintrust_team_users_select" ON public.team_users;
CREATE POLICY "fintrust_team_users_select"
    ON public.team_users FOR SELECT
    TO anon, authenticated
    USING (true);

DROP POLICY IF EXISTS "fintrust_team_users_admin_write" ON public.team_users;
CREATE POLICY "fintrust_team_users_admin_write"
    ON public.team_users FOR ALL
    TO authenticated
    USING (true) WITH CHECK (true);
