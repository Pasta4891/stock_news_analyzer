# Stock News Analyzer

自動抓取股票即時報價與相關新聞（Alpha Vantage），交給 LLM（Google Gemini）
分類與摘要，並定期用 Email 寄出報告。

## 專案架構

```
stock_news_analyzer/
├── config.py               # 讀取環境變數（API金鑰、Email帳密）
├── alpha_vantage_client.py # 呼叫 Alpha Vantage：報價 + 新聞(最多50則)
├── llm_classifier.py       # 呼叫 Gemini API 做新聞分類/摘要
├── email_sender.py         # 用 smtplib 寄送 Email
├── main.py                 # 主流程：整合以上步驟，執行一次完整報告
├── scheduler.py            # 用 schedule 套件，設定每天自動執行
├── requirements.txt
├── .env.example             # 環境變數範例（複製成 .env 使用）
└── .gitignore
```

## 安裝步驟

1. 安裝套件：
   ```bash
   pip install -r requirements.txt
   ```

2. 取得需要的金鑰：
   - Alpha Vantage API Key：https://www.alphavantage.co/support/#api-key （免費）
   - Google Gemini API Key：https://aistudio.google.com/app/apikey （免費）
   - Gmail 應用程式專用密碼：https://support.google.com/accounts/answer/185833

3. 設定環境變數（本機測試用）：
   ```bash
   cp .env.example .env
   # 打開 .env，把裡面的值換成你自己的金鑰
   ```

   > ⚠️ `.env` 已加入 `.gitignore`，不會被上傳到 GitHub。
   > 部署到雲端主機時，改成在該平台的「環境變數」設定頁面填入即可，
   > 不需要上傳 `.env` 檔案。

4. 手動測試跑一次：
   ```bash
   python main.py
   ```
   如果一切正常，你會收到一封整理好的股市新聞報告 Email。

## 自動化排程

用 Python 的 `schedule` 套件，每天固定時間自動執行：

```bash
python scheduler.py
```

預設是每天 **08:00** 執行一次，可以到 `scheduler.py` 裡修改時間。

這個程式需要「持續在背景執行」（迴圈不會自己結束），所以：
- 本機測試沒問題，但如果要長期自動運作，建議把它部署到一台
  24小時開機的伺服器/雲端主機（例如 Render、Railway、自己的VPS）。
- 或者，也可以改用 **GitHub Actions 排程（cron）** 的方式觸發
  `python main.py`（不需要一直開著機器，時間到 GitHub 會自動幫你跑），
  如果你想要這個版本，跟我說一聲，我可以幫你補上
  `.github/workflows/schedule.yml` 設定檔。

## 想追蹤的股票

預設追蹤 `NVDA`、`AAPL`、`TSM`（對應圖中的三支股票），
可以到 `config.py` 的 `STOCK_SYMBOLS` 修改。

## 放上 GitHub 前檢查清單

- [ ] 確認 `.env` **沒有**被加進 git（`git status` 檢查一下）
- [ ] 確認程式碼裡沒有任何寫死的金鑰或密碼
- [ ] README 裡的金鑰申請連結、設定步驟是否清楚
