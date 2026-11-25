# HƯỚNG DẪN TRÍCH XUẤT DỮ LIỆU TỪ BÁO CÁO TÀI CHÍNH (BCTC)

Tài liệu này hướng dẫn chi tiết quy trình trích xuất và chuẩn hóa dữ liệu tài chính từ BCTC (Excel hoặc PDF) phục vụ cho Bộ chỉ số Cảnh báo sớm Rủi ro Doanh nghiệp (EWS). Quy trình dựa trên các mã số chỉ tiêu kế toán chuẩn theo **Thông tư 200/2014/TT-BTC** và phương pháp đối chiếu từ khóa thông minh để xử lý sai sót do OCR hoặc bố cục báo cáo không nhất quán.

---

## 1. Danh sách 21 biến tài chính cần trích xuất

Để tính toán 10 chỉ số EWS, hệ thống cần trích xuất chính xác **21 chỉ tiêu tài chính** từ 3 báo cáo chính: Bảng Cân đối Kế toán (CDKT), Báo cáo Kết quả Hoạt động Kinh doanh (KQKD) và Báo cáo Lưu chuyển Tiền tệ (LCTT).

### Bảng Cân đối Kế toán (CDKT) - 12 chỉ tiêu
1. **Current_Assets**: Tài sản ngắn hạn (Mã 100)
2. **Cash_Equivalents**: Tiền và tương đương tiền (Mã 110)
3. **Current_Receivables**: Các khoản phải thu ngắn hạn (Mã 130)
4. **Accounts_Receivable**: Phải thu ngắn hạn của khách hàng (Mã 131)
5. **Inventories**: Hàng tồn kho (Mã 140)
6. **Fixed_Assets**: Tài sản cố định - Giá trị sổ sách ròng (Mã 220)
7. **Tangible_PPE_Cost**: Nguyên giá TSCĐ hữu hình (Mã 221)
8. **Total_Assets**: Tổng cộng tài sản (Mã 270)
9. **Total_Liabilities**: Nợ phải trả (Mã 300)
10. **Current_Liabilities**: Nợ ngắn hạn (Mã 310)
11. **Equity**: Vốn chủ sở hữu (Mã 400)
12. **Retained_Earnings**: Lợi nhuận sau thuế chưa phân phối (Mã 421)

### Báo cáo Kết quả Kinh doanh (KQKD) - 8 chỉ tiêu
13. **Net_Sales**: Doanh thu thuần về bán hàng & cung cấp dịch vụ (Mã 10)
14. **COGS**: Giá vốn hàng bán (Mã 11)
15. **Gross_Profit**: Lợi nhuận gộp (Mã 20 KQKD)
16. **Interest_Expense**: Chi phí lãi vay (Mã 23)
17. **Selling_Expense**: Chi phí bán hàng (Mã 25)
18. **GA_Expense**: Chi phí quản lý doanh nghiệp (Mã 26)
19. **EBT**: Tổng lợi nhuận kế toán trước thuế (Mã 50)
20. **Net_Income**: Lợi nhuận sau thuế thu nhập doanh nghiệp (Mã 60)

### Báo cáo Lưu chuyển Tiền tệ (LCTT) - 1 chỉ tiêu
21. **OCF**: Lưu chuyển tiền thuần từ hoạt động kinh doanh (Mã 20 LCTT)

---

## 2. Bản đồ mã số chỉ tiêu chuẩn (CODE_MAP)

Mã số chỉ tiêu (Form Code) trên cột "Mã số" của BCTC là điểm neo quan trọng nhất để trích xuất dữ liệu tự động. Dưới đây là bảng ánh xạ chuẩn:

| Tên biến lập trình | Tên chỉ tiêu tiếng Việt | Báo cáo nguồn | Mã số chuẩn (TT 200) |
| :--- | :--- | :---: | :---: |
| `Current_Assets` | Tài sản ngắn hạn | CDKT | **100** |
| `Cash_Equivalents` | Tiền và tương đương tiền | CDKT | **110** |
| `Current_Receivables` | Các khoản phải thu ngắn hạn | CDKT | **130** |
| `Accounts_Receivable` | Phải thu ngắn hạn của khách hàng | CDKT | **131** |
| `Inventories` | Hàng tồn kho | CDKT | **140** |
| `Fixed_Assets` | Tài sản cố định (Giá trị ròng) | CDKT | **220** |
| `Tangible_PPE_Cost` | Nguyên giá TSCĐ hữu hình | CDKT | **221** |
| `Total_Assets` | Tổng cộng tài sản | CDKT | **270** |
| `Total_Liabilities` | Nợ phải trả | CDKT | **300** |
| `Current_Liabilities` | Nợ ngắn hạn | CDKT | **310** |
| `Equity` | Vốn chủ sở hữu | CDKT | **400** |
| `Retained_Earnings` | Lợi nhuận sau thuế chưa phân phối | CDKT | **421** |
| `Net_Sales` | Doanh thu thuần | KQKD | **10** |
| `COGS` | Giá vốn hàng bán | KQKD | **11** |
| `Gross_Profit` | Lợi nhuận gộp | KQKD | **20** |
| `Interest_Expense` | Chi phí lãi vay | KQKD | **23** |
| `Selling_Expense` | Chi phí bán hàng | KQKD | **25** |
| `GA_Expense` | Chi phí QLDN | KQKD | **26** |
| `EBT` | Tổng lợi nhuận trước thuế | KQKD | **50** |
| `Net_Income` | Lợi nhuận sau thuế | KQKD | **60** |
| `OCF` | Dòng tiền thuần từ HĐKD | LCTT | **20** |

> [!WARNING]
> **Xử lý trùng mã số (Mã số 20):**
> Mã số **20** xuất hiện ở cả KQKD (Lợi nhuận gộp) và LCTT (Dòng tiền từ HĐKD). Hệ thống bắt buộc phải phân loại chính xác loại báo cáo của sheet đang đọc để ánh xạ đúng chỉ tiêu, tránh ghi đè dữ liệu.

---

## 3. Quy trình nhận diện loại báo cáo (Statement Detection)

Để tránh nhầm lẫn mã số và loại bỏ các thông tin rác (như Thuyết minh BCTC hay Báo cáo kiểm toán), hệ thống áp dụng quy trình lọc 3 bước:

### Bước 1: Loại bỏ trang không chứa số liệu chính
* BCTC dạng quét OCR thường chứa các trang thuyết minh hoặc báo cáo ý kiến kiểm toán. Hệ thống sẽ phát hiện và bỏ qua nếu tiêu đề trang hoặc văn bản chứa các cụm từ:
  * Form Code: `B09`, `B09DN`, `B09-DN` (Ký hiệu Thuyết minh BCTC).
  * Từ khóa thuyết minh: `thuyet minh bao cao tai chinh`, `thuyet minh bctc`.
  * Từ khóa kiểm toán: `kiem toan doc lap`, `y kien cua kiem toan`, `trach nhiem cua ban tong giam doc`.

### Bước 2: Nhận diện Form Code chuẩn ở góc trang
Nếu tìm thấy các mã chuẩn ở góc trên cùng bên phải trang báo cáo, lập tức phân loại:
* `B01-DN` hoặc `B01DN` hoặc `B01ADN` $\rightarrow$ **CDKT** (Bảng Cân đối Kế toán).
* `B02-DN` hoặc `B02DN` hoặc `B02ADN` $\rightarrow$ **KQKD** (Báo cáo Kết quả Kinh doanh).
* `B03-DN` hoặc `B03DN` hoặc `B03ADN` $\rightarrow$ **LCTT** (Báo cáo Lưu chuyển Tiền tệ).

### Bước 3: Đối chiếu từ khóa đặc trưng (Fallback)
Nếu góc trang bị mờ hoặc bị cắt mất mã form, hệ thống sẽ chuẩn hóa tiêu đề trang (loại bỏ dấu tiếng Việt, viết thường, bỏ ký tự đặc biệt) để đối chiếu:
* **LCTT**: chứa cụm từ `luu chuyen tien te` hoặc `luu chuyen tien`.
* **CDKT**: chứa cụm từ `bang can doi ke toan`, `can doi ke toan`, hoặc `can doi`.
* **KQKD**: chứa cụm từ `ket qua hoat dong kinh doanh`, `ket qua kinh doanh`, hoặc `bao cao ket qua hoat dong`.

---

## 4. Cấu hình từ khóa đối chiếu chi tiết (KEYWORDS_CONFIG_SF)

Để xử lý sai sót do OCR nhận diện sai mã số chỉ tiêu, hệ thống sử dụng thuật toán chuẩn hóa: **không dấu, không khoảng trắng (space-free - SF)**. Mỗi chỉ tiêu được định nghĩa bởi tập hợp từ khóa bắt buộc phải có (`pos` - positive) và tập hợp từ khóa tuyệt đối không được chứa (`neg` - negative).

Dưới đây là cấu hình chi tiết:

```python
KEYWORDS_CONFIG_SF = {
    # --- Bảng Cân đối Kế toán (CDKT) ---
    "Current_Assets": {
        "pos": [["taisannganhan"]],
        "neg": ["khac", "duphong", "chiphi", "ngoai"]
    },
    "Cash_Equivalents": {
        "pos": [["tien", "tuongduong"], ["tien", "twongduong"]],
        "neg": ["cuoinam", "daunam"]
    },
    "Current_Receivables": {
        "pos": [["phaithunganhan"]],
        "neg": ["khachhang", "duphong", "khac"]
    },
    "Accounts_Receivable": {
        "pos": [["phaithu", "khachhang"]],
        "neg": ["duphong", "khac"]
    },
    "Inventories": {
        "pos": [["hangtonkho"]],
        "neg": ["duphong", "giamgia"]
    },
    "Fixed_Assets": {
        "pos": [["taisancodinh"]],
        "neg": ["nguyengia", "haomon", "vohinh", "huuhinh", "thuetaichinh"]
    },
    "Tangible_PPE_Cost": {
        "pos": [["nguyengia"]],
        "neg": ["vohinh", "thuetaichinh"]
    },
    "Total_Assets": {
        "pos": [["tongcongtaisan"], ["tongtaisan"]],
        "neg": []
    },
    "Total_Liabilities": {
        "pos": [["nophaitra"]],
        "neg": ["nganhan", "daihan"]
    },
    "Current_Liabilities": {
        "pos": [["nonganhan"]],
        "neg": []
    },
    "Equity": {
        "pos": [["vonchusohuu"], ["vonvacacquy"]],
        "neg": ["loinhuan"]
    },
    "Retained_Earnings": {
        "pos": [["loinhuansauthuechuaphanphoi"], ["loinhuanchuaphanphoi"], ["lnstchuaphanphoi"]],
        "neg": []
    },
    
    # --- Báo cáo Kết quả Kinh doanh (KQKD) ---
    "Net_Sales": {
        "pos": [["doanhthuthuan"]],
        "neg": ["giamtru", "chuathuchien"]
    },
    "COGS": {
        "pos": [["giavon"], ["giaven"]],
        "neg": []
    },
    "Gross_Profit": {
        "pos": [["loinhuangop"]],
        "neg": []
    },
    "Interest_Expense": {
        "pos": [["laivay"], ["chiphilaivay"]],
        "neg": []
    },
    "Selling_Expense": {
        "pos": [["chiphibanhang"]],
        "neg": []
    },
    "GA_Expense": {
        "pos": [["chiphiquanly"]],
        "neg": []
    },
    "EBT": {
        "pos": [["loinhuantruocthue"], ["loinhuanketoantruocthue"]],
        "neg": []
    },
    "Net_Income": {
        "pos": [["loinhuansauthue"]],
        "neg": ["chuaphanphoi"]
    },
    
    # --- Báo cáo Lưu chuyển Tiền tệ (LCTT) ---
    "OCF": {
        "pos": [["luuchuyentienthuan"], ["tienthuan", "kinhdoanh"]],
        "neg": []
    }
}
```

> [!NOTE]
> **Ưu tiên tuyệt đối mã 421:**
> Trong CDKT, chỉ tiêu **Lợi nhuận sau thuế chưa phân phối (Mã 421)** thường có nhiều dòng phụ (như 421a, 421b). Hệ thống ưu tiên tuyệt đối mã bắt đầu bằng `421` trên bảng cân đối để lấy giá trị tổng hợp cuối cùng.

---

## 5. Các bước trích xuất số liệu từ tệp Excel BCTC

Quy trình đọc tệp Excel BCTC tự động gồm các bước sau:

1. **Quét tìm cột mã số chỉ tiêu (Code Column):**
   * Quét tất cả các tiêu đề cột. Nếu tìm thấy cột chứa các cụm từ: `mã số`, `mã`, `code`, `maso` $\rightarrow$ Đặt đó là cột mã số.
   * Nếu tiêu đề cột không ghi rõ, hệ thống quét các hàng của từng cột để tìm cột chứa nhiều mã số kế toán đặc trưng. Nếu cột chứa đồng thời tối thiểu 3 trong số các mã: `100` (TSNH), `270` (Tổng TS), `400` (VCSH), `10` (Doanh thu), `60` (LNST) $\rightarrow$ Xác định đó là cột mã số.

2. **Xác định cột năm tài chính (Year Columns):**
   * Duyệt qua các tiêu đề cột còn lại để tìm năm tài chính bằng biểu thức chính quy (Regex) tìm chuỗi 4 chữ số dạng `201x` hoặc `202x`. Hệ thống hỗ trợ lấy số liệu đa năm (ví dụ cột "Năm nay" và "Năm trước" được ghi nhận cụ thể là `2025` và `2024`).

3. **Trích xuất và làm sạch dữ liệu số:**
   * Hệ thống duyệt qua từng hàng trong bảng. Lấy mã số chỉ tiêu ở cột mã số, làm sạch (bỏ khoảng trắng, dấu chấm, dấu phẩy).
   * Lấy giá trị tại các cột năm tương ứng.
   * **Quy tắc làm sạch giá trị số:**
     * Trực quan hóa giá trị không (0.0): Nếu gặp các ký tự gạch ngang như `-`, `—`, `–`, `¬` $\rightarrow$ Quy đổi về giá trị `0.0`.
     * Xử lý số âm: Nếu giá trị nằm trong dấu ngoặc đơn `(123.456)` hoặc có dấu trừ đi trước `-123.456` $\rightarrow$ Nhân giá trị với `-1`.
     * Loại bỏ ký tự lạ: Loại bỏ các ký tự đặc biệt, dấu phân tách hàng nghìn (chỉ giữ lại chữ số) trước khi chuyển đổi sang dạng số thực (`float`).
     * Đảm bảo không lấy nhầm mã số chỉ tiêu làm giá trị số (nếu OCR đọc lệch dòng).

4. **Kiểm tra tính cân đối của dữ liệu (Data Validation):**
   Sau khi trích xuất, hệ thống thực hiện kiểm tra tính toàn vẹn của dữ liệu trước khi chuyển qua bộ tính toán EWS:
   * **Cân đối kế toán cơ bản:**
     $$\text{Tổng tài sản (270)} = \text{Nợ phải trả (300)} + \text{Vốn chủ sở hữu (400)}$$
     *(Sai số cho phép tối đa $0.5\%$ do làm tròn số hoặc lỗi hiển thị).*
   * **Kiểm tra tính nhất quán:**
     $$\text{Tài sản ngắn hạn (100)} + \text{Tài sản dài hạn (200)} = \text{Tổng cộng tài sản (270)}$$
     $$\text{Nợ ngắn hạn (310)} + \text{Nợ dài hạn (330)} = \text{Nợ phải trả (300)}$$
     $$\text{Lợi nhuận gộp (20)} = \text{Doanh thu thuần (10)} - \text{Giá vốn hàng bán (11)}$$
