import os
from dotenv import load_dotenv
from google import genai
import sqlite3
import pandas as pd

# Reads the .env file and loads GEMINI_API_KEY into the environment
load_dotenv()

# Create a client that talks to Gemini, authenticated with your key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# This describes our table structure in plain text — the AI reads this
# to know what columns exist and how to reference them correctly.
SCHEMA = """
Table: exposure
Columns:
- id (INTEGER)
- region (TEXT) -- values like 'APAC', 'EMEA', 'NA'
- counterparty (TEXT)
- asset_class (TEXT) -- values like 'Equity', 'Bond', 'FX'
- exposure_amount (REAL) -- dollar amount
- currency (TEXT)
- report_date (TEXT) -- format YYYY-MM-DD
"""

def get_sql_from_question(question: str) -> str:
    # This is the "prompt" — the full set of instructions we send the AI.
    # Being explicit about format avoids messy output we can't parse.
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

    # Gemini sometimes wraps answers in ```sql ... ``` even when told not to —
    # this cleans that up just in case, so our code doesn't break.
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql


def run_query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect("exposure.db")
    # pandas can run a SQL query directly against a database connection
    # and hand back a nicely formatted table (DataFrame)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


if __name__ == "__main__":
    question = "Show total exposure above $10M in APAC"

    print("Question:", question)

    sql = get_sql_from_question(question)
    print("\nGenerated SQL:\n", sql)

    results = run_query(sql)
    print("\nResults:\n", results)