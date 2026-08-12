import sqlite3
import pandas as pd

df = pd.read_csv("cleaned_books.csv")

conn = sqlite3.connect("zepto_books.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS books")
cursor.execute("DROP TABLE IF EXISTS categories")

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock INTEGER,
    category_id INTEGER REFERENCES categories(category_id)
);
""")

for cat in df['category'].unique():
    cursor.execute("INSERT INTO categories (category_name) VALUES (?)", (cat,))

cursor.execute("SELECT category_id, category_name FROM categories")
category_map = {
    name: cid
    for cid, name in cursor.fetchall()
}

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row['title'],
        row['price_gbp'],
        row['price_inr'],
        row['rating'],
        int(row['in_stock']),
        category_map[row['category']],
    ))

conn.commit()
print(f"Loaded {len(df)} books across {len(category_map)} categories into zepto_books.db")
conn.close()