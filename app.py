import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
import sqlite3
import pandas as pd

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCHEMA = SCHEMA = """
Table: sales
Columns:
- order_id (TEXT)
- order_date (TEXT) -- format YYYY-MM-DD
- customer_name (TEXT)
- country (TEXT)
- region (TEXT) -- broad market: 'USCA', 'Asia Pacific', 'Europe', 'Africa', 'LATAM'
- sub_region (TEXT) -- finer detail: 'Central US', 'Oceania', 'Western Europe', etc.
- category (TEXT) -- 'Technology', 'Furniture', 'Office Supplies'
- sub_category (TEXT)
- product_name (TEXT)
- sales_amount (REAL)
- quantity (INTEGER)
- discount (REAL) -- decimal, e.g. 0.1 = 10% discount
- profit (REAL) -- can be negative (a loss on that sale)
"""

def get_sql_from_question(question: str) -> str:
    prompt = f"""You are a SQL expert. Given this database schema:

{SCHEMA}

Convert the following question into a single valid SQLite SQL query.
Return ONLY the raw SQL query. No explanations, no markdown, no code fences.

Question: {question}
"""
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    sql = response.text.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def run_query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect("superstore.db")   # was "exposure.db"
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


# ---- Everything below this line is the actual visible web page ----

st.set_page_config(page_title="NL to SQL", page_icon="🔍")

st.title("🔍 Natural Language to SQL")
st.write("Ask a question about exposure data in plain English.")

# A text input box — Streamlit auto-refreshes the page whenever this changes
question = st.text_input("Your question:", placeholder="e.g. Total sales by region for Technology products")

# Only run everything below if there's actually a question typed in
if question:
    # A spinner shows a little loading animation while Gemini responds
    with st.spinner("Thinking..."):
        try:
            sql = get_sql_from_question(question)
            results = run_query(sql)

            st.subheader("Generated SQL")
            # st.code renders it in a nice monospace/highlighted box
            st.code(sql, language="sql")

            st.subheader("Results")
            st.dataframe(results)

        except Exception as e:
            # Catching errors here means a bad question shows a friendly
            # message instead of crashing the whole app
            st.error(f"Something went wrong: {e}")