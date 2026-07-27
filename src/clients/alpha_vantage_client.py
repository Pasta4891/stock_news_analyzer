"""
負責跟 Alpha Vantage API 溝通，對應圖中的兩種 HTTP Request 節點：

1. get_global_quote(symbol)   -> 對應圖中的 "XXX (GLOBAL_QUOTE)" 節點
2. get_top_news(symbol, limit) -> 對應圖中的 "XXX (新聞)" 節點，最多取 50 則
3. get_daily_range(symbol)     -> 額外補上當日最低/最高價，用於Email的股價區間條

※ 注意：Alpha Vantage 免費版有呼叫次數限制（目前為每天25次），
   每支股票會用掉 3 次額度（報價+新聞+日線），追蹤股票數不要設太多。
"""
import requests
from src.config import ALPHA_VANTAGE_API_KEY

BASE_URL = "https://www.alphavantage.co/query"


def get_global_quote(symbol: str) -> dict:
    """取得單一股票的即時報價資訊"""
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    quote = data.get("Global Quote", {})
    if not quote:
        # 常見原因：一天呼叫次數用完了 (免費版有額度限制)
        return {"symbol": symbol, "error": "查無報價資料（可能是API額度已用完）"}

    return {
        "symbol": symbol,
        "price": quote.get("05. price"),
        "change": quote.get("09. change"),
        "change_percent": quote.get("10. change percent"),
        "volume": quote.get("06. volume"),
        "latest_trading_day": quote.get("07. latest trading day"),
    }


def get_daily_range(symbol: str) -> dict:
    """
    取得當日（最近一個交易日）的最低價/最高價/開盤價，
    用來畫Email裡的股價區間條。GLOBAL_QUOTE本身不會給這個資訊，
    所以要另外呼叫 TIME_SERIES_DAILY。
    """
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    daily_series = data.get("Time Series (Daily)", {})
    if not daily_series:
        return {}

    # 字典的key是日期，取最新的一天（第一筆）
    latest_date = sorted(daily_series.keys(), reverse=True)[0]
    latest_bar = daily_series[latest_date]

    return {
        "date": latest_date,
        "open": latest_bar.get("1. open"),
        "high": latest_bar.get("2. high"),
        "low": latest_bar.get("3. low"),
        "close": latest_bar.get("4. close"),
    }


def get_top_news(symbol: str, limit: int = 50) -> list:
    """取得該股票相關新聞（Alpha Vantage 的 NEWS_SENTIMENT），預設最多 50 則"""
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "limit": limit,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    feed = data.get("feed", [])
    news_list = []
    for item in feed[:limit]:
        news_list.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "time_published": item.get("time_published"),
            "summary": item.get("summary"),
            "source": item.get("source"),
            "overall_sentiment_label": item.get("overall_sentiment_label"),
        })
    return news_list

    """取得該股票相關新聞（Alpha Vantage 的 NEWS_SENTIMENT），預設最多 50 則"""
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "limit": limit,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    feed = data.get("feed", [])
    news_list = []
    for item in feed[:limit]:
        news_list.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "time_published": item.get("time_published"),
            "summary": item.get("summary"),
            "source": item.get("source"),
            "overall_sentiment_label": item.get("overall_sentiment_label"),
        })
    return news_list
