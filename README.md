# scanner.py
# Binance Spot USDT - 1 saatlik kırılım ve geri test tarayıcısı

from __future__ import annotations

import concurrent.futures
import csv
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
QUOTE_ASSET = os.getenv("QUOTE_ASSET", "USDT").upper()
MIN_QUOTE_VOLUME = float(os.getenv("MIN_QUOTE_VOLUME_USDT", "500000"))
VOLUME_MULTIPLIER = float(os.getenv("VOLUME_MULTIPLIER", "1.5"))
BREAKOUT_LOOKBACK = int(os.getenv("BREAKOUT_LOOKBACK", "20"))
VOLUME_LOOKBACK = int(os.getenv("VOLUME_LOOKBACK", "20"))
RETEST_MAX_BARS = int(os.getenv("RETEST_MAX_BARS", "5"))
STOP_ATR_MULTIPLIER = float(os.getenv("STOP_ATR_MULTIPLIER", "1.5"))
TARGET_ATR_MULTIPLIER = float(os.getenv("TARGET_ATR_MULTIPLIER", "3.0"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "8"))
REQUEST_TIMEOUT = 20

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=MAX_WORKERS,
        pool_maxsize=MAX_WORKERS,
    )
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "BinanceSpotScanner/1.0"})
    return session


SESSION = make_session()


def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    response = SESSION.get(
        f"{BASE_URL}{path}",
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def klines_to_df(rows: list[list[Any]]) -> pd.DataFrame:
    columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore",
    ]

    df = pd.DataFrame(rows, columns=columns)

    for col in (
        "open", "high", "low", "close", "volume", "quote_volume"
    ):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["open_time"] = pd.to_datetime(
        df["open_time"], unit="ms", utc=True
    )
    df["close_time"] = pd.to_datetime(
        df["close_time"], unit="ms", utc=True
    )

    return (
        df.dropna(subset=["open", "high", "low", "close", "volume"])
        .reset_index(drop=True)
    )


def get_btc_filter() -> tuple[bool, float, float]:
    """Yalnızca kapanmış 4 saatlik BTC mumlarını kullanır."""
    rows = api_get(
        "/api/v3/klines",
        {"symbol": "BTCUSDT", "interval": "4h", "limit": 230},
    )

    df = klines_to_df(rows)

    # Son mum henüz kapanmamış olabilir; kullanma.
    closed = df.iloc[:-1].copy()

    if len(closed) < 200:
        raise RuntimeError("BTC EMA200 için yeterli 4 saatlik veri yok.")

    ema200 = closed["close"].ewm(
        span=200, adjust=False
    ).mean().iloc[-1]

    close = float(closed["close"].iloc[-1])

    return close > float(ema200), close, float(ema200)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["ema20"] = df["close"].ewm(
        span=20, adjust=False
    ).mean()

    df
