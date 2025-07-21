# database.py (Final Cleaned Version)
import sqlite3
from typing import List, Dict, Any
from receiptparserapp.models import Receipt

DB_NAME = "receipts.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, vendor TEXT, transaction_date DATE,
            amount REAL, category TEXT, raw_text TEXT NOT NULL,
            currency TEXT DEFAULT 'USD'
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vendor ON receipts (vendor);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON receipts (transaction_date);")
    conn.commit()
    conn.close()

def insert_receipt(receipt: Receipt):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO receipts (vendor, transaction_date, amount, category, raw_text, currency) VALUES (?, ?, ?, ?, ?,?)",
        (receipt.vendor, receipt.transaction_date, receipt.amount, receipt.category, receipt.raw_text, receipt.currency)
    )
    conn.commit()
    conn.close()

def get_all_receipts() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, vendor, transaction_date, amount, category, currency FROM receipts ORDER BY id DESC")
    receipts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return receipts

def update_receipt(receipt_id: int, updates: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
    values = list(updates.values())
    values.append(receipt_id)
    query = f"UPDATE receipts SET {set_clause} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def delete_receipts_by_ids(ids: List[int]):
    if not ids: return
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ', '.join('?' for _ in ids)
    query = f"DELETE FROM receipts WHERE id IN ({placeholders})"
    cursor.execute(query, ids)
    conn.commit()
    conn.close()

def delete_all_receipts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM receipts")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='receipts';")
    conn.commit()
    conn.close()