"""
對應圖中的 "Message a model" 節點：
把新聞丟給 Google Gemini，請 LLM 針對每支股票的新聞做分類與摘要。

這裡請 LLM 回傳「結構化 JSON」而不是一整段文字，
這樣 Email 樣板才能把「正面消息」「負面消息」分別渲染成獨立的色塊卡片
（像截圖那種深色報告的排版）。

如果你想改用 OpenAI 或 Anthropic 的模型，只要把這個檔案裡
呼叫API的部分換掉就好，回傳格式維持一樣的 dict 結構，main.py 不用改。
"""
import json
import re
import requests
from src.config import GEMINI_API_KEY

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.5-flash-lite:generateContent"
)

# 找不到LLM結果，或發生錯誤時的預設空結構
EMPTY_ANALYSIS = {
    "positive": [],
    "negative": [],
    "neutral": [],
    "summary": "目前沒有足夠的新聞資料可供分析。",
}


def classify_news(symbol: str, news_list: list) -> dict:
    """
    把新聞清單交給 LLM 分析，回傳結構化的 dict：
    {
        "positive": ["重點1", "重點2", ...],   # 利多因素
        "negative": ["重點1", "重點2", ...],   # 利空/潛在風險
        "neutral":  ["重點1", ...],            # 中立消息
        "summary": "整體趨勢摘要文字"
    }
    """
    if not news_list:
        return dict(EMPTY_ANALYSIS, summary=f"目前沒有取得 {symbol} 的相關新聞。")

    # 把新聞整理成給LLM看的文字，最多取前20則避免prompt過長、浪費額度
    news_text = "\n\n".join(
        f"標題：{n['title']}\n來源：{n['source']}\n摘要：{n['summary']}"
        for n in news_list[:20]
    )

    prompt = (
        f"你是一位專業的股市分析助理。以下是關於股票 {symbol} 的新聞清單，"
        f"請分析後「只回傳一個JSON物件」，不要有任何其他文字或markdown符號，"
        f"格式必須完全符合：\n"
        '{\n'
        '  "positive": ["利多重點1", "利多重點2"],\n'
        '  "negative": ["利空/風險重點1", "利空/風險重點2"],\n'
        '  "neutral": ["中立消息重點1"],\n'
        '  "summary": "2-3句話總結整體趨勢與可能對股價的影響"\n'
        '}\n'
        f"所有內容請用繁體中文，每個重點條目盡量濃縮在一句話內。\n\n"
        f"新聞內容如下：\n{news_text}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    try:
        resp = requests.post(
            GEMINI_URL, params=params, headers=headers,
            data=json.dumps(payload), timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return _parse_llm_json(raw_text)
    except Exception as e:
        return dict(EMPTY_ANALYSIS, summary=f"LLM分類時發生錯誤：{e}")


def _parse_llm_json(raw_text: str) -> dict:
    """
    嘗試把LLM回傳的文字解析成dict。
    多加一層保護：就算LLM不小心加了```json``` 這種markdown包裝，也能正常解析，
    避免程式因為LLM偶爾「多嘴」而直接壞掉。
    """
    cleaned = re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
        return {
            "positive": data.get("positive", []),
            "negative": data.get("negative", []),
            "neutral": data.get("neutral", []),
            "summary": data.get("summary", ""),
        }
    except json.JSONDecodeError:
        # 解析失敗的話，至少把原始文字放進summary，不要整封信都空白
        return dict(EMPTY_ANALYSIS, summary=raw_text)

