"""Command-line orchestration for the web-scraping ETL pipeline."""
from __future__ import annotations
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
import schedule
import time

from src.extract import extract_books
from src.transform import transform_books
from src.quality import run_quality_checks
from src.load import load_csv, load_postgres

ROOT = Path(__file__).resolve().parents[1]

def configure_logging() -> None:
    log_dir = ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8"), logging.StreamHandler()],
        force=True,
    )

def run_pipeline(pages: int = 2) -> dict:
    configure_logging()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.info("ETL run %s started", run_id)
    raw = extract_books(pages=pages)
    clean = transform_books(raw)
    quality = run_quality_checks(clean)
    data_dir = ROOT / "data"
    report_dir = ROOT / "reports"
    data_path = data_dir / f"books_{run_id}.csv"
    report_path = report_dir / f"quality_{run_id}.json"
    load_csv(clean, data_path)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(quality, indent=2), encoding="utf-8")
    postgres_loaded = False
    if quality["overall_pass"]:
        postgres_loaded = load_postgres(clean)
    else:
        logging.error("Quality checks failed; skipping PostgreSQL load.")
    summary = {"run_id": run_id, "rows": len(clean), "quality_report": str(report_path), "csv_output": str(data_path),
               "postgres_loaded": postgres_loaded, "quality": quality}
    logging.info("ETL summary: %s", json.dumps(summary))
    if not quality["overall_pass"]:
        raise RuntimeError(f"Data quality checks failed. Review {report_path}")
    return summary

def main() -> None:
    parser = argparse.ArgumentParser(description="Books to Scrape ETL pipeline")
    parser.add_argument("--pages", type=int, default=2, help="Number of catalogue pages to scrape (default: 2)")
    parser.add_argument("--schedule", action="store_true", help="Run repeatedly on a daily interval")
    parser.add_argument("--interval-minutes", type=int, default=1440, help="Interval for scheduled mode (default: 1440)")
    args = parser.parse_args()
    if not args.schedule:
        summary = run_pipeline(args.pages)
        print(json.dumps(summary, indent=2))
        return
    if args.interval_minutes < 1:
        parser.error("--interval-minutes must be >= 1")
    configure_logging()
    logging.info("Scheduler started; interval=%s minutes", args.interval_minutes)
    schedule.every(args.interval_minutes).minutes.do(run_pipeline, pages=args.pages)
    run_pipeline(args.pages)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
