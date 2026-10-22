"""Load transformed records to CSV and optionally PostgreSQL."""
from __future__ import annotations
import os
import logging
from pathlib import Path
import pandas as pd

def load_csv(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logging.info("Wrote CSV output: %s", output_path)

def load_postgres(df: pd.DataFrame) -> bool:
    """Upsert rows into PostgreSQL if DATABASE_URL is set; otherwise skip."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logging.info("DATABASE_URL not set; skipping PostgreSQL load.")
        return False
    if df.empty:
        logging.info("No rows to load into PostgreSQL.")
        return True
    import psycopg
    from psycopg.rows import dict_row
    sql_create = """
    CREATE TABLE IF NOT EXISTS scraped_books (
        title TEXT NOT NULL,
        price_gbp NUMERIC(10,2),
        availability TEXT,
        rating SMALLINT,
        product_url TEXT PRIMARY KEY,
        source_page INTEGER,
        extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    sql_upsert = """
    INSERT INTO scraped_books (title, price_gbp, availability, rating, product_url, source_page)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (product_url) DO UPDATE SET
      title = EXCLUDED.title,
      price_gbp = EXCLUDED.price_gbp,
      availability = EXCLUDED.availability,
      rating = EXCLUDED.rating,
      source_page = EXCLUDED.source_page,
      extracted_at = NOW();
    """
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_create)
            for row in df.itertuples(index=False, name=None):
                title, price, availability, rating, url, source_page = row
                cur.execute(sql_upsert, (
                    None if pd.isna(title) else str(title),
                    None if pd.isna(price) else float(price),
                    None if pd.isna(availability) else str(availability),
                    None if pd.isna(rating) else int(rating),
                    None if pd.isna(url) else str(url),
                    None if pd.isna(source_page) else int(source_page),
                ))
    logging.info("Upserted %s rows into PostgreSQL", len(df))
    return True
