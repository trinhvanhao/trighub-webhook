# 🔗 WEBHOOK SETUP GUIDE

**Hướng dẫn cấu hình Trighub Webhook**

---

## 📋 TRƯỚC TIÊN

✅ Trighub Skill server đang chạy:
```bash
python3 trighub-webhook-v2.py
```

✅ URL webhook của bạn:
```
https://trighub.xox.vn/webhook
```

---

## 🔧 CẤU HÌNH TRIGHUB (5 BƯỚC)

### Step 1: Đăng Nhập Trighub
- Vào https://app.trighub.com
- Đăng nhập tài khoản

### Step 2: Vào Settings
- Click avatar → Settings
- Hoặc tìm "Webhooks" trong menu

### Step 3: Add Webhook
- Click "Add Webhook"
- URL: `https://trighub.xox.vn/webhook`
- Event type: "transaction" hoặc "all"
- Enable retry: ✅ ON

### Step 4: Test Webhook
- Click "Test Webhook"
- Xem kết quả trong log

### Step 5: Save
- Click "Save" hoặc "Create"

---

## ✅ KIỂM TRA

### Webhook hoạt động?
```bash
# Xem logs
tail ~/trighub-webhook.log

# Kiểm tra database
sqlite3 ~/Trighub\ Skill/trighub_transactions.db \
  "SELECT COUNT(*) FROM transactions;"
```

### Tạo test transaction
- Tên: Test Transaction
- Số tiền: 100,000 VND
- Loại: Chi (OUT)

### Xem log
```
✅ Webhook received
✅ Transaction saved
```

---

## 🆘 TROUBLESHOOTING

### Webhook not working?
1. Verify server is running: `ps aux | grep trighub`
2. Check logs: `tail -50 ~/trighub-webhook.log`
3. Test manually:
   ```bash
   curl -X POST http://localhost:8888/webhook \
     -H "Content-Type: application/json" \
     -d '{"amount": 100000, "transaction_type": "OUT"}'
   ```

### No transactions in database?
```bash
# Check transaction count
sqlite3 ~/Trighub\ Skill/trighub_transactions.db \
  "SELECT COUNT(*) FROM transactions;"

# If 0, webhooks not arriving
# - Check Trighub settings
# - Verify URL is correct
# - Check firewall
```

### Server not receiving webhooks?
1. Verify Cloudflare tunnel running
2. Check Trighub webhook URL: `https://trighub.xox.vn/webhook`
3. Test with curl (above)

---

## 📊 EXPECTED PAYLOAD

Trighub sẽ gửi JSON như này:
```json
{
  "transaction_id": "123456",
  "timestamp": "2026-03-19T10:30:00Z",
  "amount": 100000,
  "transaction_type": "OUT",
  "bank_name": "Techcombank",
  "content": "Payment for service"
}
```

---

## 🎯 SUCCESS INDICATORS

✅ Webhook setup thành công khi:
1. Logs show "Webhook received"
2. Database transaction count > 0
3. Reports generate with data
4. No errors in logs

---

**Setup Time:** 5 minutes | **Status:** Ready
