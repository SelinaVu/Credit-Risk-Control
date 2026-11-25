# Hướng Dẫn Triển Khai FinTrust EWS v2.1 Lên Streamlit Cloud & Supabase (3 Phút)

Hướng dẫn dành cho quản trị viên thiết lập 1 lần duy nhất. Sau khi thiết lập xong, đồng nghiệp ở mọi quốc gia chỉ cần mở **1 đường link web** và sử dụng ngay — không cần cài đặt phần mềm.

---

## Bước 1: Tạo Cơ Sở Dữ Liệu Trên Supabase (Miễn phí)

1. Truy cập [supabase.com](https://supabase.com) ➔ đăng nhập (bằng tài khoản GitHub hoặc Google) ➔ bấm **New Project**.
2. Đặt tên dự án (ví dụ: `fintrust-ews`), chọn Region gần đội nhóm nhất (ví dụ: Singapore hoặc Tokyo), đặt Database Password ➔ bấm **Create new project** (chờ ~1 phút).
3. Ở thanh menu bên trái của Supabase, chọn **SQL Editor** ➔ bấm **New query**.
4. Mở file [`supabase_schema.sql`](./supabase_schema.sql) trong kho mã nguồn này, copy **toàn bộ nội dung**, dán vào SQL Editor ➔ bấm **Run**.
   - Nếu thấy thông báo `Success. No rows returned` là đã khởi tạo xong 4 bảng: `companies`, `financial_data`, `manual_overrides` (Audit Trail) và `appraisal_profiles`.
5. Vào **Project Settings (biểu tượng bánh răng)** ➔ **API** và copy 2 thông số:
   - **Project URL** (dạng `https://xxxxx.supabase.co`)
   - **anon / public key** (chuỗi bắt đầu bằng `eyJ...`)

---

## Bước 2: Phát Hành Ứng Dụng Lên Streamlit Community Cloud (Miễn phí)

1. Truy cập [share.streamlit.io](https://share.streamlit.io) ➔ đăng nhập bằng tài khoản GitHub (`SelinaVu`).
2. Bấm **Create app** ➔ chọn **Deploy a public/private app from GitHub**:
   - **Repository:** `SelinaVu/Credit-Risk-Control`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py` *(giao diện mới v2.1 Enterprise)*
3. Trước khi bấm Deploy (hoặc sau khi deploy vào **Settings ➔ Secrets**), dán cấu hình sau vào ô **Secrets**:
   ```toml
   [supabase]
   url = "https://xxxxx.supabase.co"
   key = "eyJhbGciOi..."

   [auth]
   team_passcode = "FinTrust2026"
   ```
   *(Thay `url`, `key` bằng thông số ở Bước 1, và đổi `team_passcode` thành mật khẩu nội bộ nhóm bạn muốn.)*
4. Bấm **Deploy!** — chờ khoảng 2 phút để hệ thống tự cài thư viện và cấp đường link web (dạng `https://credit-risk-control.streamlit.app`).

---

## Bước 3: Gửi Link Cho Đồng Nghiệp Đa Quốc Gia

- Gửi đường link ứng dụng và `team_passcode` cho đồng nghiệp.
- Khi đồng nghiệp đăng nhập ➔ nhập tên của họ (ví dụ: `Selina (JP)`) ➔ tải lên BCTC hoặc mở hồ sơ có sẵn ➔ chỉnh sửa số liệu & ghi **Remark** ➔ bấm **☁️ Lưu Vết Lên Supabase Cloud**.
- Đồng nghiệp ở quốc gia khác chỉ cần mở cùng đường link ➔ chọn hồ sơ tại mục **Mở hồ sơ từ Kho Dữ Liệu Chung** là thấy ngay toàn bộ số liệu mới nhất và Nhật ký Audit Trail.

> **Lưu ý gói Supabase Free:** Nếu **7 ngày liên tục** không có ai truy cập, Supabase Free sẽ tự động chuyển sang trạng thái *Paused*. Chỉ cần đăng nhập vào [supabase.com](https://supabase.com) và bấm **Restore Project** (1 click) để mở lại dữ liệu nguyên vẹn.
