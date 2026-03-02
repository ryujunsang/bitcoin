#!/usr/bin/env python3
"""
실시간 BTC/KRW & TSLA 시세 수집 및 REPORT.md 자동 업데이트 스크립트
"""

import json
import os
import urllib.request
from datetime import datetime, timezone


def fetch_btc_data():
    """CoinGecko API로 BTC/KRW 데이터 수집"""
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin&vs_currencies=krw"
        "&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
    )
    try:
        req = urllib.request.Request(
            url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())["bitcoin"]
        return {
            "price": data.get("krw", 0),
            "change_24h": round(data.get("krw_24h_change", 0), 2),
            "market_cap": data.get("krw_market_cap", 0),
            "volume_24h": data.get("krw_24h_vol", 0),
        }
    except Exception as e:
        print(f"BTC 데이터 수집 오류: {e}")
        return None


def fetch_tsla_data():
    """Yahoo Finance API로 TSLA 데이터 수집"""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/TSLA?interval=1d&range=2d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        meta = data["chart"]["result"][0]["meta"]
        price = meta.get("regularMarketPrice", 0)
        prev_close = meta.get("chartPreviousClose") or meta.get("previousClose", 0)
        change = round(price - prev_close, 2) if prev_close else 0
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0
        return {
            "price": round(price, 2),
            "prev_close": round(prev_close, 2),
            "change": change,
            "change_pct": change_pct,
            "volume": meta.get("regularMarketVolume", 0),
            "52w_high": round(meta.get("fiftyTwoWeekHigh", 0), 2),
            "52w_low": round(meta.get("fiftyTwoWeekLow", 0), 2),
        }
    except Exception as e:
        print(f"TSLA 데이터 수집 오류: {e}")
        return None


def update_history(btc, tsla, ts):
    history_path = "data/history.json"
    try:
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        history = {"last_updated": "", "records": []}

    record = {
        "timestamp": ts,
        "btc_krw": btc["price"] if btc else None,
        "btc_change_24h": btc["change_24h"] if btc else None,
        "tsla_usd": tsla["price"] if tsla else None,
        "tsla_change_24h": tsla["change_pct"] if tsla else None,
    }
    history["records"].append(record)
    history["last_updated"] = ts
    # 최근 288개(24시간) 유지
    history["records"] = history["records"][-288:]

    os.makedirs("data", exist_ok=True)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return history["records"]


def arrow(val):
    if val is None:
        return "⬜"
    return "🔴▼" if val < 0 else ("🟢▲" if val > 0 else "⬜")


def fmt_krw(v):
    return f"₩{v:,.0f}" if v else "N/A"


def fmt_usd(v):
    return f"${v:,.2f}" if v else "N/A"


def generate_report(btc, tsla, records, ts_kst):
    recent = records[-10:][::-1]
    history_rows = ""
    for r in recent:
        t = r["timestamp"][:16].replace("T", " ")
        b_price = fmt_krw(r.get("btc_krw"))
        b_chg = (
            f"{r['btc_change_24h']:+.2f}%"
            if r.get("btc_change_24h") is not None
            else "N/A"
        )
        t_price = fmt_usd(r.get("tsla_usd"))
        t_chg = (
            f"{r['tsla_change_24h']:+.2f}%"
            if r.get("tsla_change_24h") is not None
            else "N/A"
        )
        history_rows += f"| {t} UTC | {b_price} | {b_chg} | {t_price} | {t_chg} |\n"

    btc_price_str = fmt_krw(btc["price"]) if btc else "데이터 없음"
    btc_chg_str = f"{arrow(btc['change_24h'])} {btc['change_24h']:+.2f}%" if btc else "N/A"
    btc_vol_str = fmt_krw(btc["volume_24h"]) if btc else "N/A"
    btc_mcap_str = fmt_krw(btc["market_cap"]) if btc else "N/A"

    tsla_price_str = fmt_usd(tsla["price"]) if tsla else "데이터 없음"
    tsla_chg_str = f"{arrow(tsla['change_pct'])} {tsla['change_pct']:+.2f}% (${tsla['change']:+.2f})" if tsla else "N/A"
    tsla_52h = f"${tsla['52w_high']:,.2f}" if tsla else "N/A"
    tsla_52l = f"${tsla['52w_low']:,.2f}" if tsla else "N/A"

    return f"""# 📊 실시간 시세 보고서

> 🕐 **마지막 업데이트 (KST):** {ts_kst}
> ⚙️ GitHub Actions에 의해 **5분마다 자동 갱신**됩니다.

---

## 🟡 비트코인 (BTC/KRW) — 업비트 기준

| 항목 | 값 |
|:-----|:---|
| 💰 현재가 | **{btc_price_str}** |
| 📊 24시간 변화율 | {btc_chg_str} |
| 📦 거래량 (24h) | {btc_vol_str} |
| 🏦 시가총액 | {btc_mcap_str} |

---

## 🔵 테슬라 (TSLA / NASDAQ)

| 항목 | 값 |
|:-----|:---|
| 💰 현재가 | **{tsla_price_str}** |
| 📊 당일 변화율 | {tsla_chg_str} |
| 📅 52주 최고가 | {tsla_52h} |
| 📅 52주 최저가 | {tsla_52l} |

---

## 📈 최근 시세 히스토리 (최근 10회)

| 시간 | BTC (KRW) | BTC 변화율 | TSLA (USD) | TSLA 변화율 |
|:-----|:---------:|:---------:|:---------:|:-----------:|
{history_rows}
---

*📡 데이터 소스: [CoinGecko API](https://www.coingecko.com) / [Yahoo Finance](https://finance.yahoo.com)*
*⚙️ 자동화: GitHub Actions · 업데이트 주기: 5분*
*📂 히스토리: [data/history.json](./data/history.json)*
"""


if __name__ == "__main__":
    now_utc = datetime.now(timezone.utc)
    ts_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    kst_hour = (now_utc.hour + 9) % 24
    ts_kst = f"{now_utc.strftime('%Y-%m-%d')} {kst_hour:02d}:{now_utc.strftime('%M')} KST"

    print("📡 데이터 수집 중...")
    btc = fetch_btc_data()
    tsla = fetch_tsla_data()
    print(f"✅ BTC: {btc}")
    print(f"✅ TSLA: {tsla}")

    records = update_history(btc, tsla, ts_iso)
    report = generate_report(btc, tsla, records, ts_kst)

    with open("REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("✅ REPORT.md 업데이트 완료!")
