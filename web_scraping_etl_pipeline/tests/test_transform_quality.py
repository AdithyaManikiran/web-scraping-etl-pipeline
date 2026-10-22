import unittest
import pandas as pd
from src.transform import transform_books
from src.quality import run_quality_checks

class PipelineTests(unittest.TestCase):
    def test_transform_converts_price_and_rating(self):
        df = transform_books([{
            "title": " Example Book ", "price_text": "£12.99", "availability": " In stock ",
            "rating_text": "Four", "product_url": "https://example.test/book", "source_page": 1
        }])
        self.assertEqual(df.loc[0, "title"], "Example Book")
        self.assertAlmostEqual(float(df.loc[0, "price_gbp"]), 12.99)
        self.assertEqual(int(df.loc[0, "rating"]), 4)

    def test_quality_passes_clean_record(self):
        df = transform_books([{
            "title": "Example", "price_text": "£12.99", "availability": "In stock",
            "rating_text": "Four", "product_url": "https://example.test/book", "source_page": 1
        }])
        report = run_quality_checks(df)
        self.assertTrue(report["overall_pass"])

    def test_quality_flags_duplicate_url(self):
        base = {
            "title": "Example", "price_text": "£12.99", "availability": "In stock",
            "rating_text": "Four", "product_url": "https://example.test/book", "source_page": 1
        }
        df = transform_books([base, base])
        report = run_quality_checks(df)
        self.assertEqual(report["duplicate_product_urls"], 1)
        self.assertFalse(report["overall_pass"])

if __name__ == "__main__":
    unittest.main()
