#!/usr/bin/env python3
import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search private Amazon purchases CSV for matching products."
    )
    parser.add_argument("query", help="Search term (case-insensitive)")
    parser.add_argument(
        "--full",
        default="data-private/amazon_purchases_full.csv",
        help="Path to full private CSV",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Max rows to display",
    )
    args = parser.parse_args()

    full_path = Path(args.full)
    if not full_path.exists():
        raise SystemExit(f"Missing full dataset: {full_path}")

    df = pd.read_csv(full_path)

    # Normalize columns we use
    if "product_name" not in df.columns or "asin" not in df.columns:
        raise SystemExit("Expected columns 'product_name' and 'asin' in full dataset.")

    q = args.query.strip()
    if not q:
        raise SystemExit("Query must be non-empty.")

    mask = df["product_name"].astype(str).str.contains(q, case=False, na=False)
    matches = df[mask].copy()

    if matches.empty:
        print("No matches.")
        return

    cols = [c for c in ["product_name", "asin", "order_date", "order_id"] if c in matches.columns]
    matches = matches[cols]

    # Show most recent first if possible
    if "order_date" in matches.columns:
        matches = matches.sort_values("order_date", ascending=False)

    print(matches.head(args.limit).to_string(index=False))


if __name__ == "__main__":
    main()
