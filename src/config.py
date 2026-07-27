"""
統一管理環境變數設定。

所有機密資訊 (API Key、Email密碼) 都不寫在程式碼中，
而是從系統環境變數讀取。

本機開發時，可以建立一個 .env 檔案 (參考 .env.example，記得不要上傳到 GitHub!)，
搭配 python-dotenv 套件，程式啟動時會自動把 .env 內容載入成環境變數。
"""
import os
from dotenv import load_dotenv

# 如果本機有 .env 檔案，會自動把裡面的變數載入到環境變數
load_dotenv()

# Alpha Vantage API Key：https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

# Google Gemini API Key：https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 寄件人 Email 帳號（建議用 Gmail「應用程式專用密碼」，不是登入密碼）
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# 收件人 Email
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# 想追蹤的股票代號（對應圖中的 NVDA / AAPL / TSM，可自行增減）
STOCK_SYMBOLS = ["NVDA", "AAPL", "TSM"]

_REQUIRED_VARS = {
    "ALPHA_VANTAGE_API_KEY": ALPHA_VANTAGE_API_KEY,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "EMAIL_SENDER": EMAIL_SENDER,
    "EMAIL_PASSWORD": EMAIL_PASSWORD,
    "EMAIL_RECEIVER": EMAIL_RECEIVER,
}


def check_env_vars():
    """
    檢查必要的環境變數是否都有設定。
    如果有缺少，直接在一開始就報錯提醒，而不是等程式跑到一半才失敗。
    """
    missing = [name for name, value in _REQUIRED_VARS.items() if not value]
    if missing:
        raise EnvironmentError(
            f"缺少以下環境變數，請先設定：{', '.join(missing)}\n"
            f"可以參考專案裡的 .env.example 檔案說明。"
        )
