# 📊 FINANCIAL REPORTS GUIDE

**Hướng dẫn tạo & sử dụng báó cáo tài chính**

---

## 🚀 TẠNG BÁO CÁO

### Tạo báó cáo 30 ngày
```bash
python3 generate_financial_report_vi.py 30
```

### Tạo báó cáo 90 ngày
```bash
python3 generate_financial_report_vi.py 90
```

### Custom filename
```bash
python3 generate_financial_report_vi.py 30 "My_Report.xlsx"
```

---

## 📁 BÁÓXÁC ĐƯỢC LƯU Ở ĐÂU

```
~/Financial_Reports/Báó_cáo_tài_chính_2026-03.xlsx
```

### Mở báó cáo
```bash
open ~/Financial_Reports/Báó_cáo_tài_chính_*.xlsx
```

---

## 📊 BÁÓÁC CÓ 4 SHEETS

### 1. Tóm Tắt (Summary)
- Tổng thu nhập
- Tổng chi phí
- Lưu lại ròng
- Tỷ lệ tiết kiệm

### 2. Danh Mục (Categories)
- Chi tiêu theo loại
- Biểu đồ phân bố
- Top categories

### 3. Hàng Ngày (Daily)
- Giao dịch từng ngày
- Cộng dồn theo ngày
- Trend line

### 4. Top Giao Dịch (Top Transactions)
- 20 giao dịch lớn nhất
- Sorted by amount

---

## 🤖 AUTOMATION (Auto-Generate Daily)

### Setup Cron
```bash
crontab -e

# Thêm dòng (9:00 AM hàng ngày)
0 9 * * * python3 ~/Trighub\ Skill/generate_financial_report_vi.py 30
```

### Weekly Report (Monday)
```bash
0 9 * * 1 python3 ~/Trighub\ Skill/generate_financial_report_vi.py 7
```

### Monthly Report (1st of month)
```bash
0 9 1 * * python3 ~/Trighub\ Skill/generate_financial_report_vi.py 30
```

---

## 💡 USAGE EXAMPLES

### Generate report và mở ngay
```bash
python3 generate_financial_report_vi.py 30 && \
  open ~/Financial_Reports/Báó_cáo_tài_chính_*.xlsx
```

### Generate với custom name
```bash
python3 generate_financial_report_vi.py 30 "March_Report.xlsx"
```

### List all reports
```bash
ls -lh ~/Financial_Reports/
```

---

## 📈 BÁÓÁC THỐNG KÊ

### Tóm Tắt (Summary Sheet)
```
Thống kê       Giá trị
─────────────────────
Tổng giao dịch  50
Tổng thu nhập   2,000,000 VND
Tổng chi phí    3,500,000 VND
Lưu lại ròng   -1,500,000 VND
Tỷ lệ tiết kiệm 42.8%
```

### Danh Mục (Categories)
```
Danh mục      Số tiền
─────────────────────
Ăn uống       800,000 VND
Giao thông    500,000 VND
Mua sắm       1,200,000 VND
Khác          1,000,000 VND
```

---

## 🆘 TROUBLESHOOTING

### Report không tạo được
```bash
# Kiểm tra database có data
sqlite3 ~/Trighub\ Skill/trighub_transactions.db \
  "SELECT COUNT(*) FROM transactions;"

# Nếu 0, webhook chưa nhận dữ liệu
```

### Report lỗi khi mở
- Database corrupted? → Khởi động lại server
- Không đủ dữ liệu → Chờ webhooks

### File location lỗi
```bash
# Tạo folder nếu không có
mkdir -p ~/Financial_Reports

# Thử lại
python3 generate_financial_report_vi.py 30
```

---

## 📊 EXCEL FEATURES

✅ Color-coded headers (blue)
✅ Formatted numbers (1,000,000 VND)
✅ Professional tables
✅ Charts & graphs
✅ Mobile-friendly layout

---

## 🎯 BEST PRACTICES

1. **Generate weekly** - Easier to track
2. **Name by date** - "Report_2026-03.xlsx"
3. **Archive reports** - Keep them organized
4. **Share easily** - Email/Drive compatible

---

**Time to generate:** < 5 seconds | **File size:** ~50-100 KB
