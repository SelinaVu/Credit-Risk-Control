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
