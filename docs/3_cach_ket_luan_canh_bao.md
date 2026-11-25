# QUY TẮC KẾT LUẬN VÀ NGƯỠNG CẢNH BÁO SỚM RỦI RO (EWS)

Tài liệu này tổng hợp các điều kiện áp dụng, ngưỡng cảnh báo phân loại mức độ rủi ro (Xanh/Vàng/Đỏ) và các quy tắc kết hợp cảnh báo tổng hợp dành cho 10 chỉ số EWS khi triển khai thực tế tại Việt Nam.

---

## 1. Bảng tổng hợp ngưỡng cảnh báo và mức độ rủi ro

| STT | Chỉ số tài chính | 🟢 Rủi ro thấp (An toàn) | 🟡 Rủi ro trung bình (Vùng xám) | 🔴 Rủi ro cao (Nguy hiểm / Hạn chế) |
| :---: | :--- | :---: | :---: | :---: |
| 1 | **Altman Z'-Score** | Z' > 2.90 | 1.23 < Z' $\le$ 2.90 | Z' $\le$ 1.23 |
| 2 | **SA Index** | SA $\le$ -3.10 | -3.10 < SA $\le$ -2.55 | SA > -2.55 |
| 3 | **Beneish M-Score (1999)** | M < -2.22 | -2.22 $\le$ M $\le$ -1.78 | M > -1.78 |
| 4 | **Beneish M-Score (1997)** | P_12 $\le$ 3.00% | 3.00% < P_12 $\le$ 6.75% | P_12 > 6.75% |
| 5 | **Dechow F-Score (2011)** | F $\le$ 1.00 | 1.00 < F $\le$ 1.85 | F > 1.85 *(F > 2.45: Rất cao)* |
| 6 | **Abnormal CFO (Ab_CFO)** | Ab_CFO $\ge$ 0.00 | -0.05 $\le$ Ab_CFO < 0.00 | Ab_CFO < -0.05 |
| 7 | **Abnormal PROD (Ab_PROD)** | Ab_PROD $\le$ 0.00 | 0.00 < Ab_PROD $\le$ 0.05 | Ab_PROD > 0.05 |
| 8 | **Abnormal DISEXP (Ab_DISEXP)**| Ab_DISEXP $\ge$ 0.00 | -0.03 $\le$ Ab_DISEXP < 0.00 | Ab_DISEXP < -0.03 |
| 9 | **KZ Index** | KZ $\le$ 1.50 | 1.50 < KZ $\le$ 3.00 | KZ > 3.00 |
| 10| **WW Index** | WW $\le$ -0.40 | -0.40 < WW $\le$ -0.20 | WW > -0.20 |

---

## 2. Hướng dẫn diễn giải kết luận chi tiết từng chỉ số

### 1. Altman Z'-Score (Dự báo kiệt quệ tài chính)
* **Xanh (An toàn)**: Doanh nghiệp có cấu trúc tài chính lành mạnh, khả năng thanh toán tốt và rủi ro kiệt quệ tài chính trong 1-2 năm tới cực kỳ thấp.
* **Vàng (Vùng xám)**: Cần chú ý theo dõi. Cấu trúc vốn hoặc khả năng sinh lời bắt đầu có dấu hiệu suy yếu. Khuyến nghị kiểm tra kỹ cơ cấu tài sản thanh khoản ròng ($X_1$).
* **Đỏ (Nguy hiểm)**: Nguy cơ mất khả năng thanh toán hoặc phá sản rất cao. Cần hạn chế hoặc siết chặt điều kiện giải ngân.

### 2. SA Index (Hạn chế tài chính)
* SA Index càng tiến sát về $0$ (giá trị âm nhỏ) thể hiện doanh nghiệp có quy mô nhỏ và tuổi đời trẻ, cực kỳ khó khăn trong việc tiếp cận nguồn vốn vay ngân hàng truyền thống hoặc phát hành trái phiếu.
* **Đỏ (Hạn chế cao)**: Doanh nghiệp bị ràng buộc tài chính lớn. Mọi quyết định cấp tín dụng cần dựa nhiều vào tài sản bảo đảm thay vì tín chấp.

### 3. Beneish M-Score (Phát hiện thao túng lợi nhuận)
* **Đỏ (M > -1.78)**: Xác suất doanh nghiệp đang xào nấu báo cáo tài chính để thổi phồng lợi nhuận báo cáo rất cao.
* *Lưu ý*: M-Score phiên bản 1999 đặc biệt nhạy với biến phải thu tăng đột biến ($DSRI > 1.0$), thể hiện doanh nghiệp đang ghi nhận doanh thu ảo trước kỳ báo cáo để làm đẹp hồ sơ vay.

### 4. Dechow F-Score (Xác suất sai sót BCTC tổng hợp)
* F-Score đóng vai trò như một hệ số nhân rủi ro so với mức trung bình của thị trường.
* **F-Score = 1.00**: Mức rủi ro trung bình của thị trường.
* **F-Score > 1.85 (Đỏ)**: Rủi ro thao túng/sai sót tài chính cao gấp gần 2 lần thị trường.
* **F-Score > 2.45 (Cực kỳ nguy hiểm)**: Tỷ lệ báo động giả (bắt nhầm doanh nghiệp tốt) giảm xuống chỉ còn khoảng $5\%$. Khuyến nghị từ chối nhận hồ sơ hoặc chuyển luồng thẩm định đặc biệt.

### 5. Bộ ba biến REM Residuals (Ab_CFO, Ab_PROD, Ab_DISEXP)
Đo lường các hành vi thao túng thông qua hoạt động kinh doanh thực tế thay vì các bút toán dồn tích (accruals):
* **Ab_CFO < -0.05**: Doanh nghiệp đẩy doanh thu bằng cách nới lỏng tín dụng thương mại quá mức hoặc chiết khấu mạnh $\rightarrow$ dòng tiền từ hoạt động kinh doanh suy giảm bất thường so với mức doanh thu báo cáo.
* **Ab_PROD > 0.05**: Hành vi sản xuất vượt công suất nhu cầu (Overproduction) $\rightarrow$ tồn kho tích lũy tăng vọt để làm giảm chi phí cố định phân bổ trên mỗi đơn vị sản phẩm $\rightarrow$ tăng biên lợi nhuận danh nghĩa.
* **Ab_DISEXP < -0.03**: Cắt giảm mạnh chi phí bán hàng, chi phí quản lý tùy quyết để làm đẹp lợi nhuận ngắn hạn $\rightarrow$ gây tổn hại đến sức khỏe dài hạn của doanh nghiệp.

---

## 3. Điều kiện áp dụng và giới hạn sử dụng

Hệ thống tính toán EWS yêu cầu tuân thủ nghiêm ngặt các điều kiện biên dưới đây để tránh đưa ra kết luận sai lệch:

### 1. Yêu cầu về chuỗi thời gian dữ liệu (Data History)
* **Không yêu cầu năm trước (Tính được ngay trên BCTC hiện tại)**: Altman Z'-Score, SA Index.
* **Yêu cầu tối thiểu 2 năm liên tiếp**: Beneish M-Score, Dechow F-Score, KZ Index, WW Index (để tính toán các biến thay đổi tăng trưởng $\Delta$, dồn tích $TATA$, thay đổi đòn bẩy $LVGI$).
* **Yêu cầu tối thiểu 3 năm liên tiếp**: Các biến REM (Ab_CFO, Ab_PROD, Ab_DISEXP) vì công thức ước lượng yêu cầu trễ hai năm ($\Delta Sales_{t-1}$).

### 2. Ngoại lệ loại trừ ngành (Sector Exclusions)
* **Loại trừ tuyệt đối**: Các công ty tài chính, ngân hàng, công ty bảo hiểm (Nhóm mã SIC 6000-6500) và các công ty tiện ích điện, nước công cộng (Nhóm mã SIC 4400-5000). Cấu trúc tài sản của các nhóm này hoàn toàn khác biệt so với doanh nghiệp phi tài chính thông thường.
* **Lọc ngành sản xuất cho Ab_PROD**: Chỉ số chi phí sản xuất bất thường ($Ab\_PROD$) chỉ có ý nghĩa thực tế đối với các doanh nghiệp thuộc ngành sản xuất, xây dựng (manufacturing). Không áp dụng đối với doanh nghiệp dịch vụ hoặc thương mại thuần túy.

---

## 4. Các quy tắc kết hợp cảnh báo (Synthetic Red Flags)

Để nâng cao độ chính xác và giảm thiểu báo động giả, cán bộ thẩm định cần áp dụng các quy tắc kết hợp sau:

### Quy tắc 1: Cờ đỏ tổng hợp REM (Real Activities Manipulation)
> [!IMPORTANT]
> **Tín hiệu cảnh báo đỏ REM tổng hợp cực mạnh:**
> Nếu đồng thời xảy ra cả 3 điều kiện:
> $$\text{Ab\_CFO} < -0.05 \quad \text{AND} \quad \text{Ab\_PROD} > 0.05 \quad \text{AND} \quad \text{Ab\_DISEXP} < -0.03$$
> Doanh nghiệp đang nỗ lực tối đa để thổi phồng lợi nhuận trước kỳ vay vốn bằng cách chiết khấu bán hàng kích cầu (giảm CFO), sản xuất ồ ạt giảm giá vốn (tăng PROD) và cắt giảm chi phí hoạt động (giảm DISEXP). Đây là dấu hiệu lừa đảo tín dụng điển hình.

### Quy tắc 2: Sự đồng thuận giữa Beneish M-Score và Dechow F-Score
* Nếu cả **M-Score > -1.78** và **F-Score > 1.85**: Báo cáo tài chính của doanh nghiệp bị bóp méo nghiêm trọng. Mọi thông tin về khả năng sinh lời báo cáo đều không đáng tin cậy.

---

## 5. Khuyến nghị áp dụng thực tế tại thị trường Việt Nam

Dựa trên đánh giá khả năng tương thích của các mô hình gốc (xây dựng trên dữ liệu doanh nghiệp Mỹ) với thực tế doanh nghiệp Việt Nam (phân tích tại sheet *Tổng hợp đánh giá*):

1. **Chỉ số Khả thi nhất để Triển khai Ngay**:
   * **SA Index**: Cực kỳ dễ tính (chỉ cần Tổng tài sản và tuổi doanh nghiệp), không cần dữ liệu giá cổ phiếu, ít bị nội sinh, hoạt động tốt đối với cả doanh nghiệp tư nhân chưa niêm yết.
   * **Beneish M-Score (1999)**: Rất phù hợp, các khoản phải thu ($DSRI$) đặc biệt nhạy cảm với hành vi cố tình đẩy doanh thu để làm đẹp hồ sơ vay vốn tại Việt Nam.

2. **Chỉ số cần Thận trọng và Điều chỉnh Ngưỡng**:
   * **Altman Z'-Score**: Do đặc thù các doanh nghiệp bất động sản và xây dựng Việt Nam thường có đòn bẩy tài chính cực kỳ cao theo cơ cấu ngành $\rightarrow$ Z-Score thường bị đánh tụt xuống vùng nguy hiểm. Cán bộ thẩm định cần so sánh Z-Score trong cùng ngành thay vì so sánh tuyệt đối với ngưỡng $1.23$.
   * **Dechow F-Score**: Bắt buộc phải tái ước lượng tỷ lệ gian lận thực tế của thị trường Việt Nam (Unconditional Probability) thay vì sử dụng hệ số $0.0037$ của Mỹ để tránh lệch điểm.

3. **Chỉ số Không khuyến nghị sử dụng độc lập**:
   * **KZ Index**: Do yêu cầu biến cơ hội đầu tư Tobin's Q (đòi hỏi giá thị trường cổ phiếu) nên không thể áp dụng cho các doanh nghiệp chưa niêm yết (chiếm phần lớn tệp khách hàng vay). Đồng thời chỉ số này dễ bị nhầm lẫn giữa thắt chặt tài chính với kiệt quệ tài chính thực tế.
