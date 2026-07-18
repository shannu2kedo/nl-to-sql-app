import sqlite3
import pandas as pd

url = "https://raw.githubusercontent.com/yannie28/Global-Superstore/master/Global_Superstore%28CSV%29.csv"

df = pd.read_csv(url, encoding="latin1")

# --- CLEANING STEP 1: Fix the date column ---
# Right now 'Order Date' is just text like "11/11/2014" — pandas has no
# idea it's a date. pd.to_datetime() parses it into a real date type,
# which lets us sort/filter/compare it properly later.
# format="%m/%d/%Y" tells pandas exactly how to read it (month/day/year) —
# without this, pandas sometimes guesses wrong (e.g. mixing up day/month).
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")

# Convert it to a clean YYYY-MM-DD text format for storing in SQLite
# (SQLite doesn't have a real date type — text in this format sorts
# correctly and is what our AI prompt will expect, matching our old schema)
df["Order Date"] = df["Order Date"].dt.strftime("%Y-%m-%d")

# --- CLEANING STEP 2: Keep only the columns we actually need ---
# Real datasets often have far more columns than you need. Keeping only
# what's relevant makes the AI's job easier (smaller schema = fewer mistakes)
# and makes the table easier to reason about.
df = df[[
    "Order ID", "Order Date", "Customer Name", "Country",
    "Market", "Region", "Category", "Sub-Category",
    "Product Name", "Sales", "Quantity", "Discount", "Profit"
]]

# --- CLEANING STEP 3: Rename columns to clean, consistent names ---
# Column names with spaces/dashes are technically usable in SQL but a pain
# to type correctly every time. Renaming to snake_case (lowercase_with_underscores)
# is standard practice and keeps things predictable for the AI too.
df = df.rename(columns={
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Customer Name": "customer_name",
    "Country": "country",
    "Market": "region",       # broad grouping — USCA, Asia Pacific, Europe, etc.
    "Region": "sub_region",   # finer detail — Central US, Oceania, etc.
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales_amount",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
})

print("Cleaned data preview:")
print(df.head(3))
print("\nFinal shape:", df.shape)

# --- LOAD INTO SQLITE ---
conn = sqlite3.connect("superstore.db")

# df.to_sql() does in ONE line what took us a whole executemany() block
# before — it creates the table (matching column types automatically)
# AND inserts all rows.
# if_exists="replace" means: if this table already exists, drop it and
# rebuild fresh — this is what solves our earlier duplicate-row problem
# permanently, since re-running this script can never create duplicates.
df.to_sql("sales", conn, if_exists="replace", index=False)

conn.close()
print("\nLoaded into superstore.db, table 'sales'.")