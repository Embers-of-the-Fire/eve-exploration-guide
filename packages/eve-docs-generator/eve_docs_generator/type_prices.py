from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import aiohttp
from dotenv import find_dotenv, load_dotenv

from .generator import REPO_ROOT, resolve_cli_path
from .source_workspace import (
    resolve_download_proxy_url,
    should_skip_download_ssl_verification,
)

DEFAULT_TYPE_PRICE_MANIFEST_PATH = REPO_ROOT / "src/generated/eve-type-prices.json"
DEFAULT_TYPE_PRICE_OUTPUT_PATH = REPO_ROOT / "src/generated/eve/type-price-data.ts"
DEFAULT_MARKET_STATS_API_BASE_URL = "https://evetycoon.com/api/v1/market/stats"
REQUEST_TIMEOUT_SECONDS = 30
MAX_PARALLEL_REQUESTS = 8


@dataclass(frozen=True, order=True)
class TypePriceRef:
    region_id: int
    type_id: int


@dataclass(frozen=True)
class GeneratedTypePriceSummary:
    output_path: Path
    ref_count: int
    generated_at: str | None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the checked-in EVE market price data file from the "
            "collected EveTypePrice manifest."
        ),
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_TYPE_PRICE_MANIFEST_PATH),
        help="Path to the EveTypePrice reference manifest JSON.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_TYPE_PRICE_OUTPUT_PATH),
        help="Target file for generated market price data.",
    )
    parser.add_argument(
        "--api-base-url",
        default=DEFAULT_MARKET_STATS_API_BASE_URL,
        help=(
            "Base URL for the EveTycoon market stats API "
            f"(default: {DEFAULT_MARKET_STATS_API_BASE_URL})."
        ),
    )
    return parser


def main() -> int:
    load_dotenv(find_dotenv(usecwd=True))
    parser = build_parser()
    args = parser.parse_args()

    summary = generate_type_price_data(
        manifest_path=resolve_cli_path(args.manifest),
        output_path=resolve_cli_path(args.output),
        api_base_url=args.api_base_url,
    )

    if summary.generated_at is None:
        print(f"Generated empty EVE type price data into {summary.output_path}")
    else:
        print(
            "Generated EVE type price data "
            f"for {summary.ref_count} reference(s) into {summary.output_path}"
        )

    return 0


def format_type_price_key(region_id: int, type_id: int) -> str:
    return f"{region_id}:{type_id}"


def parse_stat(value: object) -> int | float | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float) and math.isfinite(value):
        return value

    return None


def empty_price_entry() -> dict[str, int | float | None]:
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


def build_market_stats_url(api_base_url: str, *, region_id: int, type_id: int) -> str:
    return f"{api_base_url.rstrip('/')}/{region_id}/{type_id}"


def coerce_type_price_ref(value: object) -> TypePriceRef | None:
    if not isinstance(value, dict):
        return None

    region_id = value.get("regionId")
    type_id = value.get("typeId")

    if isinstance(region_id, bool) or not isinstance(region_id, int):
        return None

    if isinstance(type_id, bool) or not isinstance(type_id, int):
        return None

    return TypePriceRef(region_id=region_id, type_id=type_id)


def load_type_price_refs(manifest_path: Path) -> list[TypePriceRef]:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []

    refs_payload = payload.get("refs", [])
    if not isinstance(refs_payload, list):
        raise TypeError("Expected 'refs' to be a list in the type price manifest")

    refs = {
        ref
        for raw_ref in refs_payload
        if (ref := coerce_type_price_ref(raw_ref)) is not None
    }

    return sorted(refs)


def render_type_price_output(
    *,
    generated_at: str | None,
    prices: dict[str, dict[str, int | float | None]],
) -> str:
    return (
        "export interface EveTypePriceDataEntry {\n"
        "    buyAvgFivePercent: number | null;\n"
        "    buyOrders: number | null;\n"
        "    buyOutliers: number | null;\n"
        "    buyThreshold: number | null;\n"
        "    buyVolume: number | null;\n"
        "    sellAvgFivePercent: number | null;\n"
        "    sellOrders: number | null;\n"
        "    sellOutliers: number | null;\n"
        "    sellThreshold: number | null;\n"
        "    sellVolume: number | null;\n"
        "}\n\n"
        f"export const eveTypePriceGeneratedAt: string | null = {json.dumps(generated_at)};\n\n"
        "export const eveTypePrices: Record<string, EveTypePriceDataEntry> = "
        f"{json.dumps(prices, indent=4)};\n"
    )


def generate_type_price_data(
    *,
    manifest_path: Path = DEFAULT_TYPE_PRICE_MANIFEST_PATH,
    output_path: Path = DEFAULT_TYPE_PRICE_OUTPUT_PATH,
    api_base_url: str = DEFAULT_MARKET_STATS_API_BASE_URL,
) -> GeneratedTypePriceSummary:
    return asyncio.run(
        generate_type_price_data_async(
            manifest_path=manifest_path,
            output_path=output_path,
            api_base_url=api_base_url,
        )
    )


async def generate_type_price_data_async(
    *,
    manifest_path: Path = DEFAULT_TYPE_PRICE_MANIFEST_PATH,
    output_path: Path = DEFAULT_TYPE_PRICE_OUTPUT_PATH,
    api_base_url: str = DEFAULT_MARKET_STATS_API_BASE_URL,
) -> GeneratedTypePriceSummary:
    refs = load_type_price_refs(manifest_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not refs:
        output_path.write_text(
            render_type_price_output(generated_at=None, prices={}),
            encoding="utf-8",
        )
        return GeneratedTypePriceSummary(
            output_path=output_path,
            ref_count=0,
            generated_at=None,
        )

    prices = await fetch_type_prices(refs=refs, api_base_url=api_base_url)
    generated_at = datetime.now(timezone.utc).isoformat()
    output_path.write_text(
        render_type_price_output(generated_at=generated_at, prices=prices),
        encoding="utf-8",
    )

    return GeneratedTypePriceSummary(
        output_path=output_path,
        ref_count=len(refs),
        generated_at=generated_at,
    )


async def fetch_type_prices(
    *,
    refs: list[TypePriceRef],
    api_base_url: str,
) -> dict[str, dict[str, int | float | None]]:
    connector = aiohttp.TCPConnector(limit=min(MAX_PARALLEL_REQUESTS, len(refs)))
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
    ordered_prices: dict[str, dict[str, int | float | None]] = {}

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        results = await asyncio.gather(
            *[
                fetch_type_price_entry(
                    session=session,
                    region_id=ref.region_id,
                    type_id=ref.type_id,
                    api_base_url=api_base_url,
                )
                for ref in refs
            ]
        )

    for ref, price_entry in zip(refs, results, strict=True):
        ordered_prices[format_type_price_key(ref.region_id, ref.type_id)] = price_entry

    return ordered_prices


async def fetch_type_price_entry(
    *,
    session: aiohttp.ClientSession,
    region_id: int,
    type_id: int,
    api_base_url: str,
) -> dict[str, int | float | None]:
    request_url = build_market_stats_url(
        api_base_url,
        region_id=region_id,
        type_id=type_id,
    )
    proxy_url = resolve_download_proxy_url(request_url)
    ssl = False if should_skip_download_ssl_verification() else None

    try:
        async with session.get(
            request_url,
            headers={"Accept": "application/json"},
            proxy=proxy_url,
            ssl=ssl,
        ) as response:
            if response.status >= 400:
                raise RuntimeError(
                    f"Unexpected response {response.status} for {region_id}:{type_id}"
                )

            payload = await response.json()
    except (aiohttp.ClientError, asyncio.TimeoutError, OSError, RuntimeError) as error:
        print(
            f"Failed to fetch EveTycoon market stats for {region_id}:{type_id}: {error}",
            file=sys.stderr,
        )
        return empty_price_entry()

    return normalize_price_entry(payload)


def normalize_price_entry(payload: object) -> dict[str, int | float | None]:
    if not isinstance(payload, dict):
        return empty_price_entry()

    return {
        "buyAvgFivePercent": parse_stat(payload.get("buyAvgFivePercent")),
        "buyOrders": parse_stat(payload.get("buyOrders")),
        "buyOutliers": parse_stat(payload.get("buyOutliers")),
        "buyThreshold": parse_stat(payload.get("buyThreshold")),
        "buyVolume": parse_stat(payload.get("buyVolume")),
        "sellAvgFivePercent": parse_stat(payload.get("sellAvgFivePercent")),
        "sellOrders": parse_stat(payload.get("sellOrders")),
        "sellOutliers": parse_stat(payload.get("sellOutliers")),
        "sellThreshold": parse_stat(payload.get("sellThreshold")),
        "sellVolume": parse_stat(payload.get("sellVolume")),
    }


if __name__ == "__main__":
    raise SystemExit(main())
