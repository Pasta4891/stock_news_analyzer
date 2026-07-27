"""
用假資料快速預覽 Email 樣板長什麼樣子，不需要設定任何 API Key。

執行方式（在專案根目錄下）：
    python preview_email.py

執行後會產生 preview_output.html，用瀏覽器打開就能看到跟寄出去
一模一樣的排版（大部分Email信箱的渲染引擎跟瀏覽器接近，但不會100%一致，
正式上線前還是建議寄一封測試信到自己信箱確認）。
"""
from src.services.email_template import build_stock_section_html, build_report_email

fake_quote = {
    "symbol": "NVDA",
    "price": "204.12",
    "change": "7.19",
    "change_percent": "3.65%",
    "volume": "147,000,000",
    "latest_trading_day": "2026-07-08",
}

fake_daily_range = {
    "date": "2026-07-08",
    "open": "195.18",
    "high": "205.16",
    "low": "195.06",
    "close": "204.12",
}

fake_quote_2 = {
    "symbol": "AAPL",
    "price": "212.40",
    "change": "-1.85",
    "change_percent": "-0.86%",
    "volume": "52,300,000",
    "latest_trading_day": "2026-07-08",
}

fake_daily_range_2 = {
    "date": "2026-07-08",
    "open": "214.00",
    "high": "215.10",
    "low": "211.90",
    "close": "212.40",
}

fake_analysis = {
    "positive": [
        "傳美國可能放寬對中國出口NVIDIA先進AI晶片的限制",
        "輝達持續擴展AI生態系統，攜手多家企業打造大規模AI資料中心",
        "摩根士丹利重申「加碼」評等，目標價上看$288",
    ],
    "negative": [
        "主要競爭對手AMD推出新解決方案，性價比表現亮眼",
        "地緣政治審批不確定性，中國官方監管審批速度存在變數",
    ],
    "neutral": [
        "分析師持續關注下一季財報表現",
    ],
    "summary": "NVIDIA展現強勁買盤動能，機構評等維持樂觀，但地緣政治與競爭對手動態仍是需要持續觀察的風險因子。",
}

fake_analysis_2 = {
    "positive": [
        "新一代晶片供應鏈傳出擴產消息",
    ],
    "negative": [
        "季度銷售預估遭部分分析師下修",
        "供應鏈成本上升壓力持續",
    ],
    "neutral": [
        "市場等待下季財報進一步指引",
    ],
    "summary": "蘋果股價短線承壓，市場情緒偏保守，需觀察下一季財報是否能扭轉預期。",
}

overview_rows = [
    {"symbol": "NVDA", "price": "204.12", "change_percent": "+3.65%", "is_up": True},
    {"symbol": "AAPL", "price": "212.40", "change_percent": "-0.86%", "is_up": False},
]

sections_html = [
    build_stock_section_html(
        symbol="NVDA", quote=fake_quote, news_count=50,
        analysis=fake_analysis, daily_range=fake_daily_range,
    ),
    build_stock_section_html(
        symbol="AAPL", quote=fake_quote_2, news_count=37,
        analysis=fake_analysis_2, daily_range=fake_daily_range_2,
    ),
]

full_html = build_report_email(
    report_datetime_str="2026-07-08 09:00",
    stock_sections_html=sections_html,
    overview_rows=overview_rows,
)

with open("preview_output.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("已產生 preview_output.html，請用瀏覽器打開查看")

