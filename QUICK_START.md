# ⚡ QUICK START — 5 MINUTES

**Get Trighub Skill running in 5 minutes**

---

## STEP 1: Start Server (1 min)

```bash
cd ~/Trighub\ Skill
python3 trighub-webhook-v2.py
```

Expected: Server running on port 8888

---

## STEP 2: Configure Webhook (2 min)

1. Go to Trighub dashboard
2. Settings → Webhooks
3. Add: `https://trighub.xox.vn/webhook`
4. Enable retry
5. Test webhook

---

## STEP 3: Generate Report (1 min)

```bash
python3 generate_financial_report_vi.py 30
```

Output: `/Users/trinhhao/Financial_Reports/Báó_cáo_tài_chính_*.xlsx`

---

## STEP 4: View Report (1 min)

```bash
open ~/Financial_Reports/Báó_cáo_tài_chính_*.xlsx
```

**Done!** ✅

---

## NEXT STEPS

- View transactions: `sqlite3 trighub_transactions.db`
- Monitor logs: `tail -f ~/trighub-webhook.log`
- Setup automation: `crontab -e`

---

**Need more help?** Read SKILL.md
