#!/usr/bin/env python3
import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build public purchases CSV from allow-list + private full dataset."
    )
    parser.add_argument(
        "--full",
        default="data-private/amazon_purchases_full.csv",
        help="Path to full private CSV",
    )
    parser.add_argument(
        "--allow",
        default="data-public/amazon_purchases_allowlist.csv",
        help="Path to allow-list CSV",
    )
    parser.add_argument(
        "--out",
        default="assets/amazon/amazon_purchases_public.csv",
        help="Output path for public CSV",
    )
    args = parser.parse_args()

    full_path = Path(args.full)
    allow_path = Path(args.allow)
    out_path = Path(args.out)

    if not full_path.exists():
        raise SystemExit(f"Missing full dataset: {full_path}")
    if not allow_path.exists():
        raise SystemExit(f"Missing allow-list: {allow_path}")

    full = pd.read_csv(full_path)
    allow = pd.read_csv(allow_path)

    # Normalize ASIN
    full["asin"] = full["asin"].astype(str).str.strip()
    allow["asin"] = allow["asin"].astype(str).str.strip()

    # Join allow-list to full dataset
    merged = allow.merge(full, on="asin", how="left", validate="one_to_many")

    # Fail loudly if allow-list ASINs are not found in full dataset
    missing = merged[merged["product_name"].isna()]["asin"].unique().tolist()
    if missing:
        raise SystemExit(f"These ASINs were not found in full dataset: {missing}")

    public = pd.DataFrame(
        {
            "product_name": merged["product_name"],
            "asin": merged["asin"],
            "affiliate_url": merged["affiliate_url"],
            "category": merged.get("category", ""),
            "notes": merged.get("notes", ""),
        }
    )

    # Deduplicate (in case you bought same ASIN multiple times)
    public = public.drop_duplicates(subset=["asin"]).sort_values("product_name")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    public.to_csv(out_path, index=False)
    print(f"Wrote {len(public):,} rows -> {out_path}")


if __name__ == "__main__":
    main()
