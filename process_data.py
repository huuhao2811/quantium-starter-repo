import pandas as pd

files = [
    "data/daily_sales_data_0.csv",
    "data/daily_sales_data_1.csv",
    "data/daily_sales_data_2.csv"
]

df = pd.concat([pd.read_csv(f) for f in files])

df["price"] = (
    df["price"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)
df["sales"] = df["price"] * df["quantity"]


pink = df[df["product"] == "pink morsel"].copy()

pink["date"] = pd.to_datetime(pink["date"], errors="coerce")

result = pink.rename(columns={"sales": "Sales", "date": "Date", "region": "Region"})[ ["Sales", "Date", "Region"] ].sort_values(["Date", "Region"], ignore_index=True)

out_path = "data/processed_sales.csv"
result.to_csv(out_path, index=False)
