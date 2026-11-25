# FinTrust EWS - Hệ Thống Cảnh Báo Sớm Rủi Ro Tín Dụng & Thẩm Định Cho Vay Vốn Lưu Động

Hệ thống hỗ trợ ra quyết định giải ngân và cảnh báo sớm rủi ro tín dụng (Early Warning System) cho các Ngân hàng Thương mại tại Việt Nam.

## 🌟 Tính Năng Chính
1. **Phân tích Cân đối Nguồn Vốn Vay Ngắn Hạn & Chu kỳ Tiền mặt (CCC)**: Bóc tách chất lượng Phải thu (DSO), Hàng tồn kho (DSI), Nợ nhà cung cấp (DPO).
2. **Khai báo Mục đích Vay theo Lĩnh vực (Module A)**: Bóc tách rủi ro theo đúng lĩnh vực/mặt hàng kinh doanh thay vì dùng số liệu gộp BCTC.
3. **Chỉ số Hoạt động Chi tiết (Module B)**: Vòng quay Tồn kho, Vòng quay Phải thu, Vòng quay Phải trả NCC, Vòng quay VLĐ.
4. **Nhóm Thanh khoản Chuyên sâu (Module C)**: Quick Ratio, Cash Ratio, OCF/Nợ ngắn hạn, Khả năng trả lãi (ICR), Tỷ lệ Vay/(PT+TK).
5. **Nhận định Tự động theo Chuẩn Ngành (Module D)**: Tự động so sánh với benchmark từng ngành và đưa ra cảnh báo cho CBTD.
6. **Mô hình EWS Toàn diện**: Altman Z'-Score, Beneish M-Score, Dechow F-Score, Dòng tiền bất thường (Ab_CFO, Ab_PROD, Ab_DISEXP).
7. **Thẩm định Tín dụng & Xuất Báo cáo**: Underwriting Memo chuẩn Ngân hàng, phân cấp phê duyệt và tính hạn mức cấp tín dụng.

## 📁 Cấu Trúc Thư Mục Dự Án

Thư mục dự án đã được chuẩn hóa và phân loại khoa học:

```text
Credit_Risk_Control/
├── fintrust_app.py                      # Ứng dụng Streamlit chính (Giao diện & xử lý)
├── credit_underwriting_engine.py         # Module động cơ thẩm định tín dụng
├── pdf_report_generator.py               # Module kết xuất báo cáo thẩm định PDF
├── quarterly_leverage_updater.py         # Bộ cập nhật ngưỡng đòn bẩy tối ưu theo quý
├── u_curve_regression.py                 # Thuật toán hồi quy kinh tế lượng chữ U
├── best_ews_model.joblib                 # Mô hình Machine Learning đã huấn luyện
├── industry_opt_lev.json                 # Ngưỡng đòn bẩy tối ưu phân ngành
├── quarterly_scheduler_config.json       # Cấu hình tự động cập nhật định kỳ
├── Fintech_EWS_GroundTruth_Template.xlsx # File Excel mẫu chuẩn TT200 tích hợp app
├── fintrust_ews.db                       # Cơ sở dữ liệu SQLite lưu trữ hồ sơ & điều chỉnh
├── storage/                              # Lưu trữ cache hồ sơ JSON doanh nghiệp
├── run_local.sh / run_local.bat          # Script khởi động nhanh hệ thống
├── Dockerfile / docker-compose.yml       # Cấu hình đóng gói container Docker
│
├── docs/                                 # Tài liệu kỹ thuật, hướng dẫn & báo cáo mẫu
│   ├── 1_cach_trich_xuat_bctc.md         # Hướng dẫn bóc tách BCTC
│   ├── 2_cach_tinh_toan_bien_ews.md      # Phương pháp tính biến EWS
│   ├── 3_cach_ket_luan_canh_bao.md       # Logic kết luận cảnh báo sớm
│   ├── eval_sheet.md / ews_sheet.md      # Bảng đặc tả chỉ tiêu & tiêu chí đánh giá
│   ├── audit_benchmark_report*.txt       # Báo cáo đối chuẩn kiểm toán
│   ├── BÁO CÁO THẨM ĐỊNH.pdf           # Báo cáo thẩm định mẫu hoàn chỉnh
│   └── Bao_Cao_Tong_Quan_*.docx          # Tài liệu thuyết minh tổng quan
│
├── presentations/                        # Slide báo cáo, họp & nghiên cứu học thuật
│   ├── FinTrust_EWS_Bao_Cao_*.pptx       # Slide thuyết trình Hội đồng Khoa học
│   ├── FinTrust_EWS_Credit_Risk_*.pptx   # Blueprint kiến trúc giải pháp tín dụng
│   ├── create_presentation.py            # Script tự động sinh deck thuyết trình
│   ├── Error_Reports_Slides/             # Báo cáo trích xuất lỗi dạng slide
│   ├── Meeting_16_11/                    # Biên bản họp và tài liệu liên quan
│   └── Luan_van_Thac_si/                 # Các bài báo nghiên cứu nền tảng
│
├── models_research/                      # Huấn luyện mô hình ML & nghiên cứu SAS
│   ├── train_ews_model.py                # Script huấn luyện mô hình ML EWS
│   ├── calculate_ews.py                  # Script trích xuất và tính biến từ Vnstock
│   └── Earnings_manipulation_*.sas       # Các file code phân tích định lượng SAS
│
├── data/                                 # Dữ liệu tài chính, BCTC mẫu & dữ liệu test
│   ├── BCTC_Tu_Dong_Vnstock.xlsx         # Dataset huấn luyện mô hình
│   ├── EWS.xlsx / Chỉ tiêu.xlsx          # Bảng dữ liệu và mapping chỉ tiêu
│   ├── bctc_mau/                         # Thư mục BCTC mẫu của các doanh nghiệp
│   ├── bctc_bo_sung/                     # Thư mục BCTC bổ sung
│   ├── bctc_error_reports/               # Dữ liệu BCTC kiểm thử lỗi
│   └── ocr_samples/                      # Ảnh mẫu các trang BCTC phục vụ test OCR
│
├── packaging/                            # Đóng gói Desktop App (PyInstaller/PyWebView)
│   ├── build_app.py                      # Script build file chạy độc lập
│   ├── desktop_wrapper.py                # Cửa sổ desktop wrapper PyWebView
│   └── Fintrust_EWS.spec                 # Cấu hình đóng gói PyInstaller
```

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 1. Chạy trên máy tính cá nhân (macOS / Linux / Windows)
```bash
# Tạo môi trường ảo
python3 -m venv .venv
source .venv/bin/activate  # Trên Windows: .venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt

# Khởi chạy ứng dụng
streamlit run fintrust_app.py
```

### 2. Triển khai Streamlit Cloud
1. Fork hoặc clone repo này về GitHub.
2. Đăng nhập [share.streamlit.io](https://share.streamlit.io) với tài khoản GitHub.
3. Chọn repo `Credit-Risk-Control`, branch `main`, main file path: `fintrust_app.py`.
4. Nhấn **Deploy!**
