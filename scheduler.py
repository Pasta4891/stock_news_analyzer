"""
對應圖中的 "When clicking 'Execute workflow'" 觸發節點，
但改成「時間排程」自動觸發，取代手動點擊。

使用 schedule 套件，每天固定時間執行一次 main.run_report()。

執行方式：
    python scheduler.py

這個程式會持續在背景執行（while迴圈不會停），所以要讓執行環境
一直保持開啟，或是部署到雲端主機/伺服器（例如 Render、Railway、
自己的VPS，或用 GitHub Actions 排程觸發）讓它自動運作。
"""
import time
import schedule
from src.main import run_report

# 每天早上 08:00 執行一次（可依需求修改時間，例如美股開盤前）
schedule.every().day.at("08:00").do(run_report)

if __name__ == "__main__":
    print("排程已啟動，等待執行時間到...（按 Ctrl+C 停止）")
    # 程式啟動時先跑一次，方便馬上測試是否成功
    run_report()

    while True:
        schedule.run_pending()
        time.sleep(30)
