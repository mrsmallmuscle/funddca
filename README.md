# FundDCA – Trợ lý Săn "Sale" Chứng chỉ Quỹ Cổ phiếu Việt Nam

> Ứng dụng theo dõi danh mục quỹ mở cổ phiếu theo thời gian thực, giúp nhà đầu tư ra quyết định DCA (Dollar-Cost Averaging) dựa trên "độ đỏ" của danh mục.

---

## 📌 Mục tiêu dự án

- Crawl dữ liệu từ API Fmarket mỗi 1 giờ trong giờ giao dịch
- Tính toán **Chỉ số Đỏ (Redness Index)** cho từng quỹ cổ phiếu
- Hiển thị thông tin trực quan để người dùng quyết định có nên DCA hay không
- Monetize thông qua **Affiliate link Fmarket** trên toàn bộ app

---

## 🔗 Affiliate Link Configuration

> **QUAN TRỌNG:** Fmarket affiliate chỉ có 1 link duy nhất dạng `https://fmarket.vn/reward/YOUR_REWARD_CODE`. Khi click, người dùng được đưa đến App Store/CH Play để cài app Fmarket.

### Kỹ thuật: Hiển thị URL đẹp khi hover, redirect affiliate khi click

Đây là yêu cầu UX quan trọng:
- **Hover chuột lên link quỹ** → Status bar trình duyệt hiện: `https://fmarket.vn/quy/vesaf` (trông tự nhiên, tin cậy)
- **Khi click thực tế** → Redirect đến: `https://fmarket.vn/reward/YOUR_REWARD_CODE` (affiliate)

Kỹ thuật này dùng `data-*` attribute + JavaScript `click` handler, **KHÔNG dùng** `href` trực tiếp là affiliate link.

```javascript
// config.js - Cấu hình affiliate (chỉ cần thay 1 chỗ duy nhất)
const AFFILIATE_CONFIG = {
  // ← THAY GIÁ TRỊ NÀY bằng link reward thực của bạn
  rewardLink: "https://fmarket.vn/reward/YOUR_REWARD_CODE",

  // Template URL hiển thị khi hover (người dùng thấy URL này ở status bar)
  // Chỉ dùng để hiển thị, KHÔNG phải link thực tế
  displayFundUrl: (fundCode) =>
    `https://fmarket.vn/quy/${fundCode.toLowerCase()}`,

  displayListUrl: "https://fmarket.vn/danh-sach-quy",
};
```

```javascript
// app.js - Hàm tạo affiliate link áp dụng cho toàn app
function createAffLink(displayUrl, element) {
  // Gán href = URL đẹp → trình duyệt hiện URL này khi hover
  element.href = displayUrl;

  // Khi click → chặn navigation mặc định, redirect sang affiliate
  element.addEventListener("click", function (e) {
    e.preventDefault();
    window.open(AFFILIATE_CONFIG.rewardLink, "_blank");
  });
}

// Cách dùng khi render từng quỹ:
// <a href="" data-fund="VESAF" class="aff-link">VESAF</a>

document.querySelectorAll(".aff-link").forEach((el) => {
  const fundCode = el.dataset.fund;
  const displayUrl = fundCode
    ? AFFILIATE_CONFIG.displayFundUrl(fundCode)
    : AFFILIATE_CONFIG.displayListUrl;
  createAffLink(displayUrl, el);
});
```

**Kết quả thực tế:**
```
Người dùng hover vào nút "DCA ngay" của quỹ VESAF
  → Status bar hiện: https://fmarket.vn/quy/vesaf  ✅ (trông tự nhiên)

Người dùng click
  → Thực tế mở: https://fmarket.vn/reward/YOUR_REWARD_CODE  ✅ (affiliate)
```

**Nguyên tắc áp dụng toàn app:**
- Mọi `<a>` và `<button>` liên quan đến quỹ → thêm class `aff-link` + `data-fund="{FUND_CODE}"`
- Link tổng (không theo quỹ cụ thể) → thêm class `aff-link` không có `data-fund`
- KHÔNG hardcode `href="https://fmarket.vn/reward/..."` trực tiếp trong HTML
- Chỉ cần đổi `rewardLink` trong `config.js` là toàn bộ app cập nhật

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────┐
│              GITHUB ACTIONS (Cron)               │
│  Chạy mỗi 1h trong giờ giao dịch (9:30 - 15:00) │
│                                                   │
│  crawler.py                                       │
│  ├── Gọi API Fmarket (~30 quỹ cổ phiếu)         │
│  ├── Tính Redness Index cho từng quỹ             │
│  ├── Tính Estimated NAV Change                   │
│  └── Ghi vào public/data.json                    │
└──────────────────┬──────────────────────────────┘
                   │ git commit & push
                   ▼
┌─────────────────────────────────────────────────┐
│           GITHUB REPOSITORY                      │
│  public/data.json  (cập nhật mỗi 1h)            │
│  index.html        (trang chủ - Chỉ số Đỏ)      │
│  fees.html         (So sánh phí)                 │
│  sectors.html      (Lọc theo ngành)              │
│  performance.html  (So sánh hiệu suất)           │
│  fund.html         (Chi tiết quỹ)                │
│  config.js         (Affiliate config)            │
└──────────────────┬──────────────────────────────┘
                   │ GitHub Pages
                   ▼
┌─────────────────────────────────────────────────┐
│           GITHUB PAGES (Frontend)                │
│  your-domain.com  (Custom domain miễn phí)       │
│  JS đọc data.json và render UI                   │
└─────────────────────────────────────────────────┘
```

**Chi phí: $0/tháng** (chỉ tốn ~$10/năm nếu mua custom domain)

---

## 📊 Nguồn dữ liệu

### API Fmarket
```
GET https://api.fmarket.vn/home/product/{FUND_CODE}
```

Ví dụ: `https://api.fmarket.vn/home/product/VESAF`

### Danh sách ~30 quỹ cổ phiếu mở trên Fmarket
```python
FUND_CODES = [
    "VESAF", "VEOF", "VDEF", "VMEEF",  # VinaCapital
    "DCDS", "DCDE", "DCAF",             # Dragon Capital
    "MAGEF", "MAFEQI",                  # Manulife
    "BVFED", "BVPF",                    # Bảo Việt
    "VCBF-BCF", "VCBF-AIF", "VCBF-MGF",# VCBF
    "SSISCA", "VLGF",                   # SSI
    "UVEEF",                            # UOB
    "BMFF", "MBVF",                     # MB
    "EVESG",                            # Eastspring
    "VNDAF",                            # VND
    "PHVSF",                            # Phú Hưng
    "TBLF",                             # Thiên Việt
    "TCGF",                             # Techcom
    "NTPPF",                            # NTP
    "LHCDF",                            # LHC
    "GDEGF",                            # GDE
    "KDEF",                             # KDE
    "RVPIF",                            # RVPI
]
```

### Các trường dữ liệu quan trọng từ JSON

| Trường JSON | Dùng cho trang | Mô tả |
|-------------|----------------|-------|
| `productTopHoldingList[].changeFromPreviousPercent` | Trang 1, 4 | % thay đổi giá live của từng mã trong danh mục |
| `productTopHoldingList[].netAssetPercent` | Trang 1, 4 | Tỷ trọng % GAV của mã trong quỹ |
| `productFeeList[]` (type=SELL) | Trang 2 | Bảng phí bán theo thời gian nắm giữ |
| `productIndustriesHoldingList[]` | Trang 3 | % phân bổ theo ngành |
| `productNavChange.navTo12Months` | Trang 5 | Lợi nhuận 12 tháng |
| `productNavChange.navTo36Months` | Trang 5 | Lợi nhuận 36 tháng |
| `productNavChange.annualizedReturn36Months` | Trang 5 | Lợi nhuận trung bình/năm (3 năm) |
| `nav` | Tất cả | NAV hiện tại |
| `productNavChange.navToPrevious` | Tất cả | % thay đổi NAV so với hôm qua |
| `riskLevel.name` | Trang 2, 5 | Mức độ rủi ro |
| `managementFee` | Trang 2 | Phí quản lý năm |

---

## 📐 Công thức tính toán

### Redness Index (Chỉ số Đỏ)

```
RednessIndex = Σ ( netAssetPercent_i × |changeFromPreviousPercent_i| )
               với mọi i có changeFromPreviousPercent_i < 0
```

**Ví dụ với VESAF:**
```
MBB:  8.53% × 2.98% = 0.2542
CTG:  5.09% × 3.66% = 0.1863
GMD:  4.74% × 4.03% = 0.1910
FPT:  4.67% × 3.55% = 0.1658
VCB:  4.36% × 3.08% = 0.1343
MWG:  4.06% × 3.33% = 0.1352
ACB:  3.90% × 2.44% = 0.0952
HPG:  3.55% × 1.04% = 0.0369
─────────────────────────────
RednessIndex VESAF ≈ 1.20%
```

→ Nghĩa là danh mục VESAF đang bị kéo xuống khoảng **1.20%** trong phiên hôm nay.

### Estimated NAV Change (Dự báo NAV)

```
EstimatedNAVChange (%) = Σ ( netAssetPercent_i × changeFromPreviousPercent_i )
                         (tính CẢ mã xanh lẫn đỏ, chỉ dùng Top Holdings)

EstimatedNAV = currentNAV × (1 + EstimatedNAVChange / 100)
```

---

## 📱 Chi tiết các trang Frontend

---

### Trang 1: Chỉ số Đỏ – Cơ hội DCA (`index.html`)

**Mục tiêu:** Trang chủ, giúp người dùng biết ngay quỹ nào đang "sale" nhất hôm nay.

**Hiển thị:**
- Header: Logo app + thời gian cập nhật gần nhất + banner "Mở tài khoản Fmarket [AFF LINK]"
- Bảng xếp hạng quỹ theo Redness Index (cao nhất lên đầu):
  - Tên quỹ (click → `fundDeepLink`)
  - Redness Index (%)
  - NAV hiện tại
  - % thay đổi NAV hôm qua (`navToPrevious`)
  - Dự báo NAV hôm nay (`EstimatedNAVChange`)
  - Badge: 🔴 Đỏ mạnh / 🟡 Đỏ nhẹ / 🟢 Xanh
  - Nút **"DCA ngay"** → `fundDeepLink` (affiliate)

**Logic hiển thị badge:**
```
RednessIndex > 1.5% → 🔴 "Đỏ mạnh – Cơ hội DCA tốt"
RednessIndex 0.5-1.5% → 🟡 "Đỏ nhẹ"
RednessIndex < 0.5% → 🟢 "Xanh – Thị trường tốt"
```

**Filter/Sort:**
- Sắp xếp: Đỏ nhất / NAV thấp nhất / Lợi nhuận cao nhất
- Filter: Chỉ hiện quỹ đỏ / Tất cả

**CTA chính:** Banner sticky bottom "Chưa có tài khoản? Mở ngay trên Fmarket [AFF LINK]"

---

### Trang 2: So sánh Phí & Thanh khoản (`fees.html`)

**Mục tiêu:** Giúp người dùng chọn quỹ phù hợp với thời gian dự kiến nắm giữ.

**Hiển thị:**
- Bảng so sánh phí bán tất cả quỹ:

| Quỹ | Phí mua | < 6 tháng | 6-12 tháng | 12-24 tháng | ≥ 24 tháng | Phí quản lý/năm |
|-----|---------|-----------|-----------|------------|------------|-----------------|
| VESAF | 0% | 2% | 2% | 1% | 0% | 1.75% |
| ... | | | | | | |

- Bộ lọc theo kế hoạch đầu tư:
  - "Tôi định giữ < 6 tháng" → Highlight quỹ có phí bán thấp nhất
  - "Tôi định giữ 1-2 năm" → Highlight quỹ có breakeven phí sớm nhất
  - "Tôi giữ dài hạn > 2 năm" → Highlight quỹ có phí quản lý thấp nhất

- Insight tự động: "Với kế hoạch giữ 12 tháng, [Quỹ X] có tổng chi phí thấp nhất"

**CTA:** Mỗi hàng có nút "Đầu tư ngay" → `fundDeepLink` (affiliate)

---

### Trang 3: Bản đồ Ngành (`sectors.html`)

**Mục tiêu:** Tìm quỹ phù hợp với kỳ vọng ngành của người dùng.

**Hiển thị:**
- Dropdown chọn ngành: Ngân hàng / Bất động sản / Công nghệ / Bán lẻ / ...
- Sau khi chọn ngành → Xếp hạng quỹ có tỷ trọng ngành đó cao nhất
- Heatmap trực quan: Mỗi quỹ là 1 ô, màu đậm = tỷ trọng ngành cao

**Ví dụ:** Người dùng chọn "Ngân hàng" → App hiện:
```
1. VESAF    – Ngân hàng 21.88% GAV → Nút "Đầu tư" [AFF]
2. VEOF     – Ngân hàng 18.5%  GAV → Nút "Đầu tư" [AFF]
3. DCDS     – Ngân hàng 15.2%  GAV → Nút "Đầu tư" [AFF]
```

**CTA:** Nút "Đầu tư vào quỹ này" → `fundDeepLink` (affiliate)

---

### Trang 4: Chi tiết Quỹ & Dự báo NAV (`fund.html?code=VESAF`)

**Mục tiêu:** Xem nhanh "nội công" của 1 quỹ và quyết định có mua hôm nay không.

**Hiển thị:**
- Header: Tên quỹ, NAV hiện tại, % thay đổi hôm qua
- **Box dự báo NAV hôm nay** (nổi bật nhất trang):
  ```
  ┌─────────────────────────────────────┐
  │  📊 Dự báo NAV hôm nay              │
  │  Dựa trên Top 10 cổ phiếu trong    │
  │  danh mục:                          │
  │                                     │
  │  Ước tính NAV: 37,278 VND           │
  │  Thay đổi: -1.5% so với hôm qua    │
  │                                     │
  │  ⏰ Đặt lệnh trước 14:40 hôm nay   │
  │  [DCA NGAY – GIÁ TỐT HÔM NAY] [AFF]│
  └─────────────────────────────────────┘
  ```
- Biểu đồ tăng trưởng NAV: Dùng data `navTo12Months`, `navTo36Months`, `navTo60Months`
- Bảng Top Holdings: Mã CK, % GAV, giá, % thay đổi hôm nay (xanh/đỏ)
- Phân bổ ngành: Bar chart ngang
- Thông tin phí: Phí mua, phí bán theo tháng nắm giữ

**CTA:** Nút sticky "Đặt lệnh mua trên Fmarket" → `fundDeepLink` (affiliate)

---

### Trang 5: So sánh Hiệu suất (`performance.html`)

**Mục tiêu:** Tìm quỹ có hiệu suất tốt nhưng đang "sale" hôm nay = điểm mua lý tưởng.

**Hiển thị:**
- Bảng so sánh tất cả quỹ:

| Quỹ | 1 tháng | 3 tháng | 6 tháng | 1 năm | 3 năm/năm | Hôm nay |
|-----|---------|---------|---------|-------|-----------|---------|
| VESAF | +2.92% | +12.40% | +2.76% | +19.54% | +21.91%/yr | 🔴 -1.5% |

- Highlight tự động: Quỹ có `annualizedReturn36Months > 15%` VÀ `RednessIndex > 1%` hôm nay → Badge "⭐ Mua vùng giá tốt"
- Sort: Theo lợi nhuận 1 năm / 3 năm / Đỏ nhất hôm nay

**CTA:** Nút "Đầu tư ngay" theo từng hàng → `fundDeepLink` (affiliate)

---

## ⚙️ Workflow chi tiết

### Workflow hệ thống (Tự động)

```
Thứ 2 - Thứ 6:
  09:30 → GitHub Actions chạy crawler.py
  10:30 → GitHub Actions chạy crawler.py
  11:30 → GitHub Actions chạy crawler.py
  13:30 → GitHub Actions chạy crawler.py
  14:30 → GitHub Actions chạy crawler.py  ← QUAN TRỌNG (trước giờ chốt 14:40)
  15:30 → GitHub Actions chạy crawler.py  ← Cập nhật NAV cuối ngày

crawler.py thực hiện:
  1. Lặp qua danh sách FUND_CODES
  2. Gọi GET https://api.fmarket.vn/home/product/{code}
  3. Parse JSON, tính RednessIndex, EstimatedNAVChange
  4. Gộp tất cả vào data.json
  5. git commit & push lên GitHub
  6. GitHub Pages tự động deploy

Cuối ngày (16:00):
  - Reset data, giữ lại NAV cuối ngày để so sánh
```

### Workflow người dùng

```
Người dùng vào app (your-domain.com)
    │
    ▼
Trang chủ: Bảng Chỉ số Đỏ
    │
    ├── Thấy quỹ đỏ mạnh hôm nay
    │       │
    │       ├── Click "DCA ngay" → Fmarket [AFF] (Conversion!)
    │       │
    │       └── Click tên quỹ → Trang Chi tiết (fund.html)
    │               │
    │               └── Xem dự báo NAV, danh mục
    │                       │
    │                       └── Click "Đặt lệnh" → Fmarket [AFF] (Conversion!)
    │
    ├── Muốn tìm quỹ theo ngành → Trang 3 (sectors.html)
    │       └── Click "Đầu tư" → Fmarket [AFF] (Conversion!)
    │
    ├── Muốn so sánh phí → Trang 2 (fees.html)
    │       └── Click "Đầu tư ngay" → Fmarket [AFF] (Conversion!)
    │
    └── Muốn so sánh hiệu suất → Trang 5 (performance.html)
            └── Click "Đầu tư ngay" → Fmarket [AFF] (Conversion!)
```

---

## 📁 Cấu trúc thư mục dự án

```
ccq-fmarket/
│
├── .github/
│   └── workflows/
│       └── crawl.yml          # GitHub Actions - Cron job crawler
│
├── crawler/
│   ├── crawler.py             # Script Python chính
│   ├── calculator.py          # Tính Redness Index, Estimated NAV
│   ├── requirements.txt       # requests, json
│   └── fund_list.py           # Danh sách mã quỹ
│
├── public/                    # Thư mục GitHub Pages serve
│   ├── data.json              # ← File dữ liệu, cập nhật mỗi 1h (auto-generated)
│   ├── index.html             # Trang 1: Chỉ số Đỏ (trang chủ)
│   ├── fees.html              # Trang 2: So sánh Phí
│   ├── sectors.html           # Trang 3: Bản đồ Ngành
│   ├── fund.html              # Trang 4: Chi tiết Quỹ
│   ├── performance.html       # Trang 5: So sánh Hiệu suất
│   ├── config.js              # ← Affiliate link config (CHỈNH Ở ĐÂY)
│   ├── app.js                 # Logic JS chung
│   └── style.css              # CSS (hoặc dùng Tailwind CDN)
│
├── README.md                  # File này
└── .gitignore
```

---

## 📦 Cấu trúc `data.json` (output của crawler)

```json
{
  "lastUpdated": "2026-03-03T14:30:00+07:00",
  "nextUpdate": "2026-03-03T15:30:00+07:00",
  "tradingDate": "2026-03-03",
  "funds": [
    {
      "code": "VESAF",
      "name": "Quỹ Đầu Tư Cổ Phiếu Tiếp Cận Thị Trường VinaCapital",
      "shortName": "VESAF",
      "nav": 37845.99,
      "navToPrevious": -0.09,
      "rednessIndex": 1.20,
      "estimatedNAVChange": -1.15,
      "estimatedNAV": 37410.5,
      "riskLevel": "Trung bình-Cao",
      "managementFee": 1.75,
      "totalAssetBillion": 2535.1,
      "performance": {
        "navTo1Months": 2.92,
        "navTo3Months": 12.40,
        "navTo6Months": 2.76,
        "navTo12Months": 19.54,
        "navTo24Months": 35.19,
        "navTo36Months": 81.17,
        "annualizedReturn36Months": 21.91
      },
      "fees": {
        "buy": 0,
        "sell": [
          { "months": "< 12", "fee": 2 },
          { "months": "12-24", "fee": 1 },
          { "months": ">= 24", "fee": 0 }
        ]
      },
      "topHoldings": [
        {
          "stockCode": "MBB",
          "industry": "Ngân hàng",
          "netAssetPercent": 8.53,
          "price": 27.65,
          "changeFromPreviousPercent": -2.98
        }
      ],
      "industries": [
        { "industry": "Ngân hàng", "assetPercent": 21.88 },
        { "industry": "Sản xuất Phụ trợ", "assetPercent": 9.51 }
      ],
      "affLink": "https://fmarket.vn/quy/VESAF"
    }
  ]
}
```

---

## 🚀 Hướng dẫn triển khai

### Bước 1: Fork/Clone repo
```bash
git clone https://github.com/YOUR_USERNAME/ccq-fmarket.git
cd ccq-fmarket
```

### Bước 2: Cấu hình Affiliate link
Mở file `public/config.js`, thay `YOUR_AFF_CODE` bằng mã affiliate Fmarket của bạn:
```javascript
const AFFILIATE_CONFIG = {
  affCode: "YOUR_AFF_CODE",
  // ...
};
```

### Bước 3: Kích hoạt GitHub Actions
- Vào repo Settings → Actions → Cho phép Actions chạy
- File `.github/workflows/crawl.yml` sẽ tự động chạy theo lịch

### Bước 4: Kích hoạt GitHub Pages
- Repo Settings → Pages → Source: `main` branch, folder `/public`
- GitHub sẽ cấp domain: `https://YOUR_USERNAME.github.io/ccq-fmarket`

### Bước 5: Custom Domain (tùy chọn)
- Mua domain (~$10/năm)
- Repo Settings → Pages → Custom domain: nhập domain của bạn
- Thêm CNAME record trỏ về `YOUR_USERNAME.github.io`

---

## 📅 Lịch crawl (GitHub Actions Cron)

```yaml
# .github/workflows/crawl.yml
schedule:
  - cron: '30 2 * * 1-5'   # 09:30 ICT (UTC+7 = UTC-7h → 02:30 UTC)
  - cron: '30 3 * * 1-5'   # 10:30 ICT
  - cron: '30 4 * * 1-5'   # 11:30 ICT
  - cron: '30 6 * * 1-5'   # 13:30 ICT
  - cron: '30 7 * * 1-5'   # 14:30 ICT ← Quan trọng (trước 14:40 chốt lệnh)
  - cron: '30 8 * * 1-5'   # 15:30 ICT (NAV cuối ngày)
```

---

## 🎯 KPI & Affiliate Strategy

### Conversion Funnel
```
Người dùng vào app
    → Xem Chỉ số Đỏ (Awareness)
    → Thấy quỹ đang "sale" (Interest)  
    → Click "DCA ngay" → Fmarket (Action = Conversion!)
```

### CTA theo từng trang

| Trang | CTA Text | Vị trí |
|-------|----------|--------|
| Trang 1 | "DCA ngay – Giá tốt hôm nay" | Mỗi hàng quỹ đỏ |
| Trang 2 | "Đầu tư ngay – Phí 0%" | Mỗi hàng quỹ |
| Trang 3 | "Đầu tư vào quỹ cầm nhiều [Ngành]" | Sau khi lọc ngành |
| Trang 4 | "Đặt lệnh trước 14:40 hôm nay" | Sticky button |
| Trang 5 | "Mua vùng giá tốt – Hiệu suất top" | Quỹ được highlight |
| Global | "Chưa có tài khoản? Mở ngay" | Header/Footer |

---

## ⚠️ Lưu ý kỹ thuật

1. **Rate limit API Fmarket:** Crawl tuần tự với delay 0.5s giữa mỗi quỹ để tránh bị block
2. **Dữ liệu `changeFromPreviousPercent`:** Đã xác nhận là giá live trong ngày (khớp với Vietstock)
3. **Giờ giao dịch:** Chỉ có dữ liệu live từ T2-T6, 9:00-15:00. Ngoài giờ hiển thị NAV cuối ngày trước
4. **Top Holdings:** Fmarket chỉ cung cấp Top 10 mã, không phải toàn bộ danh mục. Estimated NAV chỉ là ước tính ~89% độ chính xác
5. **Không cần auth:** API Fmarket public không cần token

---

## 🔮 Roadmap tương lai (v2)

- [ ] Thông báo Telegram khi quỹ nào đó đạt Redness Index > 2%
- [ ] So sánh với VN-Index (quỹ nào đang beat thị trường)
- [ ] Lịch sử Redness Index 30 ngày (chart xu hướng đỏ/xanh)
- [ ] Watchlist cá nhân (lưu vào localStorage)
- [ ] Dark mode

---

*Cập nhật lần cuối: 03/03/2026*
