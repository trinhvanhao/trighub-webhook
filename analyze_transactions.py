#!/usr/bin/env python3
"""
Transaction Analysis Tool for Claude Code
Analyzes Trighub webhook data from SQLite database
Run from Claude Code to generate financial reports
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import os

DB_PATH = os.path.expanduser("~/trighub_transactions.db")

class TransactionAnalyzer:
    """Analyze transaction data"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_summary(self, days=30):
        """Get summary for last N days"""
        conn = sqlite3.connect(self.db_path)
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total income
        income = conn.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE transaction_type = 'IN' 
            AND timestamp >= ?
        ''', (cutoff_date,)).fetchone()[0]
        
        # Total expense
        expense = conn.execute('''
            SELECT COALESCE(SUM(amount), 0) 
            FROM transactions 
            WHERE transaction_type = 'OUT' 
            AND timestamp >= ?
        ''', (cutoff_date,)).fetchone()[0]
        
        # Transaction count
        txn_count = conn.execute('''
            SELECT COUNT(*) 
            FROM transactions 
            WHERE timestamp >= ?
        ''', (cutoff_date,)).fetchone()[0]
        
        conn.close()
        
        return {
            'period_days': days,
            'total_income': income,
            'total_expense': expense,
            'net': income - expense,
            'transaction_count': txn_count,
            'avg_transaction': (income + expense) / txn_count if txn_count > 0 else 0
        }
    
    def get_by_category(self, days=30):
        """Breakdown by category"""
        conn = sqlite3.connect(self.db_path)
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        rows = conn.execute('''
            SELECT category, transaction_type, COUNT(*) as count, SUM(amount) as total
            FROM transactions
            WHERE timestamp >= ?
            GROUP BY category, transaction_type
            ORDER BY total DESC
        ''', (cutoff_date,)).fetchall()
        
        conn.close()
        
        result = {}
        for category, txn_type, count, total in rows:
            key = f"{category} ({txn_type})"
            result[key] = {
                'count': count,
                'amount': total,
                'type': txn_type
            }
        
        return result
    
    def get_daily_breakdown(self, days=30):
        """Daily breakdown"""
        conn = sqlite3.connect(self.db_path)
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        rows = conn.execute('''
            SELECT DATE(timestamp), 
                   SUM(CASE WHEN transaction_type='IN' THEN amount ELSE 0 END) as income,
                   SUM(CASE WHEN transaction_type='OUT' THEN amount ELSE 0 END) as expense
            FROM transactions
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
        ''', (cutoff_date,)).fetchall()
        
        conn.close()
        
        result = {}
        for date, income, expense in rows:
            result[date] = {
                'income': income or 0,
                'expense': expense or 0,
                'net': (income or 0) - (expense or 0)
            }
        
        return result
    
    def get_largest_transactions(self, limit=10):
        """Get largest transactions"""
        conn = sqlite3.connect(self.db_path)
        
        rows = conn.execute('''
            SELECT timestamp, amount, content, bank_name, transaction_type
            FROM transactions
            ORDER BY amount DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        
        return [{
            'time': row[0],
            'amount': row[1],
            'content': row[2],
            'bank': row[3],
            'type': row[4]
        } for row in rows]
    
    def get_stats(self, days=30):
        """Get statistical analysis"""
        conn = sqlite3.connect(self.db_path)
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # All transactions
        all_txns = conn.execute('''
            SELECT amount FROM transactions
            WHERE timestamp >= ?
        ''', (cutoff_date,)).fetchall()
        
        amounts = [row[0] for row in all_txns]
        
        if not amounts:
            conn.close()
            return None
        
        amounts_sorted = sorted(amounts)
        avg = sum(amounts) / len(amounts)
        median = amounts_sorted[len(amounts) // 2]
        min_txn = min(amounts)
        max_txn = max(amounts)
        
        conn.close()
        
        return {
            'count': len(amounts),
            'average': avg,
            'median': median,
            'min': min_txn,
            'max': max_txn,
            'total': sum(amounts)
        }
    
    def generate_report(self, days=30):
        """Generate comprehensive report"""
        summary = self.get_summary(days)
        by_category = self.get_by_category(days)
        daily = self.get_daily_breakdown(days)
        largest = self.get_largest_transactions(5)
        stats = self.get_stats(days)
        
        report = f"""
╔═══════════════════════════════════════════════╗
║         💰 FINANCIAL REPORT 💰               ║
║         Last {days} days                      ║
╚═══════════════════════════════════════════════╝

📊 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 Total Income:      {summary['total_income']:>15,.0f} VND
📤 Total Expense:     {summary['total_expense']:>15,.0f} VND
💵 Net Cash Flow:     {summary['net']:>15,.0f} VND
📈 Transaction Count: {summary['transaction_count']:>15} transactions
📊 Avg Transaction:   {summary['avg_transaction']:>15,.0f} VND

📈 BY CATEGORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for category, data in sorted(by_category.items(), key=lambda x: x[1]['amount'], reverse=True):
            report += f"{category:30} {data['count']:>3}x {data['amount']:>12,.0f} VND\n"
        
        if stats:
            report += f"""
📊 STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average:              {stats['average']:>15,.0f} VND
Median:               {stats['median']:>15,.0f} VND
Min Transaction:      {stats['min']:>15,.0f} VND
Max Transaction:      {stats['max']:>15,.0f} VND
"""
        
        report += f"""
🏆 TOP 5 LARGEST TRANSACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for i, txn in enumerate(largest, 1):
            report += f"{i}. {txn['type']:>4} | {txn['amount']:>12,.0f} | {txn['content'][:40]}\n"
        
        report += f"""
📅 DAILY BREAKDOWN (Last 10 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for date, values in sorted(daily.items(), reverse=True)[:10]:
            report += f"{date} | IN: {values['income']:>10,.0f} | OUT: {values['expense']:>10,.0f} | NET: {values['net']:>10,.0f}\n"
        
        return report

def main():
    """Main entry point"""
    import sys
    
    analyzer = TransactionAnalyzer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        
        if command == 'summary':
            data = analyzer.get_summary(days)
            print(json.dumps(data, indent=2))
        
        elif command == 'category':
            data = analyzer.get_by_category(days)
            print(json.dumps(data, indent=2))
        
        elif command == 'daily':
            data = analyzer.get_daily_breakdown(days)
            print(json.dumps(data, indent=2))
        
        elif command == 'largest':
            data = analyzer.get_largest_transactions(days)
            print(json.dumps(data, indent=2))
        
        elif command == 'stats':
            data = analyzer.get_stats(days)
            print(json.dumps(data, indent=2))
        
        elif command == 'report':
            report = analyzer.generate_report(days)
            print(report)
        
        else:
            print("Unknown command")
    else:
        # Default: print full report
        report = analyzer.generate_report(30)
        print(report)

if __name__ == "__main__":
    main()
