#!/usr/bin/env python3
"""
Trighub Webhook Receiver v2 with Data Persistence & Analysis
- Receives webhook data from Trighub
- Persists to SQLite database
- Supports recovery queue for reliability
- Claude Code can analyze stored data
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WEBHOOK_SECRET = os.environ.get("TRIGHUB_SECRET", "")
TELEGRAM_USERID = "475039450"
LOG_FILE = os.path.expanduser("~/trighub-webhook.log")
DB_PATH = os.path.expanduser("~/trighub_transactions.db")
QUEUE_DB_PATH = os.path.expanduser("~/trighub_queue.db")

def log(message):
    """Log to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")

class Database:
    """Handle transaction storage and queue"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.queue_db_path = QUEUE_DB_PATH
        self.init_transaction_db()
        self.init_queue_db()
    
    def init_transaction_db(self):
        """Create transaction table for analysis"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                received_at TEXT NOT NULL,
                amount REAL NOT NULL,
                content TEXT,
                bank_name TEXT,
                transaction_type TEXT,  -- 'IN' or 'OUT'
                category TEXT,          -- Auto-categorized
                raw_data TEXT,          -- Full JSON
                processed INTEGER DEFAULT 0
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT UNIQUE,
                category TEXT,
                type TEXT  -- 'IN' or 'OUT'
            )
        ''')
        
        # Insert default categories
        default_categories = [
            ('NHAN', 'Transfer In', 'IN'),
            ('SALARY', 'Salary', 'IN'),
            ('PAYMENT VISA', 'Card Payment', 'OUT'),
            ('TRANSFER', 'Transfer Out', 'OUT'),
            ('WITHDRAWAL', 'Cash Withdrawal', 'OUT'),
            ('INTEREST', 'Interest', 'IN'),
        ]
        
        try:
            for pattern, category, txn_type in default_categories:
                conn.execute('''
                    INSERT OR IGNORE INTO categories (pattern, category, type)
                    VALUES (?, ?, ?)
                ''', (pattern, category, txn_type))
            conn.commit()
        except:
            pass
        
        conn.close()
    
    def init_queue_db(self):
        """Create queue table for reliability"""
        conn = sqlite3.connect(self.queue_db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pending_webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                data TEXT,
                status TEXT,  -- pending, processed, failed
                retry_count INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_transaction(self, data):
        """Save transaction to database"""
        conn = sqlite3.connect(self.db_path)
        
        # Categorize
        category = self._categorize(data.get('content', ''))
        txn_type = 'IN' if 'NHAN' in data.get('content', '').upper() else 'OUT'
        
        conn.execute('''
            INSERT INTO transactions 
            (timestamp, received_at, amount, content, bank_name, transaction_type, category, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            data.get('amount', 0),
            data.get('content', ''),
            data.get('bankName', ''),
            txn_type,
            category,
            json.dumps(data)
        ))
        conn.commit()
        conn.close()
        
        log(f"💾 Saved to DB: {data.get('amount')} {txn_type} ({category})")
    
    def _categorize(self, content):
        """Auto-categorize based on content"""
        content_upper = content.upper()
        
        conn = sqlite3.connect(self.db_path)
        categories = conn.execute('''
            SELECT pattern, category FROM categories
        ''').fetchall()
        conn.close()
        
        for pattern, category in categories:
            if pattern in content_upper:
                return category
        
        return 'Other'
    
    def queue_webhook(self, data):
        """Add to recovery queue"""
        conn = sqlite3.connect(self.queue_db_path)
        conn.execute('''
            INSERT INTO pending_webhooks (timestamp, data, status)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), json.dumps(data), 'pending'))
        conn.commit()
        conn.close()
    
    def mark_processed(self, webhook_id):
        """Mark queue item as processed"""
        conn = sqlite3.connect(self.queue_db_path)
        conn.execute('''
            UPDATE pending_webhooks 
            SET status = 'processed' 
            WHERE id = ?
        ''', (webhook_id,))
        conn.commit()
        conn.close()
    
    def get_pending(self):
        """Get pending webhooks"""
        conn = sqlite3.connect(self.queue_db_path)
        rows = conn.execute('''
            SELECT id, data FROM pending_webhooks 
            WHERE status = 'pending'
            LIMIT 100
        ''').fetchall()
        conn.close()
        return rows
    
    def process_pending(self):
        """Process all pending webhooks on startup"""
        pending = self.get_pending()
        if pending:
            log(f"⏳ Processing {len(pending)} pending webhooks from queue...")
        
        for webhook_id, data_json in pending:
            try:
                data = json.loads(data_json)
                self.save_transaction(data)
                send_to_telegram(data, "📦 [FROM QUEUE] ")
                self.mark_processed(webhook_id)
                log(f"✅ Processed queued webhook #{webhook_id}")
            except Exception as e:
                log(f"❌ Failed to process queued #{webhook_id}: {e}")

db = Database()

class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming webhook requests"""
    
    def log_message(self, format, *args):
        """Override to use custom logging"""
        log(f"HTTP: {format % args}")
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                return
            
            # Read body
            body = self.rfile.read(content_length)
            
            # Verify signature if secret is set
            if WEBHOOK_SECRET:
                import hmac
                import hashlib
                
                signature = self.headers.get('X-Trighub-Signature', '')
                if not signature:
                    log("⚠️ Missing X-Trighub-Signature header")
                    self.send_response(401)
                    self.end_headers()
                    return
                
                expected_sig = hmac.new(
                    WEBHOOK_SECRET.encode(),
                    body,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected_sig):
                    log("❌ Invalid signature")
                    self.send_response(401)
                    self.end_headers()
                    return
            
            # Parse JSON
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError as e:
                log(f"❌ Invalid JSON: {e}")
                self.send_response(400)
                self.end_headers()
                return
            
            # Log webhook data
            log(f"✅ Webhook received from {self.client_address[0]}")
            log(f"📦 Data: {json.dumps(data, ensure_ascii=False)}")
            
            # Save to database
            try:
                db.save_transaction(data)
            except Exception as e:
                log(f"⚠️ Failed to save to DB: {e}")
                db.queue_webhook(data)  # Queue for retry
            
            # Send to Telegram
            try:
                send_to_telegram(data)
                log(f"💬 Sent to Telegram successfully")
            except subprocess.TimeoutExpired:
                log("❌ Telegram send timeout")
                db.queue_webhook(data)
            except Exception as e:
                log(f"⚠️ Telegram send failed: {e}")
                db.queue_webhook(data)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "timestamp": datetime.now().isoformat()
            }).encode())
            
        except Exception as e:
            log(f"❌ Error processing request: {e}")
            self.send_response(500)
            self.end_headers()

def send_to_telegram(data, prefix=""):
    """Send formatted data to Telegram"""
    amount = data.get('amount', 0)
    content = data.get('content', '')[:100]
    bank = data.get('bankName', 'Unknown')
    
    txn_type = "📥 IN" if 'NHAN' in content.upper() else "📤 OUT"
    
    message = f"""{prefix}{txn_type} | {amount:,} VND
━━━━━━━━━━━━━━━━━━━━━━━━━━
🏦 Bank: {bank}
📝 Content: {content}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}"""
    
    result = subprocess.run(
        [
            "/opt/homebrew/bin/openclaw", "message", "send",
            "--channel", "telegram",
            "--target", TELEGRAM_USERID,
            "--message", message
        ],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        log(f"❌ Telegram error: {result.stderr}")
        raise Exception(result.stderr)

def main():
    """Start webhook server"""
    port = 8888
    server_address = ('0.0.0.0', port)
    
    log("=" * 60)
    log("🚀 Starting Trighub Webhook Receiver v2")
    log(f"📍 Listening on 0.0.0.0:{port}")
    log(f"🔗 URL: https://trighub.xox.vn")
    log(f"💾 Database: {DB_PATH}")
    log(f"📦 Queue DB: {QUEUE_DB_PATH}")
    log("=" * 60)
    
    # Process pending webhooks on startup
    db.process_pending()
    
    # Start HTTP server
    httpd = HTTPServer(server_address, WebhookHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log("\n⏹️  Shutting down...")
        httpd.shutdown()
        log("✅ Server stopped")

if __name__ == "__main__":
    main()
