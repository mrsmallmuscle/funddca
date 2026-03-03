# FundDCA - Crawler Setup

## Cấu trúc thư mục crawler/

```
crawler/
├── crawler.py        # Script chính - chạy file này
├── calculator.py     # Logic tính Redness Index, Estimated NAV
├── fund_list.py      # Danh sách 30 mã quỹ cổ phiếu
└── requirements.txt  # Chỉ cần: requests
```

---

## Chạy local (test trước khi deploy)

```bash
# 1. Cài dependency
cd crawler
pip install -r requirements.txt

# 2. Chạy crawler
python crawler.py
```

Output sẽ được ghi vào `public/data.json`

---

## Output mẫu khi chạy thành công

```
09:30:00 [INFO] === Bắt đầu crawl lúc 09:30:00 03/03/2026 ===
09:30:00 [INFO] Tổng số quỹ cần crawl: 30
09:30:00 [INFO] [1/30] Đang crawl: VESAF
09:30:01 [INFO] [VESAF] OK → NAV: 37,845 | Redness: 1.20% | Est NAV change: -1.15% 🟡
09:30:02 [INFO] [2/30] Đang crawl: VEOF
...
09:30:45 [INFO] === Hoàn thành ===
09:30:45 [INFO] ✅ Crawl thành công: 30/30 quỹ
09:30:45 [INFO] 📁 Đã ghi: public/data.json

--- TOP 5 quỹ đỏ nhất hôm nay ---
  🔴 VESAF        Redness: 1.20% | Est: -1.15% | NAV: 37,845
  🟡 DCDS         Redness: 0.98% | Est: -0.87% | NAV: ...
  ...
```

---

## Deploy lên GitHub Actions

1. **Tạo thư mục** `.github/workflows/` trong repo
2. **Copy file** `github-workflows-crawl.yml` vào `.github/workflows/crawl.yml`
3. **Push lên GitHub** → Actions sẽ tự chạy theo lịch

> ⚠️ Lưu ý: GitHub Actions cron có thể delay 5-15 phút so với giờ đặt.

---

## Lịch chạy tự động

| Giờ VN | Cron (UTC) | Mục đích |
|--------|-----------|---------|
| 09:30 | `30 2 * * 1-5` | Mở phiên sáng |
| 10:30 | `30 3 * * 1-5` | Giữa phiên sáng |
| 11:30 | `30 4 * * 1-5` | Gần nghỉ trưa |
| 13:30 | `30 6 * * 1-5` | Mở phiên chiều |
| 14:30 | `30 7 * * 1-5` | **⚠️ Quan trọng** - 10 phút trước giờ chốt lệnh 14:40 |
| 15:30 | `30 8 * * 1-5` | NAV cuối ngày |

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|------------|-----------|
| `HTTPError: 404` | Mã quỹ không tồn tại hoặc sai | Kiểm tra lại `fund_list.py` |
| `Timeout` | API chậm | Tăng `REQUEST_TIMEOUT` lên 30s |
| `ConnectionError` | Không có mạng | GitHub Actions retry tự động |
| `KeyError` | API thay đổi cấu trúc JSON | Kiểm tra lại `process_fund()` trong `crawler.py` |
