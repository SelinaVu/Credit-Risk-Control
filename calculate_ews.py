import os
import math
import numpy as np
import pandas as pd
from datetime import datetime
from vnstock import Company, Fundamental

def get_value(df, item_id, year):
    col = str(year)
    if col not in df.columns:
        return 0.0
    row = df[df['item_id'] == item_id]
    if row.empty:
        # Try exact matching with item name if item_id is missing/different
        return 0.0
    val = row.iloc[0][col]
    return float(val) if pd.notna(val) else 0.0

def calculate_ews_for_symbols(symbols, years=[2022, 2023, 2024]):
    report_data = []
    
    for symbol in symbols:
        print(f"\nProcessing {symbol}...")
        try:
            # 1. Get company info to calculate Age
            c = Company(symbol=symbol, source="KBS")
            info_df = c.info()
            founded_date = info_df.iloc[0]['founded_date']
            # parse founded year
            try:
                founded_year = int(founded_date.split('/')[-1])
            except Exception:
                founded_year = 2000 # fallback
            
            # 2. Get Financial Statements from VCI (most complete)
            eq = Fundamental().equity(symbol=symbol)
            bs = eq.balance_sheet(period="year", source="VCI")
            is_ = eq.income_statement(period="year", source="VCI")
            cf = eq.cash_flow(period="year", source="VCI")
            
            if bs.empty or is_.empty:
                print(f"Skipping {symbol} due to empty financial statements.")
                continue
                
            symbol_results = {}
            
            for y in years:
                # Get variables for year y
                ta = get_value(bs, 'total_assets', y)
                if ta == 0.0:
                    # try to sum current and long term assets
                    ca_t = get_value(bs, 'current_assets', y)
                    la_t = get_value(bs, 'long_term_assets', y)
                    ta = ca_t + la_t
                    
                if ta == 0.0:
                    continue # Skip if no asset data
                    
                ca = get_value(bs, 'current_assets', y)
                cl = get_value(bs, 'current_liabilities', y)
                wc = ca - cl
                
                re = get_value(bs, 'undistributed_earnings', y)
                if re == 0.0:
                    re = get_value(bs, 'beginning_accumulated_undistributed_earnings', y) + get_value(bs, 'current_period_undistributed_earnings', y)
                
                ebit_pre_tax = get_value(is_, 'net_accounting_profit_loss_before_tax', y)
                interest = get_value(is_, 'interest_expenses', y)
                ebit = ebit_pre_tax + interest
                
                eq_book = get_value(bs, 'owners_equity', y)
                liab = get_value(bs, 'liabilities', y)
                if liab == 0.0:
                    liab = get_value(bs, 'current_liabilities', y) + get_value(bs, 'long_term_liabilities', y)
                    
                sales = get_value(is_, 'net_sales', y)
                if sales == 0.0:
                    sales = get_value(is_, 'sales', y)
                
                # A. Altman Z'-Score
                x1 = wc / ta if ta != 0 else 0
                x2 = re / ta if ta != 0 else 0
                x3 = ebit / ta if ta != 0 else 0
                x4 = eq_book / liab if liab != 0 else 0
                x5 = sales / ta if ta != 0 else 0
                
                z_prime = 0.717 * x1 + 0.847 * x2 + 3.107 * x3 + 0.420 * x4 + 0.998 * x5
                
                # Z-Score Classification
                if z_prime > 2.9:
                    z_class = "Safe (An toàn)"
                elif z_prime > 1.23:
                    z_class = "Gray Zone (Vùng xám)"
                else:
                    z_class = "Distress (Nguy hiểm)"
                    
                # B. SA Index
                # Size = ln(Total Assets in USD millions). Exchange rate: 25000 VND/USD
                ta_usd_m = ta / (25000 * 1000000)
                size_sa = math.log(ta_usd_m) if ta_usd_m > 0 else 0
                # Cap Size at ln(4500) as in Hadlock & Pierce (2010)
                size_sa = min(size_sa, math.log(4500.0))
                
                age = max(y - founded_year, 1)
                # Cap Age at 37 as in Hadlock & Pierce (2010)
                age_sa = min(age, 37)
                
                sa_index = -0.737 * size_sa + 0.043 * (size_sa ** 2) - 0.040 * age_sa
                
                # C. Financial Controls
                size_vnd = math.log(ta) if ta > 0 else 0
                lev = liab / ta if ta != 0 else 0
                roa = get_value(is_, 'net_profit_loss_after_tax', y) / ta if ta != 0 else 0
                cfo = get_value(cf, 'net_cash_inflows_outflows_from_operating_activities', y)
                cf_ratio = cfo / ta if ta != 0 else 0
                
                # Soft assets ratio
                ppe = get_value(bs, 'tangible_fixed_assets', y)
                if ppe == 0.0:
                    ppe = get_value(bs, 'fixed_assets', y)
                cash = get_value(bs, 'cash_and_cash_equivalents', y)
                soft_ratio = (ta - ppe - cash) / ta if ta != 0 else 0
                
                symbol_results[y] = {
                    'wc': wc, 'ta': ta, 're': re, 'ebit': ebit, 'eq_book': eq_book, 'liab': liab, 'sales': sales,
                    'z_prime': z_prime, 'z_class': z_class, 'sa_index': sa_index, 'age': age,
                    'size_vnd': size_vnd, 'lev': lev, 'roa': roa, 'cfo': cfo, 'cf_ratio': cf_ratio,
                    'ppe': ppe, 'cash': cash, 'soft_ratio': soft_ratio, 'ca': ca, 'cl': cl,
                    'rec': get_value(bs, 'trade_accounts_receivable', y) or get_value(bs, 'accounts_receivable', y),
                    'inv': get_value(bs, 'inventories_net', y) or get_value(bs, 'inventories', y),
                    'cogs': get_value(is_, 'cost_of_sales', y),
                    'dep': get_value(cf, 'depreciation_and_amortization', y),
                    'sga': get_value(is_, 'selling_expenses', y) + get_value(is_, 'general_and_admin_expenses', y),
                    'st_debt': get_value(bs, 'short_term_borrowings', y)
                }

            # D. Beneish M-Score (Requires t and t-1, so calculated for 2023 and 2024)
            m_scores = {}
            for y in [2023, 2024]:
                if y in symbol_results and (y-1) in symbol_results:
                    curr = symbol_results[y]
                    prev = symbol_results[y-1]
                    
                    # 1. DSRI
                    rec_t_sales_t = curr['rec'] / curr['sales'] if curr['sales'] != 0 else 0
                    rec_t1_sales_t1 = prev['rec'] / prev['sales'] if prev['sales'] != 0 else 0
                    dsri = rec_t_sales_t / rec_t1_sales_t1 if rec_t1_sales_t1 != 0 else 1.0
                    
                    # 2. GMI
                    gp_margin_t = (curr['sales'] - curr['cogs']) / curr['sales'] if curr['sales'] != 0 else 0
                    gp_margin_t1 = (prev['sales'] - prev['cogs']) / prev['sales'] if prev['sales'] != 0 else 0
                    gmi = gp_margin_t1 / gp_margin_t if gp_margin_t != 0 else 1.0
                    
                    # 3. AQI
                    aq_t = 1.0 - (curr['ca'] + curr['ppe']) / curr['ta'] if curr['ta'] != 0 else 0
                    aq_t1 = 1.0 - (prev['ca'] + prev['ppe']) / prev['ta'] if prev['ta'] != 0 else 0
                    aqi = aq_t / aq_t1 if aq_t1 != 0 else 1.0
                    
                    # 4. SGI
                    sgi = curr['sales'] / prev['sales'] if prev['sales'] != 0 else 1.0
                    
                    # 5. DEPI
                    dep_rate_t = curr['dep'] / (curr['ppe'] + curr['dep']) if (curr['ppe'] + curr['dep']) != 0 else 0
                    dep_rate_t1 = prev['dep'] / (prev['ppe'] + prev['dep']) if (prev['ppe'] + prev['dep']) != 0 else 0
                    depi = dep_rate_t1 / dep_rate_t if dep_rate_t != 0 else 1.0
                    
                    # 6. SGAI
                    sga_t_sales_t = curr['sga'] / curr['sales'] if curr['sales'] != 0 else 0
                    sga_t1_sales_t1 = prev['sga'] / prev['sales'] if prev['sales'] != 0 else 0
                    sgai = sga_t_sales_t / sga_t1_sales_t1 if sga_t1_sales_t1 != 0 else 1.0
                    
                    # 7. LVGI
                    lev_t = curr['liab'] / curr['ta'] if curr['ta'] != 0 else 0
                    lev_t1 = prev['liab'] / prev['ta'] if prev['ta'] != 0 else 0
                    lvgi = lev_t / lev_t1 if lev_t1 != 0 else 1.0
                    
                    # 8. TATA
                    d_ca = curr['ca'] - prev['ca']
                    d_cash = curr['cash'] - prev['cash']
                    d_cl = curr['cl'] - prev['cl']
                    d_st_debt = curr['st_debt'] - prev['st_debt']
                    tata_accruals = d_ca - d_cash - d_cl + d_st_debt - curr['dep']
                    tata = tata_accruals / curr['ta'] if curr['ta'] != 0 else 0
                    
                    # Calculate M
                    m_val = -4.84 + 0.920*dsri + 0.528*gmi + 0.404*aqi + 0.892*sgi + 0.115*depi - 0.172*sgai + 4.679*tata - 0.327*lvgi
                    
                    m_class = "Manipulation Suspected (Có dấu hiệu thao túng)" if m_val > -1.78 else "Normal (Bình thường)"
                    
                    m_scores[y] = {
                        'dsri': dsri, 'gmi': gmi, 'aqi': aqi, 'sgi': sgi, 'depi': depi,
                        'sgai': sgai, 'lvgi': lvgi, 'tata': tata, 'm_val': m_val, 'm_class': m_class
                    }
            
            # Save results
            report_data.append({
                'symbol': symbol,
                'financials': symbol_results,
                'beneish': m_scores,
                'founded_year': founded_year
            })
            
        except Exception as e:
            print(f"Error calculating EWS for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            
    # 3. Write Markdown Report
    write_md_report(report_data, years)

def write_md_report(data, years):
    artifact_dir = "/Users/tungnguyen/.gemini/antigravity/brain/8a4d4da0-7405-4ace-9552-f4d089f58a2a"
    os.makedirs(artifact_dir, exist_ok=True)
    report_path = f"{artifact_dir}/ews_calculated_report.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Báo Cáo Tính Toán Chỉ Số Cảnh Báo Sớm (EWS)\n")
        f.write(f"*Thời gian thực hiện: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n\n")
        
        f.write("> [!NOTE]\n")
        f.write("> Báo cáo này tự động lấy dữ liệu lịch sử từ **Vnstock API** và áp dụng các công thức định chuẩn rủi ro từ bộ EWS cập nhật.\n\n")
        
        for item in data:
            symbol = item['symbol']
            f.write(f"## Doanh nghiệp: {symbol}\n")
            f.write(f"* Năm thành lập: {item['founded_year']}\n\n")
            
            # Table 1: Altman Z' & SA Index
            f.write("### 1. Phân Tích Rủi Ro Tín Dụng & Ràng Buộc Tài Chính\n")
            f.write("| Năm | Altman Z'-Score | Phân loại rủi ro | SA Index (Constraints) | Độ tuổi DN | Quy mô TS (Tỷ VND) | Đòn bẩy (LEV) |\n")
            f.write("| :--- | :---: | :--- | :---: | :---: | :---: | :---: |\n")
            for y in sorted(item['financials'].keys()):
                fin = item['financials'][y]
                f.write(f"| {y} | {fin['z_prime']:.3f} | {fin['z_class']} | {fin['sa_index']:.3f} | {fin['age']} | {fin['ta']/1e9:,.1f} | {fin['lev']:.2%} |\n")
            f.write("\n")
            
            # Table 2: Beneish M-Score
            f.write("### 2. Phân Tích Thao Túng Lợi Nhuận (Beneish M-Score)\n")
            f.write("| Năm | M-Score | Phân loại | DSRI (Phải thu) | GMI (Biên gộp) | AQI (Tài sản) | SGI (Tăng trưởng) | TATA (Dồn tích) |\n")
            f.write("| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |\n")
            for y in [2023, 2024]:
                if y in item['beneish']:
                    m = item['beneish'][y]
                    f.write(f"| {y} | {m['m_val']:.3f} | {m['m_class']} | {m['dsri']:.3f} | {m['gmi']:.3f} | {m['aqi']:.3f} | {m['sgi']:.3f} | {m['tata']:.3f} |\n")
            f.write("\n")
            
            # Details and Red flags
            f.write("### 3. Đánh giá chất lượng BCTC & Cảnh báo rủi ro\n")
            # Loop for warnings
            for y in sorted(item['financials'].keys()):
                fin = item['financials'][y]
                f.write(f"**Năm {y}:**\n")
                flags = []
                if fin['lev'] > 0.70:
                    flags.append(f"🔴 Đòn bẩy tài chính cao ({fin['lev']:.1%}) vượt ngưỡng an toàn.")
                if fin['z_prime'] <= 1.23:
                    flags.append(f"🔴 Altman Z'-Score ({fin['z_prime']:.3f}) nằm trong vùng nguy hiểm.")
                elif fin['z_prime'] <= 2.90:
                    flags.append(f"🟡 Altman Z'-Score ({fin['z_prime']:.3f}) nằm trong vùng xám (Cần giám sát).")
                
                if fin['roa'] < 0:
                    flags.append(f"🔴 Hoạt động thua lỗ (ROA: {fin['roa']:.1%}).")
                if fin['cf_ratio'] < 0:
                    flags.append(f"🔴 Dòng tiền từ hoạt động kinh doanh âm (CFO/TA: {fin['cf_ratio']:.1%}).")
                
                # Accrual warning
                if abs(fin['soft_ratio']) > 0.60:
                    flags.append(f"🟡 Tỷ trọng tài sản mềm cao ({fin['soft_ratio']:.1%}), thể hiện phần lớn tài sản nằm ở khoản phải thu và tồn kho.")
                
                if y in item['beneish']:
                    m = item['beneish'][y]
                    if m['m_val'] > -1.78:
                        flags.append(f"🔴 Điểm Beneish M-Score ({m['m_val']:.3f}) vượt ngưỡng cảnh báo. Nghi ngờ có thao túng lợi nhuận (Accrual/Sales).")
                    if m['dsri'] > 1.20:
                        flags.append(f"🟡 Biến DSRI ({m['dsri']:.3f}) tăng mạnh, báo hiệu các khoản phải thu tăng trưởng bất thường so với doanh thu.")
                    if abs(m['tata']) > 0.15:
                        flags.append(f"🟡 Biến dồn tích TATA ({m['tata']:.3f}) ở mức cao, chất lượng lợi nhuận thấp.")
                
                if flags:
                    for flag in flags:
                        f.write(f"- {flag}\n")
                else:
                    f.write("- ✅ BCTC lành mạnh, chưa phát hiện tín hiệu cảnh báo rủi ro lớn.\n")
                f.write("\n")
                
            f.write("---\n\n")
            
    print(f"Report generated successfully at: {report_path}")

if __name__ == "__main__":
    calculate_ews_for_symbols(['FPT', 'HPG', 'VNM'])
