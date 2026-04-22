import sqlite3
from config import settings

conn = sqlite3.connect(settings.db_path)
c = conn.cursor()

print("Migrating Company.db...")

# Check and add columns to leads
lead_cols = [row[1] for row in c.execute("PRAGMA table_info(leads)").fetchall()]
new_columns = {
    "last_contacted": "DATETIME DEFAULT CURRENT_TIMESTAMP",
    "last_replied": "DATETIME",
    "followup_count": "INTEGER DEFAULT 0",
    "thread_id": "TEXT",
    "ai_score": "JSON",
    "classification": "TEXT"
}

for col, col_type in new_columns.items():
    if col not in lead_cols:
        c.execute(f"ALTER TABLE leads ADD COLUMN {col} {col_type}")
        print(f"Added {col} to leads")

# Check and add to messages if needed
msg_cols = [row[1] for row in c.execute("PRAGMA table_info(messages)").fetchall()]
if "direction" not in msg_cols:
    c.execute("ALTER TABLE messages ADD COLUMN direction TEXT DEFAULT 'sent'")
    print("Added direction to messages")

conn.commit()
conn.close()
print("Migration complete. Run: python migrate_db.py")

