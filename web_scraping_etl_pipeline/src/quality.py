"""Data-quality checks with a machine-readable JSON report."""
from __future__ import annotations
import pandas as pd

def run_quality_checks(df: pd.DataFrame) -> dict:
    required = ["title", "price_gbp", "product_url"]
    missing_by_column = {col: int(df[col].isna().sum()) for col in required if col in df.columns}
    blank_titles = int(df["title"].fillna("").astype(str).str.strip().eq("").sum()) if "title" in df else len(df)
    duplicate_urls = int(df["product_url"].duplicated().sum()) if "product_url" in df else 0
    invalid_prices = int((df["price_gbp"].isna() | (df["price_gbp"] < 0)).sum()) if "price_gbp" in df else len(df)
    invalid_ratings = int((~df["rating"].isin([1, 2, 3, 4, 5]) & df["rating"].notna()).sum()) if "rating" in df else 0
    checks = {
        "has_rows": len(df) > 0,
        "no_blank_titles": blank_titles == 0,
        "no_duplicate_product_urls": duplicate_urls == 0,
        "all_prices_valid_and_non_negative": invalid_prices == 0,
        "ratings_in_expected_range": invalid_ratings == 0,
    }
    return {
        "row_count": int(len(df)),
        "checks_passed": int(sum(checks.values())),
        "checks_total": len(checks),
        "checks": checks,
        "missing_by_column": missing_by_column,
        "blank_titles": blank_titles,
        "duplicate_product_urls": duplicate_urls,
        "invalid_prices": invalid_prices,
        "invalid_ratings": invalid_ratings,
        "overall_pass": all(checks.values()),
    }
