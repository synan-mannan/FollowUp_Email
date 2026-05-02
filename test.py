import pandas as pd
import sqlite3


# df = pd.read_json("C:/Users/syedm/Synelime/coirei/FollowUp_Email/LeadResponse/leadsData.json")

# dataList = df.get("data")
conn = sqlite3.connect("C:/Users/syedm/Synelime/coirei/FollowUp_Email/Company.db")
cursor = conn.cursor()

# cursor.execute("SELECT * FROM companies")

# rows = cursor.fetchall()

# for row in rows:
#     print(row)

# conn.close()

# Enable FK support
# cursor.execute("PRAGMA foreign_keys = ON;")

# try:
#     conn.execute("BEGIN")

#     # 1. Drop tables (order matters because of FK)
#     cursor.execute("DROP TABLE IF EXISTS messages;")
#     cursor.execute("DROP TABLE IF EXISTS leads;")

#     # 2. Recreate leads table with FK → companies
#     cursor.execute("""
#     CREATE TABLE leads (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT,
#         phone TEXT,
#         email TEXT,
#         requirement TEXT,
#         status TEXT,
#         score INTEGER,
#         lead_type TEXT,
#         last_contacted DATETIME,
#         last_replied DATETIME,
#         followup_count INTEGER,
#         thread_id TEXT,
#         ai_score TEXT,
#         classification TEXT,
#         company_id INTEGER,
#         created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
#         FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL
#     );
#     """)

#     # 3. Recreate messages table with FK → leads
#     cursor.execute("""
#     CREATE TABLE messages (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         lead_id INTEGER,
#         message TEXT,
#         direction TEXT,
#         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#         FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
#     );
#     """)

#     conn.commit()
#     print("✅ Tables recreated successfully with foreign keys!")

# except Exception as e:
#     conn.rollback()
#     print("❌ Error:", e)

# finally:
#     conn.close()

# Get all table names
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# for table in tables:
#     table_name = table[0]
#     print(f"\nTable: {table_name}")
#     print("-" * 40)

#     # Get column names
#     cursor.execute(f"PRAGMA table_info({table_name});")
#     columns = [col[1] for col in cursor.fetchall()]
#     print("Columns:", columns)

#     # Get all data
#     cursor.execute(f"SELECT * FROM {table_name};")
#     rows = cursor.fetchall()

#     if rows:
#         for row in rows:
#             print(row)
#     else:
#         print("No data found.")

# conn.close()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS companies (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     company_name TEXT NOT NULL,
#     industry TEXT,
#     services TEXT,
#     intro_message TEXT,
#     qualification_questions TEXT,
#     pricing_notes TEXT,
#     preferred_channel TEXT CHECK(preferred_channel IN ('email', 'whatsapp', 'call')),
#     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
# );
# """)

# conn.commit()
# conn.close()


cursor.execute("DELETE FROM companies;")

conn.commit()
conn.close()