# Zepto Books Catalogue — Data Pipeline

A small pipeline that scrapes book data from books.toscrape.com, cleans it
up, loads it into a SQLite database, and runs SQL + pandas queries on it.
Built as Module 1 of a multi-module data engineering course project.

## What's in this folder

| File | What it does |
|---|---|
| `scrapper.py` | Scrapes books from books.toscrape.com and saves `raw_books.csv` |
| `clean.py` | Cleans the raw CSV, converts price to INR, saves `cleaned_books.csv` |
| `build_database.py` | Creates the SQLite schema and loads the cleaned data into `zepto_books.db` |
| `run_queries.py` | Runs the 5 SQL queries and the pandas cross-check, saves output to `query_results.txt` |
| `raw_books.csv` | Raw scraped data (250 rows) |
| `cleaned_books.csv` | Cleaned data after processing |
| `zepto_books.db` | Final SQLite database |
| `query_results.txt` | Output of all 5 SQL queries + the pandas verification |

## How to run it (in order)

1. **Install requirements**

   ```bash
   pip install requests beautifulsoup4 pandas
   ```

2. **Scrape the data**

   ```bash
   python scrapper.py
   ```

   Pulls books from three categories — Sequential Art, Fiction, and
   Nonfiction — chosen for size, since together they clear the 60-book
   minimum many times over. Writes `raw_books.csv` (250 rows).

3. **Clean the data**

   ```bash
   python clean.py
   ```

   Reads `raw_books.csv`, types and cleans every field, and writes
   `cleaned_books.csv`.

4. **Build the database and load the data**

   ```bash
   python build_database.py
   ```

   Creates `zepto_books.db` with the `categories`/`books` schema, then
   loads `cleaned_books.csv` straight into it.

5. **Run the queries + pandas cross-check**

   ```bash
   python run_queries.py > query_results.txt
   ```

   Runs all 5 required queries and prints each result, then reproduces
   the join query with `pd.merge` on in-memory DataFrames and checks it
   matches the SQL result exactly.

## Cleaning decisions (in `clean.py`)

- **Price**: currency symbol stripped with a regex (`[^\d.]`, i.e. drop
  anything that isn't a digit or a decimal point), then converted with
  `pd.to_numeric(errors="coerce")` so an unparseable price becomes `NaN`
  instead of crashing the script.
- **Rating**: the word rating (One–Five) is mapped to an integer via a
  dict; anything not in the dict becomes `NaN` automatically.
- **Availability**: converted to a plain `True`/`False` with
  `.str.contains("In stock", case=False, na=False)`.
- **Missing price / rating**: filled in with the **median** of that
  column rather than dropped, so one bad numeric field doesn't throw
  away a row's otherwise-valid title and category. Imputation happens
  before `price_inr` is calculated, so the INR conversion always uses
  the final (possibly imputed) price, never the raw `NaN`.
- **Encoding**: `resp.encoding` is set to `"utf-8"` explicitly during
  scraping, since books.toscrape.com doesn't declare it in response
  headers — without this, `£` decodes as the two-character `Â£`.
- **Currency conversion**: GBP to INR at a fixed rate of 105.50
  (`price_inr = price_gbp * 105.50`), as specified for this project —
  not a live or historical rate.
- In this run, all 250 scraped books passed cleaning with valid prices
  and ratings, so the median-impute path isn't actually exercised by
  the current dataset — the columns are typed correctly either way.

## Database design (`build_database.py`)

Two tables, normalized so category names aren't repeated on every book row:

- `categories(category_id, category_name)`
- `books(book_id, title, price_gbp, price_inr, rating, in_stock, category_id)`
  with `category_id` as a foreign key into `categories`.

`in_stock` is stored as `0`/`1` (SQLite has no real boolean type).

## Queries (`run_queries.py`)

1. **Q1** — top 10 priciest books rated 4+ stars (`SELECT` / `WHERE` /
   `ORDER BY` / `LIMIT`)
2. **Q2** — distinct category names (`DISTINCT`)
3. **Q3** — books priced between £20 and £40 (`BETWEEN`)
4. **Q4** — books rated 4 or 5 (`IN`)
5. **Q5** — 5-star books by category, priciest first, joined against
   `categories` (`JOIN`) — also reproduced with `pd.merge` on in-memory
   DataFrames with no SQL involved, and checked to match exactly.

## Notes

- Q5's results are all "Fiction" — that's correct, not a bug. The sort
  is category name first, then price, and Fiction alone has more than
  15 five-star books, so it fills the whole `LIMIT` before the ordering
  ever reaches the other two categories.
