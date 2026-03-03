# calculator.py - Tính toán Redness Index và Estimated NAV Change
# Không cần thư viện ngoài, chỉ dùng Python built-in


def calc_redness_index(top_holdings: list) -> float:
    """
    Tính Redness Index = tổng (weight * |change|) cho các mã đang GIẢM.

    Args:
        top_holdings: list các dict từ productTopHoldingList
            - netAssetPercent: tỷ trọng % trong quỹ
            - changeFromPreviousPercent: % thay đổi giá so với hôm qua

    Returns:
        float: Redness Index (%), ví dụ 1.20 nghĩa là danh mục bị kéo xuống 1.20%
    """
    redness = 0.0
    for holding in top_holdings:
        change = holding.get("changeFromPreviousPercent")
        weight = holding.get("netAssetPercent")
        if change is None or weight is None:
            continue
        if change < 0:
            redness += (weight / 100) * abs(change)
    return round(redness, 4)


def calc_estimated_nav_change(top_holdings: list) -> float:
    """
    Tính % thay đổi NAV ước tính trong ngày dựa trên Top Holdings.
    Tính CẢ mã xanh lẫn đỏ (không chỉ mã đỏ).

    Lưu ý: Top Holdings chỉ chiếm ~50-60% danh mục thực tế,
    nên đây là ước tính, không phải con số chính xác 100%.

    Returns:
        float: % ước tính thay đổi NAV, ví dụ -1.15 nghĩa là NAV giảm ~1.15%
    """
    estimated_change = 0.0
    total_weight_used = 0.0

    for holding in top_holdings:
        change = holding.get("changeFromPreviousPercent")
        weight = holding.get("netAssetPercent")
        if change is None or weight is None:
            continue
        estimated_change += (weight / 100) * change
        total_weight_used += weight / 100

    return round(estimated_change, 4)


def calc_estimated_nav(current_nav: float, estimated_change_pct: float) -> float:
    """
    Tính NAV ước tính cuối ngày hôm nay.

    Args:
        current_nav: NAV hiện tại (hôm qua)
        estimated_change_pct: % thay đổi ước tính (từ calc_estimated_nav_change)

    Returns:
        float: NAV ước tính hôm nay
    """
    return round(current_nav * (1 + estimated_change_pct / 100), 2)


def extract_sell_fees(fee_list: list) -> list:
    """
    Trích xuất bảng phí bán từ productFeeList.

    Returns:
        list of dict: [{"label": "< 12 tháng", "fee": 2.0}, ...]
    """
    sell_fees = []
    seen = set()

    for fee in fee_list:
        if fee.get("type") != "SELL":
            continue

        begin = fee.get("beginVolume", 0)
        end = fee.get("endVolume")
        fee_val = fee.get("fee", 0)
        unit = fee.get("feeUnitType", "MONTH")

        if unit != "MONTH":
            continue

        # Tạo label
        if end is None:
            label = f">= {int(begin)} tháng"
        else:
            label = f"< {int(end)} tháng" if begin == 0 else f"{int(begin)}-{int(end)} tháng"

        key = label
        if key not in seen:
            seen.add(key)
            sell_fees.append({"label": label, "months_min": int(begin), "fee_pct": fee_val})

    # Sort theo months_min
    sell_fees.sort(key=lambda x: x["months_min"])
    return sell_fees


def get_redness_badge(redness_index: float) -> dict:
    """
    Xác định badge hiển thị dựa trên Redness Index.

    Returns:
        dict: {"emoji": "🔴", "label": "Đỏ mạnh", "color": "red"}
    """
    if redness_index >= 1.5:
        return {"emoji": "🔴", "label": "Đỏ mạnh – Cơ hội DCA", "color": "red"}
    elif redness_index >= 0.5:
        return {"emoji": "🟡", "label": "Đỏ nhẹ", "color": "yellow"}
    else:
        return {"emoji": "🟢", "label": "Xanh – Thị trường tốt", "color": "green"}
