"""
Email HTML 樣板，對應你截圖的深色卡片報告風格。

Email 排版的重要限制（跟一般網頁不一樣）：
1. 大部分樣式都用「行內 style」寫在標籤上，不能依賴外部 <style> 區塊，
   因為 Gmail 等信箱常常會把 <head> 裡的 CSS 濾掉。
2. 版面用 <table> 排，不用 flexbox/grid，相容性才夠好（老派但穩定）。
3. 避免整頁純黑背景：改成只在「卡片」區塊上底色，
   信件外框留給信箱自己的底色（白/黑都不會太醜）。
"""

# 顏色定義，統一管理方便微調
COLOR_BG_PAGE = "#0f0f0f"
COLOR_BG_CARD = "#1c1c1c"
COLOR_BORDER = "#333333"
COLOR_TEXT = "#e5e5e5"
COLOR_TEXT_MUTED = "#9a9a9a"
COLOR_POSITIVE = "#4ade80"
COLOR_NEGATIVE = "#f87171"
COLOR_NEUTRAL = "#9a9a9a"


def _metric_cell(label: str, value: str, value_color: str = COLOR_TEXT) -> str:
    """報價數據小卡片：今日收盤價 / 漲跌幅 / 漲跌額 / 成交量 這種格子"""
    return f"""
    <td align="center" style="padding:16px 8px; background:{COLOR_BG_CARD};
        border:1px solid {COLOR_BORDER}; border-radius:8px;">
      <div style="font-size:12px; color:{COLOR_TEXT_MUTED}; margin-bottom:6px;">{label}</div>
      <div style="font-size:22px; font-weight:bold; color:{value_color};">{value}</div>
    </td>
    """


def _price_range_bar(low, close, high) -> str:
    """今日股價區間的橫向進度條，顯示最低/收盤(位置)/最高"""
    try:
        low, close, high = float(low), float(close), float(high)
        pct = 50.0 if high == low else max(0, min(100, (close - low) / (high - low) * 100))
    except (TypeError, ValueError):
        return ""

    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
        style="margin-top:14px;">
      <tr>
        <td style="font-size:13px; color:{COLOR_TEXT_MUTED};">最低價：${low:.2f}</td>
        <td align="right" style="font-size:13px; color:{COLOR_TEXT_MUTED};">最高價：${high:.2f}</td>
      </tr>
    </table>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
        style="background:{COLOR_BORDER}; border-radius:6px; margin-top:6px;">
      <tr>
        <td style="position:relative; height:8px; line-height:8px; font-size:0;">
          <div style="width:{pct:.0f}%; height:8px; background:{COLOR_POSITIVE};
              border-radius:6px;">&nbsp;</div>
        </td>
      </tr>
    </table>
    <div style="text-align:center; font-size:13px; color:{COLOR_TEXT}; margin-top:6px;">
      收盤價落在今日區間的 <b>{pct:.0f}%</b> 位置
    </div>
    """


def _bullet_card(title: str, tag_label: str, tag_bg: str, items: list) -> str:
    """一個分類卡片：例如「利多因素」的綠色標籤 + 條列重點"""
    if not items:
        return ""

    bullets_html = "".join(
        f'<li style="margin-bottom:6px; color:{COLOR_TEXT}; font-size:14px; line-height:1.6;">{item}</li>'
        for item in items
    )

    return f"""
    <div style="background:{COLOR_BG_CARD}; border:1px solid {COLOR_BORDER};
        border-radius:8px; padding:14px 18px; margin-bottom:12px;">
      <span style="display:inline-block; background:{tag_bg}; color:#0f0f0f;
          font-size:12px; font-weight:bold; padding:2px 10px; border-radius:4px;
          margin-bottom:8px;">{tag_label}</span>
      <ul style="margin:8px 0 0 0; padding-left:18px;">
        {bullets_html}
      </ul>
    </div>
    """


def build_stock_section_html(symbol: str, quote: dict, news_count: int, analysis: dict,
                              daily_range: dict = None) -> str:
    """組合單一股票的完整區塊：報價卡片 + 區間條 + LLM分析卡片"""
    daily_range = daily_range or {}

    if "error" in quote:
        quote_block = f"""
        <div style="background:{COLOR_BG_CARD}; border:1px solid {COLOR_BORDER};
            border-radius:8px; padding:16px; color:{COLOR_NEGATIVE};">
          {quote['error']}
        </div>
        """
        range_block = ""
    else:
        try:
            change_val = float(quote.get("change") or 0)
        except (TypeError, ValueError):
            change_val = 0
        change_color = COLOR_POSITIVE if change_val >= 0 else COLOR_NEGATIVE
        change_sign = "+" if change_val >= 0 else ""

        quote_block = f"""
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
            style="border-spacing:8px 0;">
          <tr>
            {_metric_cell("今日收盤價", f"${quote.get('price', '-')}")}
            {_metric_cell("今日漲跌幅", f"{change_sign}{quote.get('change_percent', '-')}", change_color)}
            {_metric_cell("今日漲跌額", f"{change_sign}{quote.get('change', '-')}", change_color)}
            {_metric_cell("單日交易量", f"{quote.get('volume', '-')}")}
          </tr>
        </table>
        """
        range_block = _price_range_bar(
            low=daily_range.get("low"),
            close=quote.get("price"),
            high=daily_range.get("high"),
        )

    positive_html = _bullet_card("利多因素", "利多因素", COLOR_POSITIVE, analysis.get("positive", []))
    negative_html = _bullet_card("利空/潛在風險", "利空/潛在風險", COLOR_NEGATIVE, analysis.get("negative", []))
    neutral_html = _bullet_card("中立消息", "中立消息", "#d4d4d4", analysis.get("neutral", []))

    return f"""
    <div style="margin-bottom:32px;">
      <h2 style="color:#ffffff; font-size:24px; margin-bottom:4px;">{symbol}</h2>
      <div style="color:{COLOR_TEXT_MUTED}; font-size:13px; margin-bottom:14px;">
        共分析 {news_count} 則相關新聞
      </div>

      {quote_block}
      {range_block}

      <div style="margin-top:18px;">
        {positive_html}
        {negative_html}
        {neutral_html}
      </div>

      <div style="background:{COLOR_BG_CARD}; border:1px solid {COLOR_BORDER};
          border-radius:8px; padding:14px 18px; color:{COLOR_TEXT}; font-size:14px;
          line-height:1.7;">
        <b style="color:#ffffff;">整體趨勢摘要：</b><br>{analysis.get('summary', '')}
      </div>
    </div>
    """


def build_overview_table(overview_rows: list) -> str:
    """
    報告最上方的總覽表格：一眼看到所有追蹤股票的漲跌。
    overview_rows: [{"symbol": "NVDA", "price": "204.12", "change_percent": "3.65%", "is_up": True}, ...]
    """
    if not overview_rows:
        return ""

    rows_html = ""
    for row in overview_rows:
        color = COLOR_POSITIVE if row.get("is_up") else COLOR_NEGATIVE
        sign = "▲" if row.get("is_up") else "▼"
        rows_html += f"""
        <tr>
          <td style="padding:10px 12px; color:#ffffff; font-size:14px; font-weight:bold;
              border-bottom:1px solid {COLOR_BORDER};">{row.get('symbol', '-')}</td>
          <td align="right" style="padding:10px 12px; color:{COLOR_TEXT}; font-size:14px;
              border-bottom:1px solid {COLOR_BORDER};">${row.get('price', '-')}</td>
          <td align="right" style="padding:10px 12px; color:{color}; font-size:14px; font-weight:bold;
              border-bottom:1px solid {COLOR_BORDER};">{sign} {row.get('change_percent', '-')}</td>
        </tr>
        """

    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
        style="background:{COLOR_BG_CARD}; border:1px solid {COLOR_BORDER};
        border-radius:8px; margin-bottom:24px; overflow:hidden;">
      <tr>
        <td style="padding:10px 12px; color:{COLOR_TEXT_MUTED}; font-size:12px;">股票</td>
        <td align="right" style="padding:10px 12px; color:{COLOR_TEXT_MUTED}; font-size:12px;">現價</td>
        <td align="right" style="padding:10px 12px; color:{COLOR_TEXT_MUTED}; font-size:12px;">漲跌幅</td>
      </tr>
      {rows_html}
    </table>
    """


def build_report_email(report_datetime_str: str, stock_sections_html: list,
                        overview_rows: list = None) -> str:
    """把總覽表格 + 所有股票區塊組合成一封完整的Email HTML"""
    sections_joined = "".join(stock_sections_html)
    overview_html = build_overview_table(overview_rows or [])

    return f"""
    <html>
    <body style="margin:0; padding:0; background:#ffffff;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
          style="background:{COLOR_BG_PAGE};">
        <tr>
          <td align="center" style="padding:24px 12px;">
            <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                style="max-width:600px; width:100%;">
              <tr>
                <td>
                  <h1 style="color:#ffffff; font-size:26px; margin-bottom:4px;">
                    每日股市新聞報告
                  </h1>
                  <div style="color:{COLOR_TEXT_MUTED}; font-size:13px; margin-bottom:24px;">
                    產生時間：{report_datetime_str}
                  </div>

                  {overview_html}
                  {sections_joined}

                  <div style="color:{COLOR_TEXT_MUTED}; font-size:12px; margin-top:12px;
                      border-top:1px solid {COLOR_BORDER}; padding-top:12px;">
                    本報告由 Python 自動產生，資料來源：Alpha Vantage，分析：Google Gemini
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
