import pandas as pd

df = pd.read_csv("raw_books.csv")

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df['price_gbp'] = pd.to_numeric(df['price'].str.replace(r"[^\d.]", "", regex=True), errors="coerce")
df['price_gbp'] = df['price_gbp'].fillna(df['price_gbp'].median())
df['price_inr'] = df['price_gbp']*105.50
df['rating'] = df['star_rating'].map(rating_map)
df['rating'] = df['rating'].fillna(df['rating'].median()).round().astype(int)
df['in_stock'] = df['availability'].str.contains("In stock", case=False, na=False)

print(df.head())
print(df.dtypes)

print("Missing Values:")
print(df[["price_gbp", "rating", "price_inr", "in_stock"]].isna().sum())

print("Rating Values:")
print(sorted(df["rating"].unique()))

print("Stock Values:")
print(df['in_stock'].unique())

df.to_csv("cleaned_books.csv", index=False)
print("Saved cleaned_books.csv")