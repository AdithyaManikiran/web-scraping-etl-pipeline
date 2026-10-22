"""Transform raw scraped records into a normalized Pandas DataFrame."""
from __future__ import annotations
import pandas as pd

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def transform_books(records: list[dict]) -> pd.DataFrame:
    columns = ["title", "price_text", "availability", "rating_text", "product_url", "source_page"]
    df = pd.DataFrame(records, columns=columns)
    if df.empty:
        return pd.DataFrame(columns=["title", "price_gbp", "availability", "rating", "product_url", "source_page"])
    df["title"] = df["title"].astype("string").str.strip()
    df["availability"] = df["availability"].astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    # Practice source currently displays prices with a pound symbol. Remove currency marker safely.
    price_clean = (
    df["price_text"]
    .astype("string")
    .str.replace(",", "", regex=False)
    .str.replace(r"[^\d.\-]", "", regex=True)
    .str.strip()
)

    df["price_gbp"] = pd.to_numeric(price_clean, errors="coerce")
    df["rating"] = df["rating_text"].map(RATING_MAP).astype("Int64")
    df["product_url"] = df["product_url"].astype("string").str.strip()
    df["source_page"] = pd.to_numeric(df["source_page"], errors="coerce").astype("Int64")
    df = df.drop(columns=["price_text", "rating_text"])
    return df[["title", "price_gbp", "availability", "rating", "product_url", "source_page"]]
