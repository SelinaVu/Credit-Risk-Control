"""Design Tokens & Theme System cho FinTrust EWS
Định nghĩa hệ màu ngân hàng, phân cấp thị giác (visual hierarchy) và CSS tối ưu công thái học.
"""

FINTRUST_THEME = {
    # Bảng màu chủ đạo (Enterprise FinTech Palette)
    "primary": "#1e3a8a",       # Navy Blue - Đại diện cho sự tin cậy, chuẩn mực ngân hàng
    "primary_light": "#3b82f6", # Blue accent
    "secondary": "#0f172a",     # Dark Slate - Tiêu đề và phân cấp quan trọng
    "bg_subtle": "#f8fafc",     # Light Slate - Nền container, thẻ phụ
    "border": "#e2e8f0",        # Đường kẻ phân cách nhẹ nhàng
    
    # Hệ màu cảnh báo rủi ro (Traffic Light Risk Matrix)
    "risk_safe": "#10b981",     # Xanh lá - An toàn / Đạt chuẩn
    "risk_safe_bg": "#ecfdf5",
    "risk_warning": "#f59e0b",  # Vàng cam - Chú ý / Cận biên
    "risk_warning_bg": "#fffbeb",
    "risk_danger": "#ef4444",   # Đỏ - Cảnh báo nguy hiểm / Vi phạm ngưỡng
    "risk_danger_bg": "#fef2f2",
    "risk_neutral": "#64748b",  # Xám - Trung tính / Chưa xác định
}

CUSTOM_CSS = """
<style>
    /* 1. Global Font & Reset */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 2. Topbar Header Container */
    .fintrust-topbar {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 1.25rem 1.75rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .fintrust-topbar-title {
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .fintrust-topbar-subtitle {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    
    /* 3. Metric Scorecards */
    .metric-card-wrapper {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card-wrapper:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    .metric-card-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
        margin-bottom: 0.35rem;
    }
    .metric-card-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-card-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .badge-safe {
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    .badge-warning {
        background-color: #fffbeb;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    .badge-danger {
        background-color: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    
    /* 4. Company Banner */
    .company-banner {
        background: #f8fafc;
        border-left: 4px solid #2563eb;
        border-radius: 0 8px 8px 0;
        padding: 0.9rem 1.25rem;
        margin-bottom: 1.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* 5. Clean up Streamlit default margins */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1350px;
    }
</style>
"""
