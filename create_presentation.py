import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # Color Palette
    COLOR_PRIMARY_DARK = RGBColor(16, 44, 87)     # #102C57 Deep Navy
    COLOR_PRIMARY_BLUE = RGBColor(31, 78, 121)    # #1F4E79 Classic Blue
    COLOR_ACCENT_TEAL = RGBColor(0, 128, 128)     # #008080 Teal
    COLOR_ACCENT_GOLD = RGBColor(218, 165, 32)    # #DAA520 Gold
    COLOR_CARD_BG = RGBColor(245, 247, 250)       # #F5F7FA Light Card
    COLOR_TEXT_DARK = RGBColor(33, 37, 41)        # #212529 Dark text
    COLOR_TEXT_MUTED = RGBColor(108, 117, 125)    # #6C757D Gray text
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_SUCCESS = RGBColor(40, 167, 69)         # Green
    COLOR_WARNING = RGBColor(255, 193, 7)         # Yellow

    def add_header(slide, title_text, category_text="FINTRUST EWS - HỆ THỐNG GIÁM SÁT RỦI RO TÍN DỤNG THÔNG MINH"):
        # Top banner background
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = COLOR_PRIMARY_DARK
        top_bar.line.fill.background()

        # Category text
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.5), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT_GOLD

        # Title text
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(11.5), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

        # Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.3))
        tf_foot = footer_box.text_frame
        p_foot = tf_foot.paragraphs[0]
        p_foot.text = "FinTrust EWS • Báo cáo Thẩm định Cấp Tín dụng & Giám sát Cảnh báo Sớm • Thông tư 200/2014/TT-BTC & Basel II/III"
        p_foot.font.size = Pt(10)
        p_foot.font.color.rgb = COLOR_TEXT_MUTED

    def create_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_PRIMARY_BLUE):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1.5)
        else:
            shape.line.fill.background()
        return shape

    # =========================================================================
    # SLIDE 1: COVER SLIDE
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_slide_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_PRIMARY_DARK
    bg1.line.fill.background()

    # Title box
    tbox = slide1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(10.9), Inches(3.0))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "BÁO CÁO KHOA HỌC & GIẢI TRÌNH HỘI ĐỒNG"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_ACCENT_GOLD
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "HỆ THỐNG FINTRUST EWS\nĐỊNH LƯỢNG RỦI RO TÍN DỤNG & THẨM ĐỊNH CẤP VỐN LƯU ĐỘNG"
    p1.font.size = Pt(30)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_after = Pt(16)

    p2 = tf1.add_paragraph()
    p2.text = "Nền tảng Tự động hóa Ingestion BCTC (PDF/Excel), Chuẩn hóa Thông tư 200, Bóc tách Chu kỳ Tiền mặt,\nMô hình Cảnh báo Sớm EWS và Tạo Tờ trình Thẩm định Tín dụng Chuẩn Ngân hàng Thương mại"
    p2.font.size = Pt(15)
    p2.font.color.rgb = RGBColor(200, 215, 235)

    # Info card at bottom
    c1 = create_card(slide1, Inches(1.2), Inches(5.0), Inches(10.9), Inches(1.6), bg_color=RGBColor(24, 58, 107), border_color=COLOR_ACCENT_GOLD)
    info_box = slide1.shapes.add_textbox(Inches(1.5), Inches(5.1), Inches(10.3), Inches(1.4))
    itf = info_box.text_frame
    ip1 = itf.paragraphs[0]
    ip1.text = "🎯 ĐƠN VỊ NGHIÊN CỨU & ỨNG DỤNG:"
    ip1.font.size = Pt(12)
    ip1.font.bold = True
    ip1.font.color.rgb = COLOR_ACCENT_GOLD
    ip2 = itf.add_paragraph()
    ip2.text = "• Đề tài: Kiểm soát Rủi ro Tín dụng & Xây dựng Hệ thống Cảnh báo Sớm cho Doanh nghiệp Việt Nam\n• Đối tượng: Khối Quản trị Rủi ro, Khối Phê duyệt Tín dụng KHDN tại các Ngân hàng Thương mại\n• Mã nguồn & Triển khai: GitHub Repositories • Nền tảng Cloud Streamlit Serverless"
    ip2.font.size = Pt(11)
    ip2.font.color.rgb = COLOR_WHITE

    # =========================================================================
    # SLIDE 2: BỐI CẢNH & NỖI ĐAU THỰC TIỄN
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide2, "1. Bối cảnh Nghiên cứu & 3 Thách thức Lớn trong Thẩm định Tín dụng")

    cards_data_s2 = [
        ("NỖI ĐAU 1: NHẬP LIỆU THỦ CÔNG", "⏳ Chậm trễ & Rủi ro sai số học", [
            "Chuyên viên thẩm định (CBTD) mất từ 3 - 5 giờ để gõ tay BCTC dạng PDF/Scan vào bảng Excel tính toán.",
            "Tỷ lệ lỗi do con người (Typo, lệch năm, dính số thuyết minh) chiếm tới 15 - 25% các tờ trình tín dụng.",
            "Khó khăn trong việc đối soát tính cân đối giữa Bảng CĐKT, KQKD và LCTT theo chuẩn Thông tư 200."
        ]),
        ("NỖI ĐAU 2: GIAN LẬN SỔ SÁCH", "📉 Thao túng lợi nhuận tinh vi", [
            "Doanh nghiệp đi vay thường sử dụng các thủ thuật 'Earnings Management' (ghi nhận trước doanh thu, vốn hóa chi phí, dồn tích ảo).",
            "Mắt thường rất khó phát hiện dấu hiệu bất thường nếu chỉ nhìn vào báo cáo lãi/lỗ đơn thuần.",
            "Hậu quả: Ngân hàng giải ngân vào các hồ sơ 'bệnh nặng', dẫn tới nợ xấu phát sinh đột ngột sau 1 - 2 năm."
        ]),
        ("NỖI ĐAU 3: THẨM ĐỊNH TĨNH CÀO BẰNG", "📊 Thiếu bóc tách thực tế", [
            "Hầu hết mô hình thẩm định hiện nay chỉ tính toán chỉ số gộp toàn công ty, không bóc tách được phương án vay cụ thể.",
            "Doanh nghiệp đa ngành vay vốn cho 1 mảng kinh doanh nhưng lại dùng vòng quay chung của toàn công ty để cấp hạn mức.",
            "Thiếu công cụ đối chiếu tự động với Benchmark của từng phân ngành kinh tế Việt Nam."
        ])
    ]

    for idx, (title, subtitle, bullets) in enumerate(cards_data_s2):
        left = Inches(0.8 + idx * 4.0)
        create_card(slide2, left, Inches(1.5), Inches(3.733), Inches(5.2))
        tb = slide2.shapes.add_textbox(left + Inches(0.2), Inches(1.7), Inches(3.333), Inches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_PRIMARY_DARK
        
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = COLOR_PRIMARY_BLUE
        p_sub.space_after = Pt(12)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.size = Pt(10.5)
            p_b.font.color.rgb = COLOR_TEXT_DARK
            p_b.space_after = Pt(8)

    # =========================================================================
    # SLIDE 3: CƠ SỞ KHOA HỌC & HỆ THỐNG MÔ HÌNH EWS (TRẢ LỜI THẦY CÔ)
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide3, "2. Cơ sở Khoa học: Hệ thống 10 Chỉ số Cảnh báo Sớm EWS Định lượng")

    create_card(slide3, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb_left = slide3.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tfl = tb_left.text_frame
    tfl.word_wrap = True

    p = tfl.paragraphs[0]
    p.text = "🏛️ KHUNG MÔ HÌNH HỌC THUẬT QUỐC TẾ"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_DARK

    models = [
        ("1. Altman Z'-Score (Private / Emerging)", "Định lượng xác suất vỡ nợ cho DN tư nhân & TT mới nổi với 5 biến tài chính (Working Capital, RE, EBIT, BV Equity, Sales)."),
        ("2. Beneish M-Score (1999 - 8 Biến)", "Phát hiện thao túng BCTC thông qua phân tích dồn tích, biên lợi nhuận, khấu hao, chi phí bán hàng (DSRI, GMI, AQI, SGI, DEPI, SGAI, TATA, LVGI)."),
        ("3. Dechow F-Score (2011)", "Dự báo xác suất BCTC phải cải chính (Restatement) do sai lệch kế toán nghiêm trọng."),
        ("4. SA Index (Hadlock & Pierce, 2010)", "Đo lường mức độ thắt chặt/hạn chế tài chính (Financial Constraints) dựa trên Quy mô tài sản (Size) và Tuổi doanh nghiệp (Age)."),
        ("5. Bất thường Dòng tiền (Roychowdhury 2006)", "Bóc tách dòng tiền HĐKD dị biệt (Ab_CFO), chi phí sản xuất dư thừa (Ab_PROD), và cắt giảm chi phí tùy ý (Ab_DISEXP).")
    ]
    for m_name, m_desc in models:
        pm = tfl.add_paragraph()
        pm.text = f"▶ {m_name}:"
        pm.font.size = Pt(11)
        pm.font.bold = True
        pm.font.color.rgb = COLOR_PRIMARY_BLUE
        pm_d = tfl.add_paragraph()
        pm_d.text = f"   {m_desc}"
        pm_d.font.size = Pt(10)
        pm_d.font.color.rgb = COLOR_TEXT_DARK
        pm_d.space_after = Pt(6)

    create_card(slide3, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb_right = slide3.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tfr = tb_right.text_frame
    tfr.word_wrap = True

    pr = tfr.paragraphs[0]
    pr.text = "⚖️ QUY CHUẨN THÔNG TƯ 200 & BASEL II/III"
    pr.font.size = Pt(14)
    pr.font.bold = True
    pr.font.color.rgb = COLOR_PRIMARY_DARK

    regs = [
        ("6. Chu kỳ chuyển đổi Tiền mặt (CCC)", "Bóc tách từng chặng: Thời gian thu tiền (DSO) + Thời gian tồn kho (DSI) - Thời gian trả tiền NCC (DPO)."),
        ("7. Khả năng bao phủ Nợ & Lãi vay (ICR / DSCR)", "Đo lường số lần EBIT bù đắp chi phí lãi vay (Mã 23) và khả năng trả nợ gốc ngắn hạn."),
        ("8. Chất lượng Vốn tự có & Đòn bẩy tối ưu", "Tái ước lượng định kỳ đòn bẩy tối ưu theo lý thuyết Hồi quy Chữ U (U-Curve Trade-off Theory) cho từng phân ngành."),
        ("9. Kiểm soát Dòng tiền thuần từ HĐKD (OCF)", "Phân tích mối tương quan OCF / Nợ ngắn hạn để phát hiện các DN 'lợi nhuận trên giấy nhưng cạn kiệt tiền mặt'."),
        ("10. Hệ thống Thẻ điểm Xếp hạng Nội bộ AAA -> D", "Ánh xạ xác suất vỡ nợ (PD) sang khung xếp hạng 7 bậc chuẩn Basel phục vụ định giá khoản vay và phân cấp thẩm quyền.")
    ]
    for r_name, r_desc in regs:
        pr_item = tfr.add_paragraph()
        pr_item.text = f"▶ {r_name}:"
        pr_item.font.size = Pt(11)
        pr_item.font.bold = True
        pr_item.font.color.rgb = COLOR_PRIMARY_BLUE
        pr_d = tfr.add_paragraph()
        pr_d.text = f"   {r_desc}"
        pr_d.font.size = Pt(10)
        pr_d.font.color.rgb = COLOR_TEXT_DARK
        pr_d.space_after = Pt(6)

    # =========================================================================
    # SLIDE 4: GIẢI ĐÁP CÁC CÂU HỎI THẮC MẮC CỦA THẦY CÔ & HỘI ĐỒNG (FAQ)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide4, "3. Giải đáp Thắc mắc Chuyên sâu của Hội đồng & Giảng viên (Technical FAQ)")

    faqs = [
        ("❓ Câu hỏi 1: Vì sao mô hình SA Index lại chặn trần tuổi doanh nghiệp tối đa ở mức 37 năm?",
         "💡 Căn cứ khoa học:",
         "Theo nghiên cứu gốc của Hadlock & Pierce (Journal of Financial Studies, 2010), biến Age đại diện cho thâm niên hoạt động được winsorize/chặn trên tại 37 năm (min(Age, 37)) và Quy mô tài sản chặn tại log($4.5B). Quy chuẩn này nhằm ngăn chặn các doanh nghiệp thâm niên quá lớn (ví dụ 50 - 100 năm) làm sai lệch phi tuyến kết quả đo lường mức độ hạn chế tài chính. Phần mềm đã bổ sung tooltip minh bạch hóa quy chuẩn này."),

        ("❓ Câu hỏi 2: Vì sao chỉ số Vòng quay (Turnover) trong phần mềm lệch so với Vietstock hay FiinGroup?",
         "💡 Căn cứ chuẩn mực kế toán:",
         "Các nền tảng dữ liệu thị trường (như Vietstock) tính vòng quay dựa trên Số dư Bình quân = (Đầu kỳ + Cuối kỳ) / 2. Trong khi đó, trong thẩm định tín dụng nhanh tại thời điểm lập báo cáo, CBTD cần đối chiếu số dư tức thời cuối kỳ. Hệ thống FinTrust hỗ trợ đồng thời cả 2 cách tiếp cận và có chú thích chi tiết công thức để hội đồng kiểm chứng."),

        ("❓ Câu hỏi 3: Vì sao phần mềm chỉ áp dụng cho doanh nghiệp Phi tài chính và loại bỏ Ngân hàng/Bảo hiểm?",
         "💡 Căn cứ chế độ kế toán:",
         "Tổ chức tín dụng (NHTM, Bảo hiểm, Chứng khoán) hoạt động theo chế độ kế toán đặc thù của Ngân hàng Nhà nước và Bộ Tài chính, không sử dụng hệ thống tài khoản Thông tư 200/2014/TT-BTC. Các mô hình phá sản chuẩn (Altman Z', Beneish M) không có giá trị thống kê trên bảng cân đối tài chính của ngân hàng. FinTrust tự động nhận diện và phân tách loại trừ thông minh.")
    ]

    for idx, (q, head, a) in enumerate(faqs):
        top = Inches(1.5 + idx * 1.8)
        create_card(slide4, Inches(0.8), top, Inches(11.733), Inches(1.65))
        tb = slide4.shapes.add_textbox(Inches(1.0), top + Inches(0.1), Inches(11.333), Inches(1.45))
        tf = tb.text_frame
        tf.word_wrap = True
        
        pq = tf.paragraphs[0]
        pq.text = q
        pq.font.size = Pt(12)
        pq.font.bold = True
        pq.font.color.rgb = COLOR_PRIMARY_DARK
        
        pa = tf.add_paragraph()
        pa.text = f"{head} {a}"
        pa.font.size = Pt(10.5)
        pa.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 5: CÔNG NGHỆ BÓC TÁCH OCR & BỘ GIẢI TỰ CÂN ĐỐI KẾ TOÁN
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide5, "4. Đột phá Công nghệ: Bộ giải Tự cân đối Kế toán & Khử nhiễu Đa tầng")

    cards_data_s5 = [
        ("LỚP 1: KHỬ NHIỄU OCR ĐA TẦNG", "Xử lý triệt để lỗi scan", [
            "Tách mã chỉ tiêu dính số: Tự động bóc tách tiền tố (vd '300.665.242.118.219' -> Mã 300 & Số tiền 665 tỷ).",
            "Lọc bỏ số Thuyết minh: Nhận diện cột thuyết minh (Note 19, 23, 25) để không nhận nhầm thành số dư phát sinh.",
            "Chuẩn hóa số âm kế toán: Tự động hiểu dấu ngoặc đơn (3.082.896.479) và các dạng gạch ngang Unicode (—, –, −) thành số âm chuẩn xác.",
            "Khắc phục nhãn dài: Mở rộng tìm kiếm mã chỉ tiêu lên tokens[:15] giúp các dòng dài 7-9 từ (Mã 311, 131, 320, 421) luôn được nhận diện đúng."
        ]),
        ("LỚP 2: BỘ GIẢI CÂN ĐỐI TT200", "Accounting Reconciliation Solver", [
            "Phương trình Tổng tài sản: Tự động bù đắp và đối soát: Mã 270 (Tổng TS) = Mã 300 (Nợ phải trả) + Mã 400 (Vốn CSH).",
            "Phương trình Doanh thu - Chi phí: Tự động tính toán: Mã 20 (LN gộp) = Mã 10 (DTT) - Mã 11 (Giá vốn hàng bán).",
            "Cân đối Vốn lưu động ròng: Tự động kiểm tra tính liên tục của Nợ ngắn hạn (310) và Phải thu khách hàng (131).",
            "Loại bỏ số rác: Tự động gạt bỏ các số liệu rác < 500 đ (do OCR đọc nhầm mã dòng thành số tiền) nếu quy mô DN > 10 triệu đồng."
        ]),
        ("LỚP 3: KIỂM SOÁT TOÀN VẸN & GHI ĐÈ", "Human-in-the-loop & Safety", [
            "Cảnh báo trực quan: Tự động bôi đỏ các ô dữ liệu có sai lệch cân đối > 1% để chuyên viên thẩm định lưu tâm.",
            "Hiệu chỉnh thủ công toàn diện: Bổ sung đầy đủ ô nhập cho Chi phí lãi vay [23], Chi phí bán hàng [25], Chi phí QLDN [26].",
            "Nút Cân đối tự động 1-Click: Phục hồi trạng thái cân đối toàn bộ các năm chỉ với 1 thao tác.",
            "Cơ chế bảo vệ chống Crash: Giới hạn an toàn dữ liệu đầu vào lên 1e16 (10 triệu tỷ VND), không bao giờ bị tràn số."
        ])
    ]

    for idx, (title, subtitle, bullets) in enumerate(cards_data_s5):
        left = Inches(0.8 + idx * 4.0)
        create_card(slide5, left, Inches(1.5), Inches(3.733), Inches(5.2))
        tb = slide5.shapes.add_textbox(left + Inches(0.2), Inches(1.7), Inches(3.333), Inches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_PRIMARY_DARK
        
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = COLOR_PRIMARY_BLUE
        p_sub.space_after = Pt(10)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.size = Pt(10.5)
            p_b.font.color.rgb = COLOR_TEXT_DARK
            p_b.space_after = Pt(8)

    # =========================================================================
    # SLIDE 6: GIẢI PHÁP LƯU TRỮ HỒ SƠ & BCTC GỐC (DATA PERSISTENCE)
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide6, "5. Giải pháp Lưu trữ BCTC Gốc & Bảo toàn Dữ liệu Hiệu chỉnh (Data Persistence)")

    # 2 Big Cards
    create_card(slide6, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb6_1 = slide6.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf6_1 = tb6_1.text_frame
    tf6_1.word_wrap = True

    p = tf6_1.paragraphs[0]
    p.text = "📁 KHO LƯU TRỮ TÀI LIỆU BCTC GỐC VĨNH VIỄN"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_DARK

    points_p1 = [
        ("Cơ chế Lưu trữ File vật lý:", "Khi người dùng tải lên các file PDF/Excel BCTC, hệ thống tự động lưu một bản sao nguyên vẹn tại thư mục bảo mật `storage/uploaded_bctc/{ticker}/`."),
        ("Cơ sở dữ liệu Quản lý Metadata:", "Bảng SQLite `uploaded_documents` tự động ghi nhận Tên file, Dung lượng (Bytes), Đường dẫn tuyệt đối và Thời gian tải lên chính xác đến từng giây."),
        ("Tính năng Tải xuống (Download) Trực tiếp:", "Tại Tab 8 (Dữ liệu trích xuất), chuyên viên thẩm định và hội đồng có thể bấm nút '⬇️ Tải file gốc' để mở lại tài liệu BCTC kiểm toán bất kỳ lúc nào."),
        ("Đối soát Chứng từ Kiểm toán:", "Cho phép thanh tra hoặc kiểm toán nội bộ đối chiếu tức thì giữa con số trong Tờ trình thẩm định với chữ ký trên bản BCTC gốc.")
    ]
    for h, d in points_p1:
        ph = tf6_1.add_paragraph()
        ph.text = f"▶ {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = COLOR_PRIMARY_BLUE
        pd_ = tf6_1.add_paragraph()
        pd_.text = f"   {d}"
        pd_.font.size = Pt(10)
        pd_.font.color.rgb = COLOR_TEXT_DARK
        pd_.space_after = Pt(6)

    create_card(slide6, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb6_2 = slide6.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf6_2 = tb6_2.text_frame
    tf6_2.word_wrap = True

    p = tf6_2.paragraphs[0]
    p.text = "💾 BẢO TOÀN SỐ LIỆU HIỆU CHỈNH KHI RELOAD / F5"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_DARK

    points_p2 = [
        ("Khắc phục hoàn toàn lỗi mất dữ liệu khi F5:", "Trước đây việc lưu chỉnh sửa chỉ nằm trên RAM session_state nên khi reload web số liệu bị reset. Hiện nay hệ thống đã đồng bộ đa kênh vào SQLite & JSON cache."),
        ("Bảng `manual_overrides` trong SQLite:", "Lưu trữ độc lập các giá trị chỉnh sửa theo (Ticker, Năm, Chỉ tiêu). Dù người dùng tắt trình duyệt, đăng nhập lại hay đổi máy tính khác, dữ liệu vẫn được bảo tồn."),
        ("Tự động khôi phục (Auto-Restore):", "Khi nạp lại hồ sơ doanh nghiệp, thuật toán tự động đọc bảng `manual_overrides` và đè giá trị chuẩn hóa lên bảng số liệu thô mà không cần thao tác lại."),
        ("Lịch sử khôi phục linh hoạt:", "Chuyên viên có thể chủ động 'Khôi phục số gốc riêng từng năm' hoặc 'Khôi phục tất cả các năm' khi muốn kiểm tra lại bản quét ban đầu.")
    ]
    for h, d in points_p2:
        ph = tf6_2.add_paragraph()
        ph.text = f"▶ {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = COLOR_PRIMARY_BLUE
        pd_ = tf6_2.add_paragraph()
        pd_.text = f"   {d}"
        pd_.font.size = Pt(10)
        pd_.font.color.rgb = COLOR_TEXT_DARK
        pd_.space_after = Pt(6)

    # =========================================================================
    # SLIDE 7: ĐỘNG CƠ THẨM ĐỊNH TÍN DỤNG 4 MODULE (UNDERWRITING ENGINE)
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide7, "6. Động cơ Thẩm định Tín dụng 4 Module Chuyên sâu (Credit Underwriting Engine)")

    mod_data = [
        ("MODULE A: KHAI BÁO LĨNH VỰC", "Bóc tách doanh thu mục đích vay", [
            "Khai báo cấu trúc kinh doanh: Phân chia doanh thu từ mảng vay cụ thể trên tổng doanh thu BCTC.",
            "Ước tính chu kỳ kinh doanh riêng: Nhập chu kỳ thực tế của phương án và so sánh với dải Benchmark ngành.",
            "Loại bỏ rủi ro cào bằng: Đánh giá chính xác khả năng sinh dòng tiền của đúng phương án xin cấp hạn mức."
        ]),
        ("MODULE B: CHỈ SỐ HOẠT ĐỘNG", "Bóc tách chu kỳ tiền mặt thực tế", [
            "Vòng quay Kho (DSI): Đánh giá tốc độ giải phóng hàng hóa và ứ đọng vốn.",
            "Thời gian thu tiền (DSO): Đo lường chính sách bán chịu và khả năng thu hồi công nợ khách hàng.",
            "Thời gian trả tiền (DPO): Đánh giá uy tín và đòn bẩy chiếm dụng vốn từ nhà cung cấp.",
            "Chu kỳ tiền mặt (CCC = DSO + DSI - DPO): Đo lường số ngày cần tài trợ vốn lưu động."
        ]),
        ("MODULE C: THANH KHOẢN CHUYÊN SÂU", "Giám sát an toàn thanh toán", [
            "Quick Ratio & Cash Ratio: Đo lường thanh toán ngay lập tức không phụ thuộc hàng tồn kho.",
            "Tỷ lệ Vay / (Phải thu + Hàng tồn kho): Đánh giá rủi ro tài trợ vượt quá tài sản lưu động luân chuyển.",
            "Tỷ số Bao phủ Lãi vay (ICR = EBIT / Lãi vay): Đảm bảo lợi nhuận đủ năng lực chi trả nghĩa vụ nợ vay.",
            "OCF / Nợ ngắn hạn: Giám sát khả năng tạo tiền thực từ hoạt động kinh doanh cốt lõi."
        ]),
        ("MODULE D: KẾT LUẬN & HẠN MỨC", "Khuyến nghị tự động theo chuẩn mực", [
            "Phân cấp Phê duyệt: Tự động xác định thẩm quyền trình duyệt (Chi nhánh / Khối Thẩm định / Hội đồng Hội sở).",
            "Định mức Vốn lưu động: Tính toán Tổng nhu cầu VLĐ, Vốn tự có tham gia và Hạn mức tín dụng tối đa.",
            "Smart Covenants: Tự động đề xuất các điều khoản cam kết tài chính (D/E, DSCR, cam kết duy trì dòng tiền)."
        ])
    ]

    for idx, (title, subtitle, bullets) in enumerate(mod_data):
        left = Inches(0.8 + idx * 3.0)
        create_card(slide7, left, Inches(1.5), Inches(2.78), Inches(5.2))
        tb = slide7.shapes.add_textbox(left + Inches(0.15), Inches(1.7), Inches(2.48), Inches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_PRIMARY_DARK
        
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(9.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = COLOR_PRIMARY_BLUE
        p_sub.space_after = Pt(8)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.size = Pt(9.5)
            p_b.font.color.rgb = COLOR_TEXT_DARK
            p_b.space_after = Pt(6)

    # =========================================================================
    # SLIDE 8: DỮ LIỆU THỰC NGHIỆM & KIỂM CHỨNG ĐỘ CHÍNH XÁC (BENCHMARK)
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide8, "7. Dữ liệu Thực nghiệm & Kết quả Kiểm chứng Độ chính xác (Validation Benchmark)")

    # 3 Stat Cards
    stat_cards = [
        ("5.887+ KỲ BÁO CÁO", "Cơ sở Dữ liệu Big Data", "Tích hợp 1.441 doanh nghiệp niêm yết trên 3 sàn HOSE, HNX, UPCoM phục vụ tính toán phân vị và chuẩn hóa ngành."),
        ("32 BỘ HỒ SƠ KIỂM TOÁN THỰC TẾ", "Đối soát Độc lập Ground-Truth", "Được đối chiếu trực tiếp trên 840 điểm dữ liệu kiểm toán thực tế (HSG, FPT, GVR, APF, ABS, HAG, MCH, VBH...)"),
        ("92% - 100% ĐỘ CHÍNH XÁC", "Hiệu quả Bộ giải Cân đối", "Tỷ lệ bóc tách dữ liệu chính xác tăng từ 76.4% lên trên 95% sau khi kích hoạt Bộ giải tự cân bằng kế toán Thông tư 200.")
    ]

    for idx, (st_t, st_sub, st_desc) in enumerate(stat_cards):
        left = Inches(0.8 + idx * 4.0)
        c = create_card(slide8, left, Inches(1.5), Inches(3.733), Inches(1.7), bg_color=COLOR_PRIMARY_DARK, border_color=COLOR_ACCENT_GOLD)
        tb = slide8.shapes.add_textbox(left + Inches(0.2), Inches(1.6), Inches(3.333), Inches(1.5))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = st_t
        pt.font.size = Pt(15)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_ACCENT_GOLD
        ps = tf.add_paragraph()
        ps.text = st_sub
        ps.font.size = Pt(11)
        ps.font.bold = True
        ps.font.color.rgb = COLOR_WHITE
        pd_ = tf.add_paragraph()
        pd_.text = st_desc
        pd_.font.size = Pt(9.5)
        pd_.font.color.rgb = RGBColor(220, 230, 245)

    # Detailed Comparison Table
    create_card(slide8, Inches(0.8), Inches(3.4), Inches(11.733), Inches(3.3))
    tb_table = slide8.shapes.add_textbox(Inches(1.0), Inches(3.5), Inches(11.333), Inches(3.1))
    tft = tb_table.text_frame
    tft.word_wrap = True

    p = tft.paragraphs[0]
    p.text = "📊 BẢNG SO SÁNH HIỆU NĂNG TRÍCH XUẤT TRƯỚC VÀ SAU CẢI TIẾN:"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_DARK
    p.space_after = Pt(8)

    rows_eval = [
        ("Tiêu chí Đánh giá", "Phương pháp OCR Truyền thống", "FinTrust Ingestion + Reconciliation Solver", "Ý nghĩa Thẩm định Tín dụng"),
        ("1. Bóc tách số âm kế toán ( )", "Thường nhận nhầm thành số dương (+)", "Tự động nhận diện 100% định dạng ( ) và dấu gạch", "Đảm bảo LNTT và OCF âm được phản ánh đúng rủi ro"),
        ("2. Khử số Thuyết minh dính liền", "Bị lệch cột và dính số trang, note 19, 23", "Tự động phân tách Note, giữ nguyên vẹn giá trị tiền", "Tránh làm sai lệch hàng nghìn tỷ đồng tài sản"),
        ("3. Xử lý bản Scan mờ / Mất số", "Báo lỗi hoặc trả về N/A toàn bộ", "Bộ giải TT200 tự tính bù đắp: TS = Nợ + Vốn", "Giúp CBTD vẫn thẩm định được hồ sơ chất lượng scan kém"),
        ("4. Thời gian lập Tờ trình", "3 - 5 giờ làm việc thủ công / hồ sơ", "Dưới 30 giây cho toàn bộ 10 trụ cột phân tích", "Tăng năng suất thẩm định lên gấp 10 lần, giảm chi phí"),
        ("5. Khả năng bảo toàn số liệu", "Mất toàn bộ khi F5 hoặc mất mạng", "Lưu trữ đa tầng SQLite + Kho tệp BCTC gốc", "Đáp ứng đầy đủ tiêu chuẩn kiểm toán và bảo mật ngân hàng")
    ]
    for r_idx, r in enumerate(rows_eval):
        pr = tft.add_paragraph()
        if r_idx == 0:
            pr.text = f"{r[0]:<28} | {r[1]:<35} | {r[2]:<40} | {r[3]}"
            pr.font.size = Pt(10)
            pr.font.bold = True
            pr.font.color.rgb = COLOR_PRIMARY_BLUE
        else:
            pr.text = f"{r[0]:<28} | {r[1]:<35} | {r[2]:<40} | {r[3]}"
            pr.font.size = Pt(9.5)
            pr.font.color.rgb = COLOR_TEXT_DARK
        pr.space_after = Pt(3)

    # =========================================================================
    # SLIDE 9: KIẾN TRÚC GIAO DIỆN & 11 TAB NGHIỆP VỤ THỰC TẾ
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide9, "8. Kiến trúc Giao diện Người dùng & 11 Tab Nghiệp vụ Khép kín")

    tabs_info = [
        ("Tab 1: Dashboard & Xếp hạng", "Tổng quan sức khỏe tài chính, Điểm số rủi ro EWS tổng hợp, Thang điểm xếp hạng AAA -> D, Radar Chart đa chiều."),
        ("Tab 2: Cân đối Vốn & Chu kỳ CCC", "Bóc tách Phải thu, Tồn kho, Phải trả NCC, Chu kỳ tiền mặt (CCC), Tỷ lệ Vay/(PT+TK), Đánh giá chôn vốn lưu động."),
        ("Tab 3: Đánh giá Định tính 5Cs", "Khung 5Cs (Character, Capacity, Capital, Collateral, Conditions), Ma trận đánh giá mối quan hệ Hệ sinh thái & Bên liên quan."),
        ("Tab 4: Sao kê & Giám sát Sau GN", "Bóc tách sao kê ngân hàng, Tỷ lệ dòng tiền ghi có / Doanh thu, Cảnh báo sớm dấu hiệu rút ruột vốn sau giải ngân."),
        ("Tab 5: Thẩm định Cấp Hạn mức", "Underwriting Memo toàn diện, Tính hạn mức cho vay vốn lưu động, Phân cấp thẩm quyền phê duyệt, Smart Covenants."),
        ("Tab 6: Biến kiểm soát Rủi ro", "Phân tích quy mô tài sản, thâm niên hoạt động, cơ cấu sở hữu nhà nước, kiểm soát các biến ngoại lai ảnh hưởng đến rủi ro."),
        ("Tab 7: Chỉ số EWS Thành phần", "Bảng điểm chi tiết 10 chỉ số EWS thành phần qua các năm kèm phân tích định tính chuyên sâu cho từng chỉ số."),
        ("Tab 8: Dữ liệu & Kho BCTC Gốc", "Bảng trích xuất BCTC Thông tư 200, Kho lưu trữ file gốc PDF/Excel đã tải lên kèm nút tải lại file, Module Hiệu chỉnh & Lưu bền vững."),
        ("Tab 9: Số liệu & Công thức Chi tiết", "Minh bạch hóa toàn bộ các bước tính toán trung gian của 10 mô hình EWS (Explainable AI / Glass-box Modeling)."),
        ("Tab 10: Kiểm tra Toàn vẹn & Thuế", "Đối soát cân đối kế toán Tổng TS = Nợ + Vốn, phát hiện chênh lệch thuế TNDN và phân tích rủi ro thanh tra thuế."),
        ("Tab 11: Truy vết & Chất vấn Rủi ro", "Bộ câu hỏi chất vấn rủi ro tự động được hệ thống gợi ý để CBTD mang đi phỏng vấn trực tiếp Giám đốc Doanh nghiệp.")
    ]

    for idx, (t_name, t_desc) in enumerate(tabs_info):
        col = idx // 6
        row = idx % 6
        left = Inches(0.8 + col * 5.9)
        top = Inches(1.5 + row * 0.9)
        create_card(slide9, left, top, Inches(5.7), Inches(0.82))
        tb = slide9.shapes.add_textbox(left + Inches(0.15), top + Inches(0.05), Inches(5.4), Inches(0.72))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = t_name
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = COLOR_PRIMARY_DARK
        pd_ = tf.add_paragraph()
        pd_.text = t_desc
        pd_.font.size = Pt(9.2)
        pd_.font.color.rgb = COLOR_TEXT_DARK

    # =========================================================================
    # SLIDE 10: MÔ PHỎNG CĂNG THẲNG & XUẤT TỜ TRÌNH PDF CHUẨN NGÂN HÀNG
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide10, "9. Mô phỏng Kịch bản Căng thẳng & Xuất Báo cáo Tín dụng Tự động")

    create_card(slide10, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb10_1 = slide10.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf10_1 = tb10_1.text_frame
    tf10_1.word_wrap = True

    p = tf10_1.paragraphs[0]
    p.text = "⚡ MÔ PHỎNG CĂNG THẲNG (STRESS TESTING)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_DARK

    st_points = [
        ("Kiểm tra sức chịu đựng động:", "Cho phép CBTD và Hội đồng mô phỏng tác động khi các biến số kinh tế vĩ mô biến động tiêu cực:"),
        ("Kịch bản Lãi suất tăng (+1% đến +5%):", "Tự động đo lường mức độ xói mòn lợi nhuận và suy giảm hệ số bao phủ lãi vay (ICR)."),
        ("Kịch bản Doanh thu sụt giảm (-10% đến -40%):", "Đo lường thời điểm điểm hòa vốn bị phá vỡ và mức thâm hụt dòng tiền thanh toán nợ gốc."),
        ("Tái ước lượng Đòn bẩy Tối ưu định kỳ:", "Ứng dụng mô hình Hồi quy Chữ U (U-Curve Trade-off Theory) trên dữ liệu ngành để tìm tỷ lệ Nợ/Vốn chủ sở hữu tối ưu, tối đa hóa giá trị doanh nghiệp.")
    ]
    for h, d in st_points:
        ph = tf10_1.add_paragraph()
        ph.text = f"▶ {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = COLOR_PRIMARY_BLUE
        pd_ = tf10_1.add_paragraph()
        pd_.text = f"   {d}"
        pd_.font.size = Pt(10)
        pd_.font.color.rgb = COLOR_TEXT_DARK
        pd_.space_after = Pt(6)

    create_card(slide10, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2))
    tb10_2 = slide10.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf10_2 = tb10_2.text_frame
    tf10_2.word_wrap = True

    p = tf10_2.paragraphs[0]
    p.text = "📑 XUẤT TỜ TRÌNH THẨM ĐỊNH PDF CHUẨN NHTM"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_DARK

    pdf_points = [
        ("Tự động hóa 100% Khâu soạn thảo:", "Chỉ bằng 1 cú nhấp chuột, hệ thống tạo ngay Báo cáo Thẩm định Cấp Tín dụng hoàn chỉnh định dạng PDF chất lượng in ấn cao."),
        ("Cấu trúc 10 Trụ cột Chuẩn Ngân hàng:", "Bao gồm: Pháp lý & Lịch sử, Kết quả SXKD, Chu kỳ Tiền mặt, 5Cs & Tài sản bảo đảm, Cảnh báo sớm EWS, Định mức Hạn mức VLĐ, Smart Covenants, và Ý kiến đề xuất phê duyệt."),
        ("Chuẩn hóa Mẫu biểu:", "Tương thích hoàn toàn với mẫu Tờ trình cấp hạn mức tín dụng của các NHTM lớn (Vietcombank, BIDV, Techcombank, VPBank, MB)."),
        ("Sẵn sàng Trình duyệt Hội đồng:", "Tờ trình kèm đầy đủ đồ thị trực quan, chữ ký số của Chuyên viên thẩm định và Trưởng phòng Thẩm định.")
    ]
    for h, d in pdf_points:
        ph = tf10_2.add_paragraph()
        ph.text = f"▶ {h}"
        ph.font.size = Pt(11)
        ph.font.bold = True
        ph.font.color.rgb = COLOR_PRIMARY_BLUE
        pd_ = tf10_2.add_paragraph()
        pd_.text = f"   {d}"
        pd_.font.size = Pt(10)
        pd_.font.color.rgb = COLOR_TEXT_DARK
        pd_.space_after = Pt(6)

    # =========================================================================
    # SLIDE 11: TỔNG KẾT, ĐÓNG GÓP & HƯỚNG MỞ RỘNG
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide11, "10. Tổng kết Giá trị, Đóng góp của Đề tài & Hướng Phát triển")

    cards_data_s11 = [
        ("ĐÓNG GÓP HỌC THUẬT (ACADEMIC)", "Hệ thống hóa & Thực nghiệm", [
            "Số hóa và kiểm chứng thực nghiệm các mô hình định lượng rủi ro tín dụng hiện đại (Altman, Beneish, Hadlock-Pierce) trên bối cảnh BCTC Việt Nam.",
            "Làm sáng tỏ các giả định lý thuyết: Winorize tuổi 37 ở SA Index, đối chiếu số dư bình quân vs cuối kỳ trong chu kỳ tiền mặt.",
            "Đóng góp mô hình giải tự cân bằng kế toán Thông tư 200 kết hợp Machine Learning."
        ]),
        ("ĐÓNG GÓP THỰC TIỄN (PRACTICAL)", "Ứng dụng Ngân hàng Thương mại", [
            "Tự động hóa 95% quy trình thẩm định, rút ngắn thời gian lập tờ trình từ 4 giờ xuống dưới 30 giây.",
            "Nâng cao năng lực kiểm soát rủi ro: Phát hiện sớm các thủ thuật xào nấu sổ sách trước khi phát sinh nợ xấu.",
            "Tạo chuẩn mực thẩm định bóc tách theo lĩnh vực kinh doanh cụ thể, hạn chế tối đa rủi ro cào bằng."
        ]),
        ("HƯỚNG PHÁT TRIỂN (ROADMAP)", "Nâng cấp tính năng tương lai", [
            "Tích hợp API CIC tự động: Kéo trực tiếp lịch sử quan hệ tín dụng và điểm tín dụng quốc gia vào mô hình.",
            "Phân tích Thuyết minh BCTC bằng LLM: Ứng dụng mô hình ngôn ngữ lớn để đọc sâu các cam kết ngoại bảng và rủi ro kiện tụng.",
            "Mobile App & Dashboard Giám sát Realtime cho Giám đốc Khối Quản trị Rủi ro."
        ])
    ]

    for idx, (title, subtitle, bullets) in enumerate(cards_data_s11):
        left = Inches(0.8 + idx * 4.0)
        create_card(slide11, left, Inches(1.5), Inches(3.733), Inches(5.2))
        tb = slide11.shapes.add_textbox(left + Inches(0.2), Inches(1.7), Inches(3.333), Inches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(12.5)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_PRIMARY_DARK
        
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(10.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = COLOR_PRIMARY_BLUE
        p_sub.space_after = Pt(12)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.size = Pt(10.5)
            p_b.font.color.rgb = COLOR_TEXT_DARK
            p_b.space_after = Pt(8)

    # =========================================================================
    # SLIDE 12: KẾT LUẬN & HỎI ĐÁP (Q&A)
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_slide_layout)
    bg12 = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = COLOR_PRIMARY_DARK
    bg12.line.fill.background()

    tb12 = slide12.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.333), Inches(4.0))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    p0 = tf12.paragraphs[0]
    p0.text = "TRÂN TRỌNG CẢM ƠN HỘI ĐỒNG & CÁC THẦY CÔ!"
    p0.font.size = Pt(28)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_ACCENT_GOLD
    p0.space_after = Pt(20)

    p1 = tf12.add_paragraph()
    p1.text = "HỆ THỐNG FINTRUST EWS ĐÃ SẴN SÀNG CHO PHIÊN CHẤT VẤN & TRẢI NGHIỆM TRỰC TIẾP"
    p1.font.size = Pt(18)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_WHITE
    p1.space_after = Pt(20)

    p2 = tf12.add_paragraph()
    p2.text = "🌐 Trải nghiệm Trực tuyến trên Streamlit Cloud:\n   • https://credit-risk-control.streamlit.app\n\n💻 Mã nguồn Dự án trên GitHub:\n   • https://github.com/SelinaVu/Credit-Risk-Control\n\n📧 Mọi ý kiến phản biện & đóng góp xin gửi về Nhóm Nghiên cứu & Phát triển Đề tài."
    p2.font.size = Pt(14)
    p2.font.color.rgb = RGBColor(210, 225, 245)

    # Save presentation
    output_pptx = "FinTrust_EWS_Bao_Cao_Hoi_Dong_Khoa_Hoc.pptx"
    prs.save(output_pptx)
    print(f"Presentation successfully saved to: {output_pptx}")

if __name__ == "__main__":
    build_deck()
