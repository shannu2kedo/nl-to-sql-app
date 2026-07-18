import pandas as pd

url = "https://raw.githubusercontent.com/yannie28/Global-Superstore/master/Global_Superstore%28CSV%29.csv"

# encoding='latin1' matters here — this specific file isn't standard UTF-8
# text encoding (common with older/international datasets). Without this,
# pandas would throw an error trying to read certain special characters.
df = pd.read_csv(url, encoding="latin1")

print("Shape (rows, columns):", df.shape)
print("\nColumn names:\n", df.columns.tolist())
print("\nMissing values per column:\n", df.isna().sum())
print("\nFirst 3 rows:\n", df.head(3))