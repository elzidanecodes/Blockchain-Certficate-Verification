import sqlite3
import json

DB_PATH = "logs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS certificates
                      (certificate_id TEXT PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()

def save_to_sqlite(certificate_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO certificates (certificate_id, data) VALUES (?, ?)",
                   (certificate_data['certificate_id'], json.dumps(certificate_data)))
    conn.commit()
    conn.close()

# Inisialisasi database saat pertama kali dijalankan
init_db()
