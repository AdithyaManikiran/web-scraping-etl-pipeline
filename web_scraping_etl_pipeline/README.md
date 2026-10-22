# Web Scraping ETL Pipeline (Starter Project)

A small, portfolio-friendly ETL pipeline using **Python, Requests, BeautifulSoup, Pandas, data-quality checks, CSV output, optional PostgreSQL, and scheduled runs**.

> Practice source: https://books.toscrape.com/ — a website intended for web-scraping practice. Do not use this template to scrape sites that prohibit it or to collect personal/sensitive data. Keep requests polite and check the site's terms/robots policy before using any source.

## What it does
1. **Extract:** reads catalogue pages from Books to Scrape.
2. **Transform:** normalizes titles, price, availability, rating and product URL with Pandas.
3. **Quality checks:** checks required fields, duplicates, non-negative prices and valid ratings.
4. **Load:** writes timestamped CSV and quality report; optionally loads records into PostgreSQL when `DATABASE_URL` is set.
5. **Schedule:** supports one-off runs by default and optional interval scheduling.

## Quick start (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.pipeline --pages 2
```

If PowerShell blocks activation, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and then `.\.venv\Scripts\python.exe -m src.pipeline --pages 2`.

## Output
- `data/books_YYYYMMDD_HHMMSS.csv`
- `reports/quality_YYYYMMDD_HHMMSS.json`
- `logs/pipeline.log`

The first run creates these folders automatically.

## Optional PostgreSQL load
1. Create a database and table permissions for a dedicated development user.
2. Set `DATABASE_URL`, for example:
   - PowerShell: `$env:DATABASE_URL="postgresql://username:password@localhost:5432/books_demo"`
   - macOS/Linux: `export DATABASE_URL="postgresql://username:password@localhost:5432/books_demo"`
3. Run `python -m src.pipeline --pages 2`.
4. The pipeline creates `scraped_books` if needed and upserts on `product_url`.

Never commit credentials. Use environment variables and keep `.env` out of Git.

## Optional scheduled mode
Install dependencies, then:
```powershell
python -m src.pipeline --schedule --interval-minutes 1440 --pages 2
```
This keeps the process running and runs once every 24 hours. For a real machine, Windows Task Scheduler or cron is usually more robust; see `docs/scheduling.md`.

## Tests
```powershell
python -m unittest discover -s tests -v
```

## Suggested learning path
- First run without PostgreSQL and inspect the CSV.
- Read `src/extract.py`, then `src/transform.py`, then `src/quality.py`.
- Break one rule intentionally and observe the quality report.
- Add tests for missing title, invalid price, duplicate URL.
- Commit small changes with clear messages.
- Add PostgreSQL only after the CSV flow works.

## Current limitations
- The scraper is intentionally small and uses basic pagination.
- It does not guarantee that the practice site's HTML will never change.
- Scheduled mode is a lightweight demonstration, not a production orchestration platform.
- It uses a simple upsert model; a production pipeline would add retries, metrics, alerting, incremental extraction and a more explicit schema/versioning strategy.
