# Tóm Tắt Dự Án & Bối Cảnh Hệ Thống (Compact Summary)

> **Dự án**: FinTrust EWS - Hệ thống Cảnh báo Sớm Rủi ro Tín dụng & Thẩm định Hạn mức Cho vay Vốn Lưu động  
> **Cập nhật ngày**: 17/11/2026  
> **Trạng thái**: Hoàn thành tái cấu trúc và tinh gọn toàn bộ repository (~1.72 GB đã giải phóng).

---

## 1. Mục Tiêu & Chức Năng Cốt Lõi Của FinTrust EWS
- **Ứng dụng**: Hệ thống hỗ trợ ra quyết định giải ngân và cảnh báo sớm rủi ro tín dụng cho các Ngân hàng Thương mại tại Việt Nam.
- **Tính năng trọng tâm**:
  1. **Chu kỳ tiền mặt (CCC) & Vốn lưu động**: Đánh giá chi tiết DSO (Phải thu), DSI (Tồn kho), DPO (Phải trả nhà cung cấp).
  2. **Bóc tách rủi ro theo mục đích vay (Module A)**: Phân loại theo ngành hàng/mặt hàng thực tế.
  3. **Bộ chỉ số hoạt động chuyên sâu (Module B)**: Vòng quay VLĐ, Phải thu, Tồn kho, Nhà cung cấp.
  4. **Nhóm thanh khoản & khả năng trả nợ (Module C)**: Quick Ratio, Cash Ratio, OCF/Nợ ngắn hạn, ICR, Tỷ lệ Vay/(Phải thu + Tồn kho).
  5. **Đối chuẩn ngành tự động (Module D)**: Benchmark tự động theo từng lĩnh vực.
  6. **Mô hình EWS toàn diện**: Altman Z'-Score, Beneish M-Score, Dechow F-Score, Abnormal Cash Flow (Ab_CFO, Ab_PROD, Ab_DISEXP) và mô hình Machine Learning phân loại rủi ro (`best_ews_model.joblib`).
  7. **Underwriting Memo & Xuất Báo Cáo**: Thẩm định phân cấp phê duyệt và xuất báo cáo thẩm định chuẩn ngân hàng dạng PDF.

---

## 2. Cấu Trúc Repository Đã Chuẩn Hóa

### 🚀 Thư mục gốc (Core Production & Deployment)
Giữ nguyên các file runtime để ứng dụng Streamlit, Docker và runner cục bộ hoạt động trơn tru:
- `fintrust_app.py`: Ứng dụng Streamlit chính (UI + Controller).
- `credit_underwriting_engine.py`: Động cơ tính toán thẩm định tín dụng.
- `pdf_report_generator.py`: Module xuất báo cáo PDF chuẩn ReportLab.
- `quarterly_leverage_updater.py`: Cập nhật ngưỡng đòn bẩy tối ưu định kỳ theo quý.
- `u_curve_regression.py`: Thuật toán hồi quy kinh tế lượng hàm chữ U.
- `best_ews_model.joblib`: Model ML EWS đã huấn luyện.
- `industry_opt_lev.json`: Cấu hình đòn bẩy tối ưu theo từng ngành.
- `quarterly_scheduler_config.json`: Cấu hình scheduler cập nhật đòn bẩy.
- `Fintech_EWS_GroundTruth_Template.xlsx`: File Excel mẫu TT200 nhúng trong app cho người dùng tải.
- `fintrust_ews.db`, `fintrust_profiles.db`: Cơ sở dữ liệu SQLite cục bộ.
- `storage/`: Thư mục lưu cache hồ sơ JSON doanh nghiệp.
- `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `packages.txt`: Đóng gói môi trường.
- `run_local.sh`, `run_local.bat`, `run_ews.sh`, `run_ews.bat`, `setup_windows.bat`: Script khởi chạy nhanh.
- `README.md`, `README_DEPLOY.md`, `AGENTS.md`, `.gitignore`.

### 📁 Các thư mục chức năng chuyên biệt
1. **`docs/`**: Tài liệu kỹ thuật & nghiệp vụ:
   - `1_cach_trich_xuat_bctc.md`, `2_cach_tinh_toan_bien_ews.md`, `3_cach_ket_luan_canh_bao.md`.
   - `eval_sheet.md`, `ews_sheet.md`, `ews_summary.txt`.
   - `audit_benchmark_report_v2.txt`.
   - `BÁO CÁO THẨM ĐỊNH.pdf`, `Bao_Cao_Tong_Quan_FinTrust_Thuyet_Trinh.docx`.
2. **`presentations/`**: Slide báo cáo & tài liệu học thuật:
   - `FinTrust_EWS_Bao_Cao_Hoi_Dong_Khoa_Hoc.pptx`, `FinTrust_EWS_Credit_Risk_Blueprint.pptx`.
   - `create_presentation.py` (Script sinh slide tự động).
   - `Error_Reports_Slides/`, `Meeting_16_11/`, `Luan_van_Thac_si/`.
3. **`models_research/`**: Nghiên cứu & Huấn luyện mô hình:
   - `train_ews_model.py`, `calculate_ews.py`.
   - `Earnings_manipulation_Roychowdhury.sas`, `Earnings_manipulation_fixed_2_V1.sas`.
4. **`data/`**: Kho dữ liệu kiểm thử & Panel BCTC:
   - `BCTC_Tu_Dong_Vnstock.xlsx`, `EWS.xlsx`, `Chỉ tiêu.xlsx`, `financials_progress.csv`.
   - `bctc_mau/`, `bctc_bo_sung/`, `bctc_error_reports/`, `ocr_samples/`.
5. **`packaging/`**: Công cụ đóng gói ứng dụng Desktop (PyInstaller / PyWebView):
   - `build_app.py`, `desktop_wrapper.py`, `Fintrust_EWS.spec`.

---

## 3. Nhật Ký Tối Ưu Hóa & Dọn Dẹp (~1.72 GB giải phóng)
- **Đã xóa**:
  - Cache build và file thực thi compiled cũ trong `packaging/build` và `packaging/dist` (~1.29 GB).
  - Thư mục nén và backup cũ `archives/` (~466 MB) bao gồm môi trường `venv` cũ bị lồng trong `Bank_ver_01`.
  - Log màn hình terminal `docs/logs/screenlog.0`.
  - Bản thảo cũ `audit_benchmark_report.txt` (đã có v2) và file SAS cũ chưa fix join `Earnings_manipulation_fixed_2.sas`.
  - Cache tạm Python (`__pycache__`) và các file `.DS_Store`.
- **Tương thích ngược**:
  - `quarterly_leverage_updater.py` tự động nhận diện `data/BCTC_Tu_Dong_Vnstock.xlsx` hoặc tại thư mục gốc.
  - `models_research/train_ews_model.py` và các script trong `packaging/` đã được cấu hình đường dẫn động.
