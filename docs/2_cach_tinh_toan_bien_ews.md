# PHƯƠNG PHÁP TÍNH TOÁN 10 CHỈ SỐ CẢNH BÁO SỚM (EWS)

Tài liệu này hướng dẫn chi tiết các công thức toán học, định nghĩa biến số đầu vào và logic lập trình cho **10 chỉ số cảnh báo sớm** được sử dụng trong hệ thống quản trị rủi ro tín dụng.

---

## Ký hiệu viết tắt các biến số BCTC đầu vào
* $TA_t$: Tổng tài sản cuối kỳ $t$ (Mã 270)
* $CA_t$: Tài sản ngắn hạn cuối kỳ $t$ (Mã 100)
* $CL_t$: Nợ ngắn hạn cuối kỳ $t$ (Mã 310)
* $RE_t$: Lợi nhuận sau thuế chưa phân phối cuối kỳ $t$ (Mã 421)
* $EBT_t$: Lợi nhuận trước thuế kỳ $t$ (Mã 50)
* $Interest_t$: Chi phí lãi vay kỳ $t$ (Mã 23)
* $Equity_t$: Vốn chủ sở hữu kỳ $t$ (Mã 400)
* $Liab_t$: Tổng nợ phải trả kỳ $t$ (Mã 300)
* $Sales_t$: Doanh thu thuần kỳ $t$ (Mã 10)
* $COGS_t$: Giá vốn hàng bán kỳ $t$ (Mã 11)
* $Rec_t$: Phải thu khách hàng kỳ $t$ (Mã 131)
* $Inv_t$: Hàng tồn kho cuối kỳ $t$ (Mã 140)
* $FA_t$: Tài sản cố định ròng cuối kỳ $t$ (Mã 220)
* $PPE\_Cost_t$: Nguyên giá TSCĐ hữu hình cuối kỳ $t$ (Mã 221)
* $NI_t$: Lợi nhuận sau thuế kỳ $t$ (Mã 60)
* $OCF_t$: Dòng tiền thuần từ HĐKD kỳ $t$ (Mã 20 LCTT)
* $Cash_t$: Tiền và tương đương tiền cuối kỳ $t$ (Mã 110)

---

## 1. Altman Z'-Score (Dành cho Doanh nghiệp tư nhân)

Mô hình biệt số đa biến (MDA) dùng để dự báo rủi ro kiệt quệ tài chính và phá sản của doanh nghiệp phi sản xuất/tư nhân.

### Công thức:
$$Z' = 0.717 \times X_1 + 0.847 \times X_2 + 3.107 \times X_3 + 0.420 \times X_4 + 0.998 \times X_5$$

### Các biến thành phần:
* $X_1 = \frac{CA_t - CL_t}{TA_t}$ (Tỷ lệ Vốn lưu động ròng / Tổng tài sản)
* $X_2 = \frac{RE_t}{TA_t}$ (Tỷ lệ Lợi nhuận giữ lại tích lũy / Tổng tài sản)
* $X_3 = \frac{EBT_t + Interest_t}{TA_t}$ (Tỷ lệ EBIT / Tổng tài sản)
* $X_4 = \frac{Equity_t}{Liab_t}$ (Tỷ lệ Vốn chủ sở hữu / Tổng nợ phải trả)
* $X_5 = \frac{Sales_t}{TA_t}$ (Vòng quay tổng tài sản)

---

## 2. Size-Age (SA) Index

Chỉ số đo lường mức độ hạn chế tài chính (khó tiếp cận nguồn vốn bên ngoài) dựa hoàn toàn trên quy mô tài sản và tuổi đời của doanh nghiệp.

### Công thức:
$$SA = -0.737 \times Size + 0.043 \times Size^2 - 0.040 \times Age$$

### Định nghĩa biến:
* $Size = \ln(TA_{USD\_M})$, trong đó $TA_{USD\_M}$ là Tổng tài sản quy đổi ra triệu USD:
  $$TA_{USD\_M} = \frac{TA_t}{25,000 \times 1,000,000}$$
  *(Quy đổi tỷ giá $1 \text{ USD} = 25,000 \text{ VND}$. Giá trị $Size$ được chặn trên ở mức $\ln(4500.0)$).*
* $Age$: Số năm doanh nghiệp hoạt động kể từ khi thành lập/niêm yết (được chặn trên ở mức $37$ năm).

---

## 3. Beneish M-Score (Mô hình 8 biến - Phiên bản 1999)

Dùng để phát hiện các dấu hiệu thao túng báo cáo tài chính nhằm thổi phồng lợi nhuận.

### Công thức:
$$M = -4.84 + 0.920 \times DSRI + 0.528 \times GMI + 0.404 \times AQI + 0.892 \times SGI + 0.115 \times DEPI - 0.172 \times SGAI + 4.679 \times TATA - 0.327 \times LVGI$$

### Các tỷ số thành phần:
1. **DSRI (Days Sales in Receivables Index - Chỉ số phải thu trên doanh thu):**
   $$DSRI = \frac{Rec_t / Sales_t}{Rec_{t-1} / Sales_{t-1}}$$
2. **GMI (Gross Margin Index - Chỉ số biên lợi nhuận gộp):**
   $$GMI = \frac{GrossMargin_{t-1}}{GrossMargin_t} \quad \text{với} \quad GrossMargin_t = \frac{Sales_t - COGS_t}{Sales_t}$$
3. **AQI (Asset Quality Index - Chỉ số chất lượng tài sản):**
   $$AQI = \frac{1 - (CA_t + FA_t)/TA_t}{1 - (CA_{t-1} + FA_{t-1})/TA_{t-1}}$$
   *(Phản ánh tỷ lệ tài sản phi truyền thống/tài sản mềm tăng lên).*
4. **SGI (Sales Growth Index - Chỉ số tăng trưởng doanh thu):**
   $$SGI = \frac{Sales_t}{Sales_{t-1}}$$
5. **DEPI (Depreciation Index - Chỉ số khấu hao):**
   $$DEPI = \frac{DepRate_{t-1}}{DepRate_t} \quad \text{với} \quad DepRate_t = \frac{Depreciation_t}{Depreciation_t + PPE\_Cost_t}$$
   *(Nếu thiếu số liệu chi tiết khấu hao trong thuyết minh, mặc định đặt $DEPI = 1.0$).*
6. **SGAI (SG&A Expense Index - Chỉ số chi phí bán hàng và quản lý):**
   $$SGAI = \frac{SGA_t / Sales_t}{SGA_{t-1} / Sales_{t-1}} \quad \text{với} \quad SGA_t = \text{Selling\_Expense}_t + \text{GA\_Expense}_t$$
7. **LVGI (Leverage Index - Chỉ số đòn bẩy):**
   $$LVGI = \frac{Liab_t / TA_t}{Liab_{t-1} / TA_{t-1}}$$
8. **TATA (Total Accruals to Total Assets - Tổng biến dồn tích trên tài sản):**
   $$TATA = \frac{NI_t - OCF_t}{TA_t}$$

---

## 4. Beneish M-Score (Mô hình 12 biến Probit - Phiên bản 1997)

Phiên bản mở rộng của M-Score kết hợp thêm các biến động cơ và bối cảnh thị trường để tính ra xác suất thao túng cụ thể.

### Công thức chỉ số Probit ($Z_{12}$):
$$Z_{12} = Z_8 - 0.320 \times Ab\_Return + 0.35 \times Pos\_Accruals + 0.25 \times Dec\_Cash + 0.40 \times Issue\_Sec$$
*(Trong đó $Z_8$ là giá trị tổ hợp tuyến tính của 8 biến ở phần 3 nhưng với hệ số gốc của mô hình Probit: $-3.5 + 0.920 \times DSRI + \dots$).*

### Các biến bổ sung:
* $Ab\_Return$: Tỷ suất sinh lời bất thường của cổ phiếu doanh nghiệp so với thị trường (mặc định $= 0.0$ đối với doanh nghiệp chưa niêm yết).
* $Pos\_Accruals$: Biến giả nhận giá trị $1.0$ nếu $TATA > 0$, ngược lại $= 0.0$.
* $Dec\_Cash$: Biến giả giảm doanh thu tiền mặt, bằng $1.0$ nếu doanh nghiệp có tăng trưởng doanh thu âm ($SGI < 1.0$) đồng thời dòng tiền thấp hơn lợi nhuận ($OCF_t < NI_t$), ngược lại $= 0.0$.
* $Issue\_Sec$: Biến giả phát hành chứng khoán, bằng $1.0$ nếu doanh nghiệp phát hành cổ phiếu hoặc nợ dài hạn trong năm hiện tại để huy động vốn, ngược lại $= 0.0$.

### Tính xác suất thao túng ($P_{12}$):
Xác suất được tính qua hàm phân phối tích lũy chuẩn tắc (Cumulative Normal Distribution):
$$P_{12} = \Phi(Z_{12}) = \frac{1}{2} \left[ 1 + \text{erf}\left( \frac{Z_{12}}{\sqrt{2}} \right) \right]$$

---

## 5. Dechow F-Score (2011)

Chỉ số đo lường xác suất xảy ra gian lận hoặc sai sót trọng yếu trên báo cáo tài chính quy chiếu tương đối với xác suất trung bình của toàn thị trường.

### Bước 1: Tính giá trị dự báo (Predicted Value - PV):
$$PV = -7.893 + 0.790 \times rsst\_acc + 2.518 \times ch\_rec + 1.191 \times ch\_inv + 1.979 \times soft\_assets + 0.171 \times ch\_cs - 0.932 \times ch\_roa + 1.029 \times issue$$

### Các biến thành phần:
* $Average\_TA = 0.5 \times (TA_t + TA_{t-1})$
* $wc_t = (CA_t - Cash_t) - CL_t$ (Vốn lưu động hoạt động)
* $nco_t = (TA_t - CA_t - \text{Đầu tư dài hạn}) - (Total\_Liab_t - CL_t - \text{Nợ dài hạn}) \approx (TA_t - CA_t - FA_t) - (Liab_t - CL_t)$ (Tài sản hoạt động dài hạn ròng)
* $fin_t = Cash_t - (Liab_t - CL_t)$ (Tài sản tài chính ròng)
* $rsst\_acc = \frac{(wc_t - wc_{t-1}) + (nco_t - nco_{t-1}) + (fin_t - fin_{t-1})}{Average\_TA}$ (Biến dồn tích RSST tổng hợp)
* $ch\_rec = \frac{Rec_t - Rec_{t-1}}{Average\_TA}$ (Thay đổi khoản phải thu)
* $ch\_inv = \frac{Inv_t - Inv_{t-1}}{Average\_TA}$ (Thay đổi hàng tồn kho)
* $soft\_assets = \frac{TA_t - FA_t - Cash_t}{TA_t}$ (Tỷ lệ tài sản mềm)
* $ch\_cs = \frac{CashSales_t - CashSales_{t-1}}{CashSales_{t-1}}$ với $CashSales_t = Sales_t - (Rec_t - Rec_{t-1})$
* $ch\_roa = \frac{NI_t}{TA_t} - \frac{NI_{t-1}}{TA_{t-1}}$
* $issue$: Đặt bằng $1.0$ nếu doanh nghiệp phát hành chứng khoán trong năm, ngược lại $= 0.0$.

### Bước 2: Chuyển đổi thành xác suất gian lận ($Prob$):
$$Prob = \frac{e^{PV}}{1 + e^{PV}}$$

### Bước 3: Tính chỉ số F-Score:
$$F\text{-Score} = \frac{Prob}{\text{Unconditional Probability}}$$
*(Mặc định tỷ lệ gian lận trung bình thị trường Unconditional Probability $= 0.0037$ tức $0.37\%$).*

---

## 6. Dòng tiền hoạt động bất thường (Abnormal CFO)

Đo lường sự sai lệch giữa dòng tiền kinh doanh thực tế thu được với dòng tiền lý thuyết ước lượng dựa trên doanh thu.

### Công thức dòng tiền bình thường ước lượng:
$$\frac{Normal\_CFO_t}{TA_{t-1}} = -0.01 \times \left(\frac{1}{TA_{t-1}}\right) + 0.09 \times \left(\frac{Sales_t}{TA_{t-1}}\right) - 0.02 \times \left(\frac{Sales_t - Sales_{t-1}}{TA_{t-1}}\right)$$

### Tính phần dư bất thường (Ab_CFO):
$$Ab\_CFO = \frac{OCF_t}{TA_{t-1}} - \frac{Normal\_CFO_t}{TA_{t-1}}$$

---

## 7. Chi phí sản xuất bất thường (Abnormal Production)

Phát hiện hành vi sản xuất dư thừa (overproduction) để phân bổ chi phí cố định cho nhiều sản phẩm hơn, qua đó giảm giá vốn hàng bán (COGS) trên mỗi đơn vị và nâng khống lợi nhuận.

### Bước 1: Tính chi phí sản xuất thực tế ($PROD_t$):
$$PROD_t = COGS_t + (Inv_t - Inv_{t-1})$$

### Bước 2: Ước lượng chi phí sản xuất bình thường:
$$\frac{Normal\_PROD_t}{TA_{t-1}} = 0.03 \times \left(\frac{1}{TA_{t-1}}\right) + 0.82 \times \left(\frac{Sales_t}{TA_{t-1}}\right) + 0.12 \times \left(\frac{Sales_t - Sales_{t-1}}{TA_{t-1}}\right) - 0.05 \times \left(\frac{\Delta Sales_{t-1}}{TA_{t-1}}\right)$$
*(Trong đó $\Delta Sales_{t-1} = Sales_{t-1} - Sales_{t-2}$. Nếu thiếu năm $t-2$, hệ thống sử dụng $\Delta Sales_t$ thay thế).*

### Bước 3: Tính phần dư bất thường (Ab_PROD):
$$Ab\_PROD = \frac{PROD_t}{TA_{t-1}} - \frac{Normal\_PROD_t}{TA_{t-1}}$$

---

## 8. Chi phí tùy quyết bất thường (Abnormal Discretionary Expenses)

Phát hiện hành vi cắt giảm bất thường các chi phí bán hàng, quản lý, quảng cáo và nghiên cứu phát triển (SG&A, R&D) để tăng lợi nhuận báo cáo trong ngắn hạn.

### Công thức chi phí tùy quyết bình thường ước lượng:
$$\frac{Normal\_DISEXP_t}{TA_{t-1}} = 0.01 \times \left(\frac{1}{TA_{t-1}}\right) + 0.06 \times \left(\frac{Sales_{t-1}}{TA_{t-1}}\right)$$

### Tính phần dư bất thường (Ab_DISEXP):
$$Ab\_DISEXP = \frac{\text{Selling\_Expense}_t + \text{GA\_Expense}_t}{TA_{t-1}} - \frac{Normal\_DISEXP_t}{TA_{t-1}}$$

---

## 9. Kaplan-Zingales (KZ) Index

Chỉ số đo lường mức độ thắt chặt tài chính tổng hợp từ đòn bẩy, dự trữ tiền mặt, dòng tiền và phân phối cổ tức.

### Công thức:
$$KZ = -1.002 \times \left(\frac{CF_t}{K_{t-1}}\right) + 0.283 \times Tobin\_Q + 3.139 \times \left(\frac{Debt_t}{K_{t-1}}\right) - 39.368 \times \left(\frac{Div_t}{K_{t-1}}\right) - 1.315 \times \left(\frac{Cash_t}{K_{t-1}}\right)$$

### Định nghĩa biến số quy đổi:
* $K_{t-1}$: Giá trị tài sản cố định ròng đầu kỳ ($FA_{t-1}$). Nếu thiếu, sử dụng Tổng tài sản đầu kỳ ($TA_{t-1}$) thay thế.
* $CF_t$: Dòng tiền tạo ra trong kỳ, ước tính bằng: $NI_t + 0.05 \times FA_t$.
* $Debt_t$: Tổng nợ phải trả ($Liab_t$).
* $Div_t$: Cổ tức chi trả trong năm, ước tính bằng: $div\_ratio \times NI_t$ (mặc định $div\_ratio = 0.0$).
* $Cash_t$: Tiền và tương đương tiền ($Cash_t$).
* $Tobin\_Q$: Chỉ số cơ hội đầu tư của doanh nghiệp (mặc định gán bằng $1.2$ nếu thiếu thông tin vốn hóa thị trường).

---

## 10. Whited-Wu (WW) Index

Chỉ số đo lường ràng buộc tài chính thay thế cho KZ Index, loại bỏ biến cơ hội đầu tư Tobin's Q vốn nhạy cảm với biến động giá cổ phiếu.

### Công thức:
$$WW = -0.091 \times CF\_WW_t - 0.062 \times DIVPOS_t + 0.021 \times TLTD_t - 0.044 \times LNTA_t + 0.102 \times ISG_t - 0.035 \times SG_t$$

### Định nghĩa biến số quy đổi:
* $CF\_WW_t = \frac{NI_t + 0.05 \times FA_t}{TA_t}$ (Tỷ lệ dòng tiền trên tổng tài sản)
* $DIVPOS_t$: Biến giả cổ tức, bằng $1.0$ nếu doanh nghiệp có chi trả cổ tức tiền mặt ($Div_t > 0$), ngược lại $= 0.0$.
* $TLTD_t = \frac{Liab_t - CL_t}{TA_t}$ (Tỷ lệ nợ dài hạn trên tổng tài sản)
* $LNTA_t = \ln(TA_t / 25000 / 1,000,000)$ (Tổng tài sản quy đổi ra triệu USD, chặn dưới ở mức $0.001$).
* $ISG_t$: Tốc độ tăng trưởng doanh thu trung bình của ngành kinh doanh (mặc định bằng $0.08$ tức $8.0\%$).
* $SG_t = \frac{Sales_t - Sales_{t-1}}{Sales_{t-1}}$ (Tốc độ tăng trưởng doanh thu của riêng doanh nghiệp).
