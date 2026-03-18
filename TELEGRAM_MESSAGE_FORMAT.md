# 📱 TELEGRAM MESSAGE FORMAT v2.2

**Định dạng tin nhắn Telegram khi nhận webhook từ Trighub**

---

## 💚 NHẬN (Inflow) - Khi có tiền được thêm vào tài khoản

### Format:
```
💚 NHẬN

Ngân hàng: [Bank Name]
Số tiền: [Amount] VND
Mã giao dịch: [Transaction ID]
Nội dung: [Transfer content]

⏰ Thời gian: HH:MM:SS - DD/MM/YYYY
```

### Example:
```
💚 NHẬN

Ngân hàng: Techcombank
Số tiền: 5,000,000 VND
Mã giao dịch: TRX123456789
Nội dung: Lương tháng 3/2026

⏰ Thời gian: 03:47:18 - 19/03/2026
```

### Webhook Data:
```json
{
  "amount": 5000000,
  "content": "Lương tháng 3/2026",
  "bankName": "Techcombank",
  "transactionType": "IN",
  "transaction_id": "TRX123456789"
}
```

---

## ❤️ CHUYỂN (Outflow) - Khi có tiền bị trừ

### Format:
```
❤️ CHUYỂN

Ngân hàng: [Bank Name]
Số tiền: [Amount] VND
Tên người nhận: [Recipient Name]
Mã giao dịch: [Transaction ID]
Nội dung: [Transfer content]

⏰ Thời gian: HH:MM:SS - DD/MM/YYYY
```

### Example:
```
❤️ CHUYỂN

Ngân hàng: Techcombank
Số tiền: 500,000 VND
Tên người nhận: Nguyễn Văn A
Mã giao dịch: TRX987654321
Nội dung: Payment for service

⏰ Thời gian: 03:47:18 - 19/03/2026
```

### Webhook Data:
```json
{
  "amount": 500000,
  "content": "Payment for service",
  "bankName": "Techcombank",
  "transactionType": "OUT",
  "transaction_id": "TRX987654321",
  "recipient_name": "Nguyễn Văn A"
}
```

---

## 📊 Tất cả thông tin cần có

### NHẬN (IN):
- ✅ Ngân hàng (bankName)
- ✅ Số tiền (amount)
- ✅ Mã giao dịch (transaction_id)
- ✅ Nội dung chuyển khoản (content)
- ✅ Thời gian (timestamp)

### CHUYỂN (OUT):
- ✅ Ngân hàng (bankName)
- ✅ Số tiền (amount)
- ✅ Tên người nhận (recipient_name)
- ✅ Mã giao dịch (transaction_id)
- ✅ Nội dung chuyển khoản (content)
- ✅ Thời gian (timestamp)

---

## 🎨 Formatting

- **Bold:** `<b>Text</b>` (sử dụng HTML)
- **Italic:** `<i>Text</i>`
- **Monospace (Code):** `<code>Text</code>`
- **Mode:** parse_mode = "HTML"

---

## 🧪 Test Format

### Test NHẬN:
```bash
curl -X POST http://localhost:8888/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000000,
    "content": "Lương tháng 3/2026",
    "bankName": "Techcombank",
    "transactionType": "IN",
    "transaction_id": "TRX123456789"
  }'
```

### Test CHUYỂN:
```bash
curl -X POST http://localhost:8888/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500000,
    "content": "Payment for service",
    "bankName": "Techcombank",
    "transactionType": "OUT",
    "transaction_id": "TRX987654321",
    "recipient_name": "Nguyễn Văn A"
  }'
```

---

## 📝 Webhook Data Mapping

Khi Trighub gửi webhook, dữ liệu được map như sau:

| Telegram | JSON Field | Description |
|----------|-----------|-------------|
| 💚/❤️ Title | transactionType | IN = 💚 NHẬN, OUT = ❤️ CHUYỂN |
| Ngân hàng | bankName | Tên ngân hàng |
| Số tiền | amount | Số tiền (formatted: 1,000,000) |
| Tên người nhận | recipient_name | Chỉ cho CHUYỂN |
| Mã giao dịch | transaction_id | ID giao dịch |
| Nội dung | content | Nội dung chuyển khoản |
| Thời gian | (auto) | Thời gian hiện tại |

---

## ✅ Verification

Check webhook logs:
```bash
tail -f /tmp/trighub-webhook.log
```

View sent transactions:
```bash
sqlite3 ~/trighub_transactions.db \
  "SELECT amount, bankName, transactionType, transaction_id FROM transactions ORDER BY id DESC LIMIT 3;"
```

Check Telegram app for messages!

---

## 📱 Visual Preview

### NHẬN Message:
```
💚 NHẬN

Ngân hàng: Techcombank
Số tiền: 5,000,000 VND
Mã giao dịch: TRX123456789
Nội dung: Lương tháng 3/2026

⏰ Thời gian: 03:47:18 - 19/03/2026
```

### CHUYỂN Message:
```
❤️ CHUYỂN

Ngân hàng: Techcombank
Số tiền: 500,000 VND
Tên người nhận: Nguyễn Văn A
Mã giao dịch: TRX987654321
Nội dung: Payment for service

⏰ Thời gian: 03:47:18 - 19/03/2026
```

---

## 🚀 Version History

**v2.2** (2026-03-19 03:47)
- Enhanced message format
- Separate NHẬN and CHUYỂN templates
- Added recipient name for CHUYỂN
- Added transaction ID
- Professional HTML formatting

**v2.1** (2026-03-19 03:30)
- Initial Telegram support
- Basic transaction notification

---

**Server Version:** v2.2  
**Last Updated:** 2026-03-19 03:47 GMT+7
