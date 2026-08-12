# Module 1 — Data Pipeline

## Overview
Scrapes book listings from books.toscrape.com, cleans and types the fields,
converts GBP to INR at a fixed rate, and loads everything into a normalized
SQLite database. SQL and pandas are used interchangeably to query the result.

## Data source
books.toscrape.com, 3 categories: Sequential Art, Fiction, Nonfiction —
chosen for size, comfortably clearing the 60-book minimum. 250 books total.

## Install & run
```bash
pip install requests beautifulsoup4 pandas
python scrapper.py                        # scrapes -> raw_books.csv
python clean.py                           # cleans  -> cleaned_books.csv
python build_database.py                  # loads   -> zepto_books.db
python run_queries.py > query_results.txt # 5 required queries + pandas verification
```

## Design decisions
- **Currency conversion**: fixed rate of 1 GBP = 105.50 INR, as specified — no live lookup, no date reference.
- **Malformed rows**: numeric fields (`price_gbp`, `rating`) that fail to parse are median-imputed rather than dropped, so one bad field doesn't discard an otherwise-valid row's title/category. Implemented via `pd.to_numeric(errors="coerce")` + `.fillna(median)`. Books.toscrape.com's data is clean, so this path isn't exercised by the current dataset — the columns are typed correctly regardless.
- **Encoding**: `resp.encoding = "utf-8"` is set explicitly on every scrape request, since the site doesn't declare it in response headers and `requests` would otherwise mis-decode the £ symbol.
- **Schema**: two tables, `categories` (PK `category_id`) and `books` (PK `book_id`, FK `category_id`).

## Files
| File | Purpose |
|---|---|
| `scrapper.py` | Scrapes books.toscrape.com into `raw_books.csv` |
| `clean.py` | Types/cleans fields, converts currency, into `cleaned_books.csv` |
| `build_database.py` | Builds `zepto_books.db` from the cleaned CSV |
| `run_queries.py` | Runs the 5 required SQL queries + pandas verification |
| `query_results.txt` | Saved output of `run_queries.py` |
