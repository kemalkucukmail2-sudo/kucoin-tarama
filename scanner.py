import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.binance.com"
OUTPUT_FILE = "reports/latest.csv"
MIN_QUOTE_VOLUME = 2_000_000
MAX_COINS = 180
WORKERS = 8

FIELDS = [
    "symbol", "signal", "score", "price", "entry", "stop", "target",
    "rsi", "quote_volume_24h", "market_regime", "adx",
    "ema20_gap_pct", "volume_ratio", "breakout",
    "ema4h200_ok", "reason", "candle_close_time_utc", "scan_time_utc"
]

session = requests.Session()
retry = Retry(
    total=4,
    backoff_factor=0.7,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry, pool_connections=WORKERS, pool_maxsize=WORKERS)
session.mount("https://", adapter)
session.headers.update({"User-Agent": "BinanceSpotScanner/1.0"})


def api(path, params=None):
    response = session.get(
        BASE_URL + path,
        params=params,
        timeout=20
    )
    response.raise_for_status()
    return response.json()


def candles(symbol, interval, limit):
    raw = api("/api/v3/klines", {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    })

    columns = [
        "time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ]
    df = pd.DataFrame(raw, columns=columns)

    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["close_time"] = pd.to_numeric(df["close_time"], errors="coerce")

    # Açık olan son mum kullanılmasın.
    now_ms = int(time.time() * 1000)
    df = df[df["close_time"] < now_ms].copy()

    return df.reset_index(drop=True)


def indicators(df):
    df = df.copy()

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))
    df["rsi"] = df["rsi"].fillna(50)

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs()
    ], axis=1).max(axis=1)

    df["atr"] = tr.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()

    up = df["high"].diff()
    down = -df["low"].diff()

    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)

    atr_for_di = tr.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean() / atr_for_di.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean() / atr_for_di.replace(0, np.nan)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    df["adx"] = dx.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean().fillna(0)

    df["volume_avg20"] = df["volume"].rolling(20).mean()
    df["volume_ratio"] = df["volume"] / df["volume_avg20"].replace(0, np.nan)

    df["ema20_prev"] = df["ema20"].shift(3)
    df["previous_high20"] = df["high"].shift(1).rolling(20).max()

    df["bb_mid"] = df["close"].rolling(20).mean()
    bb_std = df["close"].rolling(20).std(ddof=0)
    df["bb_upper"] = df["bb_mid"] + 2 * bb_std
    df["bb_lower"] = df["bb_mid"] - 2 * bb_std
    df["bb_width_pct"] = (
        (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"].replace(0, np.nan) * 100
    )

    return df


def scan_symbol(symbol, volume_24h):
    try:
        h4 = candles(symbol, "4h", 260)
        h1 = candles(symbol, "1h", 100)

        if len(h4) < 210 or len(h1) < 60:
            return None

        h4["ema200"] = h4["close"].ewm(span=200, adjust=False).mean()
        h4_last = h4.iloc[-1]
        h4_ok = bool(h4_last["close"] > h4_last["ema200"])

        h1 = indicators(h1)
        last = h1.iloc[-1]
        prev = h1.iloc[-2]

        price = float(last["close"])
        atr = float(last["atr"]) if pd.notna(last["atr"]) else 0.0
        rsi = float(last["rsi"])
        adx = float(last["adx"])
        ema20 = float(last["ema20"])
        ema50 = float(last["ema50"])

        if price <= 0 or atr <= 0:
            return None

        gap_pct = (price / ema20 - 1) * 100 if ema20 else 0.0
        volume_ratio = float(last["volume_ratio"]) if pd.notna(last["volume_ratio"]) else 0.0

        trend_ok = price > ema20 > ema50
        macd_ok = last["macd"] > last["macd_signal"] and last["macd_hist"] > prev["macd_hist"]
        rsi_ok = 50 <= rsi <= 68
        adx_ok = adx >= 20
        volume_ok = volume_ratio >= 1.2
        ema_rising = last["ema20"] > last["ema20_prev"]
        breakout = bool(
            pd.notna(last["previous_high20"])
            and price > float(last["previous_high20"])
            and volume_ratio >= 1.5
        )
        pullback = bool(
            ema20 > 0
            and abs(price / ema20 - 1) <= 0.012
            and price >= ema20
            and last["close"] >= last["open"]
        )

        score = 0
        reasons = []

        if h4_ok:
            score += 15
            reasons.append("4s EMA200 üstü")
        else:
            reasons.append("4s EMA200 altı")

        if trend_ok:
            score += 20
            reasons.append("1s yükseliş trendi")

        if macd_ok:
            score += 15
            reasons.append("MACD pozitif")

        if rsi_ok:
            score += 10
            reasons.append("RSI uygun")

        if adx_ok:
            score += 10
            reasons.append("ADX güçlü")

        if volume_ok:
            score += 10
            reasons.append("Hacim destekli")

        if breakout or pullback:
            score += 10
            reasons.append("Kırılım/geri çekilme")

        if ema_rising:
            score += 5
            reasons.append("EMA20 yükseliyor")

        bullish_candle = (
            last["close"] > last["open"]
            and last["close"] > prev["close"]
        )
        if bullish_candle:
            score += 5
            reasons.append("Pozitif mum")

        bb_width = float(last["bb_width_pct"]) if pd.notna(last["bb_width_pct"]) else 0.0
        if adx < 17 or (bb_width < 3 and adx < 22):
            regime = "YATAY"
        elif trend_ok and adx >= 20:
            regime = "YÜKSELİŞ"
        else:
            regime = "KARARSIZ"

        late_entry = gap_pct > 2.5 or rsi >= 72
        entry_ok = h4_ok and trend_ok and (breakout or pullback) and not late_entry

        if not h4_ok or regime == "YATAY":
            signal = "UYGUN DEĞİL"
        elif entry_ok and score >= 80 and macd_ok and volume_ok:
            signal = "GÜÇLÜ AL"
        elif entry_ok and score >= 65 and macd_ok:
            signal = "AL"
        else:
            signal = "BEKLE"

        stop = price - 1.5 * atr
        target = price + 2.5 * atr

        close_time = datetime.fromtimestamp(
            int(last["close_time"]) / 1000, tz=timezone.utc
        ).isoformat()

        return {
            "symbol": symbol,
            "signal": signal,
            "score": score,
            "price": round(price, 8),
            "entry": round(price, 8),
            "stop": round(stop, 8),
            "target": round(target, 8),
            "rsi": round(rsi, 2),
            "quote_volume_24h": round(volume_24h, 2),
            "market_regime": regime,
            "adx": round(adx, 2),
            "ema20_gap_pct": round(gap_pct, 2),
            "volume_ratio": round(volume_ratio, 2),
            "breakout": "EVET" if breakout else "HAYIR",
            "ema4h200_ok": "EVET" if h4_ok else "HAYIR",
            "reason": ", ".join(reasons),
            "candle_close_time_utc": close_time,
            "scan_time_utc": datetime.now(timezone.utc).isoformat()
        }

    except Exception as exc:
        print(f"{symbol} tarama hatası: {exc}")
        return None


def main():
    print("Binance Spot taraması başlıyor...")

    exchange_info = api("/api/v3/exchangeInfo")
    tickers = api("/api/v3/ticker/24hr")

    allowed_symbols = {
        item["symbol"]
        for item in exchange_info["symbols"]
        if item.get("status") == "TRADING"
        and item.get("quoteAsset") == "USDT"
        and item.get("isSpotTradingAllowed", False)
    }

    volumes = {}
    for ticker in tickers:
        symbol = ticker.get("symbol")
        if symbol not in allowed_symbols:
            continue
        try:
            quote_volume = float(ticker.get("quoteVolume", 0))
        except (TypeError, ValueError):
            continue

        if quote_volume >= MIN_QUOTE_VOLUME:
            volumes[symbol] = quote_volume

    candidates = sorted(
        volumes.items(), key=lambda item: item[1], reverse=True
    )[:MAX_COINS]

    print(f"Taranacak coin sayısı: {len(candidates)}")

    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(scan_symbol, symbol, volume): symbol
            for symbol, volume in candidates
        }

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)

    results.sort(
        key=lambda row: (
            {"GÜÇLÜ AL": 0, "AL": 1, "BEKLE": 2, "UYGUN DEĞİL": 3}.get(row["signal"], 4),
            -row["score"],
            -row["quote_volume_24h"]
        )
    )

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    print(f"Tarama tamamlandı. Sonuç sayısı: {len(results)}")
    print(f"Dosya kaydedildi: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
