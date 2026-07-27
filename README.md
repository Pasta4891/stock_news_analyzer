# Stock News Analyzer

自動抓取股票即時報價、當日高低點與相關新聞（Alpha Vantage），
交給 LLM（Google Gemini）分類成「利多／利空／中立」，
套用深色卡片版型，定期用 Email 寄出報告。

## 專案架構

```
stock_news_analyzer/
├── src/
│   ├── config.py                       # 讀取環境變數（API金鑰、Email帳密、追蹤股票清單）
│   ├── clients/
│   │   └── alpha_vantage_client.py     # 呼叫 Alpha Vantage：報價 / 當日高低點 / 新聞(最多50則)
│   ├── services/
│   │   ├── llm_classifier.py           # 呼叫 Gemini，回傳結構化JSON分類結果
│   │   ├── email_template.py           # 深色卡片Email樣板（總覽表格+個股卡片）
│   │   └── email_sender.py             # 用 smtplib 寄送 Email
│   └── main.py                         # 主流程：整合以上步驟，執行一次完整報告
├── .github/workflows/
│   └── daily_report.yml     # GitHub Actions排程，雲端自動每天執行(不需自己開機)
├── scheduler.py              # 另一種排程方式：本機/伺服器用 schedule 套件常駐執行
├── preview_email.py          # 用假資料預覽Email長相，不需要任何API Key
├── requirements.txt
├── .env.example               # 環境變數範例（複製成 .env 使用）
└── .gitignore
```

`clients/` 放「跟外部API拿資料」的程式，`services/` 放「處理/加工資料」的程式，
`main.py` 負責把它們串接起來。

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
   > 部署到雲端主機／GitHub Actions時，改成在該平台的「環境變數/Secrets」
   > 設定頁面填入即可，不需要上傳 `.env` 檔案。

4. **（建議先做）預覽Email長相，不需要任何API Key：**
   ```bash
   python preview_email.py
   ```
   會產生 `preview_output.html`，用瀏覽器打開就能看到排版結果，
   確認滿意後再進行下一步實際串接API。

5. 手動測試跑一次完整流程（**注意**：因為 `main.py` 放在 `src/` 資料夾內，
   變成一個 package 的一部分，所以要用 `-m` 的方式執行，
   而且要在**專案根目錄**下執行這個指令，不要跑到 `src/` 資料夾裡面下指令）：
   ```bash
   python -m src.main
   ```
   如果一切正常，你會收到一封整理好的股市新聞報告 Email。

## 自動化排程（兩種方式擇一）

### 方式一：GitHub Actions（推薦，不用自己開機）

1. 把整個專案 push 到 GitHub repo（記得確認 `.env` 沒有被加進去，見下方檢查清單）
2. 到 repo 的 **Settings -> Secrets and variables -> Actions -> New repository secret**，
   依序新增 5 個 secret（名稱要完全一致）：
   `ALPHA_VANTAGE_API_KEY`、`GEMINI_API_KEY`、`EMAIL_SENDER`、`EMAIL_PASSWORD`、`EMAIL_RECEIVER`
3. 完成後，`.github/workflows/daily_report.yml` 會讓 GitHub 每天
   UTC 00:00（台灣時間 08:00）自動執行一次 `python -m src.main`，
   也可以到 repo 的 **Actions** 頁籤手動點 **Run workflow** 立即測試，
   不需要等到隔天。

### 方式二：本機／自己的伺服器用 `schedule` 套件

```bash
python scheduler.py
```

預設是每天 **08:00** 執行一次，可以到 `scheduler.py` 裡修改時間。
這個程式需要「持續在背景執行」（迴圈不會自己結束），適合部署在一台
24小時開機的伺服器（例如 Render、Railway、自己的VPS），本機測試也可以，
但關機後就不會繼續執行了 —— 如果不想管理一台常駐主機，建議直接用方式一。

## 想追蹤的股票

預設追蹤 `NVDA`、`AAPL`、`TSM`（對應圖中的三支股票），
可以到 `src/config.py` 的 `STOCK_SYMBOLS` 修改。

> ⚠️ Alpha Vantage 免費版有呼叫次數限制（目前為每天25次），
> 每支股票會用掉3次額度（報價 + 當日高低點 + 新聞），
> 追蹤股票數不要設太多，或考慮升級付費方案。

## 放上 GitHub 前檢查清單

- [ ] 確認 `.env` **沒有**被加進 git（`git status` 檢查一下，或執行 `git ls-files | grep .env` 確認沒有結果）
- [ ] 確認程式碼裡沒有任何寫死的金鑰或密碼
- [ ] 確認 `preview_output.html`（測試產生的檔案）不需要的話沒有被加進 git
- [ ] README 裡的金鑰申請連結、設定步驟是否清楚
