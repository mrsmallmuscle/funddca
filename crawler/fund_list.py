# fund_list.py - Danh sách toàn bộ quỹ cổ phiếu mở trên Fmarket
# Cập nhật: 03/2026
# Nguồn: https://fmarket.vn/danh-sach-quy (tab Quỹ cổ phiếu)

STOCK_FUNDS = [
    # VinaCapital
    "VESAF",
    "VEOF",
    "VDEF",
    "VMEEF",
    # Dragon Capital
    "DCDS",
    "DCDE",
    "DCAF",
    # Manulife / Mirae
    "MAGEF",
    "MAFEQI",
    # Bảo Việt
    "BVFED",
    "BVPF",
    # VCBF
    "VCBF-BCF",
    "VCBF-AIF",
    "VCBF-MGF",
    # SSI
    "SSISCA",
    "VLGF",
    # UOB
    "UVEEF",
    # MB
    "BMFF",
    "MBVF",
    # Eastspring
    "EVESG",
    # VND
    "VNDAF",
    # Phú Hưng
    "PHVSF",
    # Thiên Việt
    "TBLF",
    # Techcom
    "TCGF",
    # NTP
    "NTPPF",
    # LHC
    "LHCDF",
    # GDE
    "GDEGF",
    # KDE
    "KDEF",
    # RVPI
    "RVPIF",
    # VCAM
    "VCAMDF",
]

# Tên đầy đủ để hiển thị (nếu API không trả về)
FUND_DISPLAY_NAMES = {
    "VESAF": "VinaCapital VESAF",
    "VEOF": "VinaCapital VEOF",
    "VDEF": "VinaCapital VDEF",
    "VMEEF": "VinaCapital VMEEF",
    "DCDS": "Dragon Capital DCDS",
    "DCDE": "Dragon Capital DCDE",
    "DCAF": "Dragon Capital DCAF",
    "MAGEF": "Mirae Asset MAGEF",
    "MAFEQI": "Manulife MAFEQI",
    "BVFED": "Bảo Việt BVFED",
    "BVPF": "Bảo Việt BVPF",
    "VCBF-BCF": "VCBF Blue Chip",
    "VCBF-AIF": "VCBF AIF",
    "VCBF-MGF": "VCBF MGF",
    "SSISCA": "SSI SSISCA",
    "VLGF": "SSI VLGF",
    "UVEEF": "UOB UVEEF",
    "BMFF": "MB BMFF",
    "MBVF": "MB MBVF",
    "EVESG": "Eastspring EVESG",
    "VNDAF": "VND VNDAF",
    "PHVSF": "Phú Hưng PHVSF",
    "TBLF": "Thiên Việt TBLF",
    "TCGF": "Techcom TCGF",
    "NTPPF": "NTP NTPPF",
    "LHCDF": "LHC LHCDF",
    "GDEGF": "GDE GDEGF",
    "KDEF": "KDE KDEF",
    "RVPIF": "RVPI RVPIF",
    "VCAMDF": "VCAM VCAMDF",
}
