import sqlite3

conn = sqlite3.connect("superstore.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sales")
print("Total rows:", cursor.fetchone()[0])
conn.close()