"""
主程式，串起整條流程（對應圖中從左到右的所有節點）：

1. 針對 STOCK_SYMBOLS 每一支股票，抓取報價 + 當日高低點 + 新聞（最多50則）
2. 把新聞交給 LLM 分類、摘要（回傳結構化JSON：正面/負面/中立/摘要）
3. 套用深色卡片樣板（含總覽表格 + 股價區間條），整理成一封 HTML Email 並寄出
"""
from datetime import datetime
from src.config import STOCK_SYMBOLS, check_env_vars
from src.clients.alpha_vantage_client import get_global_quote, get_daily_range, get_top_news
from src.services.llm_classifier import classify_news
from src.services.email_sender import send_report_email
from src.services.email_template import build_stock_section_html, build_report_email


def collect_stock_data(symbol: str) -> dict:
    """抓取單一股票需要的所有原始資料：報價、當日高低點、新聞、LLM分析"""
    quote = get_global_quote(symbol)
    daily_range = get_daily_range(symbol)
    news = get_top_news(symbol, limit=50)
    analysis = classify_news(symbol, news)

    return {
        "symbol": symbol,
        "quote": quote,
        "daily_range": daily_range,
        "news_count": len(news),
        "analysis": analysis,
    }


def build_overview_row(stock_data: dict) -> dict:
    """把單一股票資料轉成總覽表格需要的格式"""
    quote = stock_data["quote"]
    if "error" in quote:
        return {"symbol": stock_data["symbol"], "price": "-", "change_percent": "N/A", "is_up": True}

    try:
        is_up = float(quote.get("change") or 0) >= 0
    except (TypeError, ValueError):
        is_up = True

    return {
        "symbol": stock_data["symbol"],
        "price": quote.get("price", "-"),
        "change_percent": quote.get("change_percent", "-"),
        "is_up": is_up,
    }


def run_report():
    """執行一次完整流程：抓資料 -> LLM分析 -> 套版 -> 寄信"""
    print(f"[{datetime.now()}] 開始產生股票報告...")
    check_env_vars()

    all_stock_data = [collect_stock_data(symbol) for symbol in STOCK_SYMBOLS]

    overview_rows = [build_overview_row(d) for d in all_stock_data]
    sections_html = [
        build_stock_section_html(
            symbol=d["symbol"],
            quote=d["quote"],
            news_count=d["news_count"],
            analysis=d["analysis"],
            daily_range=d["daily_range"],
        )
        for d in all_stock_data
    ]

    html_body = build_report_email(
        report_datetime_str=datetime.now().strftime("%Y-%m-%d %H:%M"),
        stock_sections_html=sections_html,
        overview_rows=overview_rows,
    )

    send_report_email(
        subject=f"每日股市新聞報告 {datetime.now().strftime('%Y-%m-%d')}",
        html_body=html_body,
    )
    print(f"[{datetime.now()}] 報告產生完成！")


if __name__ == "__main__":
    run_report()


