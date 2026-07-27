"""
對應圖中的 "Send a message" (Gmail) 節點：
負責把整理好的報告透過 Email 寄出。

使用標準函式庫 smtplib + Gmail SMTP。

※ 重要：Gmail 帳號請使用「應用程式專用密碼」，不要用登入密碼！
   設定教學：https://support.google.com/accounts/answer/185833
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_report_email(subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

    print(f"Email已寄出 -> {EMAIL_RECEIVER}")
