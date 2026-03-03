#!/usr/bin/env python3
"""
crawler.py - Crawl dữ liệu quỹ cổ phiếu từ API Fmarket
Ghi output vào public/data.json

Chạy local:
    cd crawler
    python crawler.py

GitHub Actions: Chạy tự động theo lịch cron (xem .github/workflows/crawl.yml)
"""

import json
import os
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

from fund_list import STOCK_FUNDS
from calculator import (
    calc_redness_index,
    calc_estimated_nav_change,
    calc_estimated_nav,
    extract_sell_fees,
    get_redness_badge,
)

# ── Cấu hình ──────────────────────────────────────────────────────────────────

API_BASE = "https://api.fmarket.vn/home/product"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://fmarket.vn",
    "Referer": "https://fmarket.vn/",
}

DELAY_BETWEEN_REQUESTS = 0.8   # giây - tránh bị rate limit
REQUEST_TIMEOUT = 15            # giây

# Múi giờ Việt Nam (UTC+7)
VN_TZ = timezone(timedelta(hours=7))

# Đường dẫn output
OUTPUT_DIR = Path(__file__).parent.parent / "public"
OUTPUT_FILE = OUTPUT_DIR / "data.json"

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Fetch một quỹ ─────────────────────────────────────────────────────────────

def fetch_fund(code: str) -> dict | None:
    """
    Gọi API Fmarket lấy thông tin một quỹ.
    Trả về dict dữ liệu thô, hoặc None nếu lỗi.
    """
    url = f"{API_BASE}/{code}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()

        if payload.get("status") != 200:
            log.warning(f"[{code}] API trả về status lạ: {payload.get('status')}")
            return None

        return payload.get("data")

    except requests.exceptions.Timeout:
        log.error(f"[{code}] Timeout sau {REQUEST_TIMEOUT}s")
    except requests.exceptions.HTTPError as e:
        log.error(f"[{code}] HTTP error: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        log.error(f"[{code}] Request lỗi: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        log.error(f"[{code}] Parse JSON lỗi: {e}")

    return None


# ── Xử lý dữ liệu thô → dạng chuẩn ──────────────────────────────────────────

def process_fund(raw: dict, code: str) -> dict:
    """
    Chuyển dữ liệu thô từ API sang cấu trúc gọn, chuẩn cho frontend.
    """
    nav_change = raw.get("productNavChange") or {}
    top_holdings = raw.get("productTopHoldingList") or []
    industries = raw.get("productIndustriesHoldingList") or []
    fee_list = (raw.get("productFeeList") or []) + (raw.get("productFeeSipList") or [])
    risk = raw.get("riskLevel") or {}
    fund_type_obj = raw.get("dataFundAssetType") or {}

    # --- Tính toán ---
    redness_index = calc_redness_index(top_holdings)
    estimated_nav_change = calc_estimated_nav_change(top_holdings)
    current_nav = raw.get("nav") or 0
    estimated_nav = calc_estimated_nav(current_nav, estimated_nav_change)
    badge = get_redness_badge(redness_index)
    sell_fees = extract_sell_fees(fee_list)

    # --- Top holdings gọn ---
    holdings_clean = []
    for h in top_holdings:
        holdings_clean.append({
            "stockCode": h.get("stockCode", ""),
            "industry": h.get("industry", ""),
            "netAssetPercent": h.get("netAssetPercent"),
            "price": h.get("price"),
            "changeFromPrevious": h.get("changeFromPrevious"),
            "changeFromPreviousPercent": h.get("changeFromPreviousPercent"),
            "isRed": (h.get("changeFromPreviousPercent") or 0) < 0,
        })

    # --- Industries gọn ---
    industries_clean = [
        {
            "industry": i.get("industry", ""),
            "assetPercent": i.get("assetPercent"),
        }
        for i in industries
    ]

    return {
        "code": code,
        "name": raw.get("name", ""),
        "shortName": raw.get("shortName", code),
        "fundType": fund_type_obj.get("name", ""),
        "nav": current_nav,
        "navToPrevious": nav_change.get("navToPrevious"),
        "riskLevel": risk.get("name", ""),
        "managementFee": raw.get("managementFee"),
        "totalAssetBillion": _parse_total_asset(raw),

        # --- Tính toán ---
        "rednessIndex": redness_index,
        "estimatedNavChange": estimated_nav_change,
        "estimatedNav": estimated_nav,
        "badge": badge,

        # --- Performance ---
        "performance": {
            "navTo1Months": nav_change.get("navTo1Months"),
            "navTo3Months": nav_change.get("navTo3Months"),
            "navTo6Months": nav_change.get("navTo6Months"),
            "navTo12Months": nav_change.get("navTo12Months"),
            "navTo24Months": nav_change.get("navTo24Months"),
            "navTo36Months": nav_change.get("navTo36Months"),
            "navTo60Months": nav_change.get("navTo60Months"),
            "navTo7Years": nav_change.get("navTo7Years"),
            "navToEstablish": nav_change.get("navToEstablish"),
            "annualizedReturn36Months": nav_change.get("annualizedReturn36Months"),
        },

        # --- Phí ---
        "fees": {
            "buyPct": _get_buy_fee(fee_list),
            "sell": sell_fees,
            "managementPct": raw.get("managementFee"),
        },

        # --- Danh mục ---
        "topHoldings": holdings_clean,
        "industries": industries_clean,

        # --- Meta ---
        "website": raw.get("website", ""),
        "closedOrderBookAt": raw.get("closedOrderBookAt", "14:40"),
    }


def _parse_total_asset(raw: dict) -> float | None:
    """Lấy tổng tài sản (tỷ VND) từ fundReport."""
    report = raw.get("fundReport") or {}
    val = report.get("totalAssetValue")
    if val:
        return round(val / 1e9, 1)  # Chuyển sang tỷ VND
    return None


def _get_buy_fee(fee_list: list) -> float:
    """Lấy phí mua cơ bản (thường là 0%)."""
    for fee in fee_list:
        if fee.get("type") == "BUY":
            return fee.get("fee", 0)
    return 0


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    now_vn = datetime.now(VN_TZ)
    log.info(f"=== Bắt đầu crawl lúc {now_vn.strftime('%H:%M:%S %d/%m/%Y')} ===")
    log.info(f"Tổng số quỹ cần crawl: {len(STOCK_FUNDS)}")

    results = []
    errors = []

    for i, code in enumerate(STOCK_FUNDS, 1):
        log.info(f"[{i}/{len(STOCK_FUNDS)}] Đang crawl: {code}")
        raw = fetch_fund(code)

        if raw is None:
            log.warning(f"[{code}] Bỏ qua do lỗi")
            errors.append(code)
        else:
            fund_data = process_fund(raw, code)
            results.append(fund_data)
            log.info(
                f"[{code}] OK → NAV: {fund_data['nav']:,.0f} | "
                f"Redness: {fund_data['rednessIndex']:.2f}% | "
                f"Est NAV change: {fund_data['estimatedNavChange']:+.2f}% "
                f"{fund_data['badge']['emoji']}"
            )

        # Delay để tránh rate limit (trừ lần cuối)
        if i < len(STOCK_FUNDS):
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # --- Sắp xếp: Redness Index cao nhất lên đầu ---
    results.sort(key=lambda x: x["rednessIndex"], reverse=True)

    # --- Build output JSON ---
    next_update = now_vn + timedelta(hours=1)

    output = {
        "lastUpdated": now_vn.isoformat(),
        "lastUpdatedStr": now_vn.strftime("%H:%M %d/%m/%Y"),
        "nextUpdate": next_update.isoformat(),
        "tradingDate": now_vn.strftime("%Y-%m-%d"),
        "totalFunds": len(results),
        "failedFunds": errors,
        "funds": results,
    }

    # --- Ghi file ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info(f"=== Hoàn thành ===")
    log.info(f"✅ Crawl thành công: {len(results)}/{len(STOCK_FUNDS)} quỹ")
    if errors:
        log.warning(f"❌ Lỗi: {errors}")
    log.info(f"📁 Đã ghi: {OUTPUT_FILE}")

    # --- In top 5 để preview ---
    log.info("\n--- TOP 5 quỹ đỏ nhất hôm nay ---")
    for fund in results[:5]:
        log.info(
            f"  {fund['badge']['emoji']} {fund['code']:12s} "
            f"Redness: {fund['rednessIndex']:.2f}% | "
            f"Est: {fund['estimatedNavChange']:+.2f}% | "
            f"NAV: {fund['nav']:,.0f}"
        )


if __name__ == "__main__":
    main()
