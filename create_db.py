import sqlite3

# Connect to (or create) a database file called "exposure.db"
# If the file doesn't exist yet, SQLite creates it automatically.
conn = sqlite3.connect("exposure.db")

# A "cursor" is what lets us actually run SQL commands through Python
cursor = conn.cursor()

# Create the table (only runs if it doesn't already exist)
cursor.execute("""
CREATE TABLE IF NOT EXISTS exposure (
    id INTEGER PRIMARY KEY,
    region TEXT,
    counterparty TEXT,
    asset_class TEXT,
    exposure_amount REAL,
    currency TEXT,
    report_date TEXT
)
""")
# Check how many rows already exist before inserting anything.
# This makes the script "idempotent" — safe to run any number of times
# without creating duplicates.
cursor.execute("SELECT COUNT(*) FROM exposure")
row_count = cursor.fetchone()[0]
print("Row count is ",row_count)
if row_count == 0:
    sample_data = [
        ("APAC", "Tokyo Capital Partners", "Equity", 12500000, "USD", "2026-06-30"),
        ("APAC", "Singapore Holdings", "Bond", 8300000, "USD", "2026-06-30"),
        ("APAC", "HK Trading Co", "FX", 15750000, "USD", "2026-06-30"),
        ("EMEA", "London Finance Ltd", "Equity", 9800000, "USD", "2026-06-30"),
        ("EMEA", "Frankfurt Bank AG", "Bond", 22000000, "USD", "2026-06-30"),
        ("NA", "New York Capital", "Equity", 18500000, "USD", "2026-06-30"),
        ("NA", "Toronto Investments", "FX", 6200000, "USD", "2026-06-30"),
        ("APAC", "Sydney Asset Mgmt", "Bond", 11200000, "USD", "2026-06-30"),
    ]

    cursor.executemany("""
    INSERT INTO exposure (region, counterparty, asset_class, exposure_amount, currency, report_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, sample_data)

    conn.commit()
    print("Database created successfully with", len(sample_data), "rows.")
else:
    print(f"Database already has {row_count} rows — skipping insert to avoid duplicates.")