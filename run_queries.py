import sqlite3
import pandas as pd

conn = sqlite3.connect("zepto_books.db")

queries = {
    "Q1 - top 10 priciest books rated 4+ (SELECT/WHERE/ORDER BY/LIMIT)": """
        SELECT title, price_gbp, rating FROM books
        WHERE rating >= 4
        ORDER BY price_gbp DESC
        LIMIT 10;
    """,
    "Q2 - distinct categories (DISTINCT)": """
        SELECT DISTINCT category_name FROM categories;
    """,
    "Q3 - books priced 20-40 (BETWEEN)": """
        SELECT title, price_gbp FROM books
        WHERE price_gbp BETWEEN 20 AND 40
        ORDER BY price_gbp;
    """,
    "Q4 - books rated 4 or 5 (IN)": """
        SELECT title, rating FROM books
        WHERE rating IN (4, 5)
        ORDER BY rating DESC;
    """,
    "Q5 - 5-star books by category, priciest first (JOIN)": """
        SELECT b.title, b.rating, b.price_inr, c.category_name
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.rating = 5
        ORDER BY c.category_name, b.price_inr DESC
        LIMIT 15;
    """,
}

results = {}
output_file = open("query_results.txt", "w", encoding="utf-8")
for label, sql in queries.items():
    df_result = pd.read_sql(sql, conn)
    results[label] = df_result
    print(f"--- {label} ---")
    print(df_result, "\n")
    output_file.write(f"--- {label} ---\n")
    output_file.write("SQL:\n")
    output_file.write(sql.strip() + "\n\n")
    output_file.write("OUTPUT:\n")
    output_file.write(df_result.to_string(index=False))
    output_file.write("\n\n")

books_df = pd.read_sql("SELECT * FROM books", conn)
categories_df = pd.read_sql("SELECT * FROM categories", conn)

merged = books_df.merge(categories_df, on="category_id")
join_via_pandas = (
    merged[merged["rating"] == 5]
    [["title", "rating", "price_inr", "category_name"]]
    .sort_values(["category_name", "price_inr"], ascending=[True, False])
    .head(15)
    .reset_index(drop=True)
)

join_via_sql = results["Q5 - 5-star books by category, priciest first (JOIN)"].reset_index(drop=True)

print("--- Q5 reproduced via pd.merge (no SQL) ---")
print(join_via_pandas, "\n")
print("SQL result == pandas-merge result:", join_via_sql.equals(join_via_pandas))
output_file.write(" --- Q5 reproduced via pd.merge (no SQL) ---\n")
output_file.write(join_via_pandas.to_string(index=False))
output_file.write("\n\n")

output_file.write(
    "SQL result == pandas-merge result: "
    + str(join_via_sql.equals(join_via_pandas))
    + "\n"
)

output_file.close()

conn.close()