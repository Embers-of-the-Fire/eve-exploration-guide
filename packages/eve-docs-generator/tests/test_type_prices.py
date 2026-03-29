from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from eve_docs_generator.type_prices import (
    TypePriceRef,
    generate_type_price_data_async,
    load_type_price_refs,
    normalize_price_entry,
    parse_stat,
    render_type_price_output,
)


class LoadTypePriceRefsTests(unittest.TestCase):
    def test_ignores_invalid_entries_and_sorts_unique_refs(self):
        with TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "eve-type-prices.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "refs": [
                            {"regionId": 10000043, "typeId": 34},
                            {"regionId": 10000002, "typeId": 28665},
                            {"regionId": 10000002, "typeId": 28665},
                            {"regionId": "bad", "typeId": 123},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            refs = load_type_price_refs(manifest_path)

        self.assertEqual(
            refs,
            [
                TypePriceRef(region_id=10000002, type_id=28665),
                TypePriceRef(region_id=10000043, type_id=34),
            ],
        )


class ParseStatTests(unittest.TestCase):
    def test_rejects_non_finite_numbers_and_bools(self):
        self.assertIsNone(parse_stat(True))
        self.assertIsNone(parse_stat(float("inf")))
        self.assertIsNone(parse_stat(float("nan")))
        self.assertIsNone(parse_stat("100"))

    def test_keeps_finite_numeric_values(self):
        self.assertEqual(parse_stat(100), 100)
        self.assertEqual(parse_stat(12.5), 12.5)


class NormalizePriceEntryTests(unittest.TestCase):
    def test_returns_empty_entry_for_non_mapping_payload(self):
        self.assertEqual(
            normalize_price_entry(["bad"]),
            {
                "buyAvgFivePercent": None,
                "buyOrders": None,
                "buyOutliers": None,
                "buyThreshold": None,
                "buyVolume": None,
                "sellAvgFivePercent": None,
                "sellOrders": None,
                "sellOutliers": None,
                "sellThreshold": None,
                "sellVolume": None,
            },
        )


class RenderTypePriceOutputTests(unittest.TestCase):
    def test_renders_typescript_module(self):
        rendered = render_type_price_output(
            generated_at="2026-03-29T01:23:45+00:00",
            prices={
                "10000002:28665": {"buyAvgFivePercent": 1, "sellAvgFivePercent": 2}
            },
        )

        self.assertIn("export interface EveTypePriceDataEntry", rendered)
        self.assertIn('"2026-03-29T01:23:45+00:00"', rendered)
        self.assertIn('"10000002:28665"', rendered)


class GenerateTypePriceDataAsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_writes_empty_entries_when_fetch_fails(self):
        with TemporaryDirectory() as tmp_dir:
            manifest_path = Path(tmp_dir) / "eve-type-prices.json"
            output_path = Path(tmp_dir) / "type-price-data.ts"
            manifest_path.write_text(
                json.dumps({"refs": [{"regionId": 10000002, "typeId": 28665}]}),
                encoding="utf-8",
            )

            async def failing_fetch(**kwargs):
                del kwargs
                return {
                    "buyAvgFivePercent": None,
                    "buyOrders": None,
                    "buyOutliers": None,
                    "buyThreshold": None,
                    "buyVolume": None,
                    "sellAvgFivePercent": None,
                    "sellOrders": None,
                    "sellOutliers": None,
                    "sellThreshold": None,
                    "sellVolume": None,
                }

            with patch(
                "eve_docs_generator.type_prices.fetch_type_price_entry",
                side_effect=failing_fetch,
            ):
                summary = await generate_type_price_data_async(
                    manifest_path=manifest_path,
                    output_path=output_path,
                )

            rendered = output_path.read_text(encoding="utf-8")

        self.assertEqual(summary.ref_count, 1)
        self.assertIsNotNone(summary.generated_at)
        self.assertIn('"10000002:28665"', rendered)
        self.assertIn('"buyAvgFivePercent": null', rendered)
