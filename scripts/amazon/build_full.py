#!/usr/bin/env python3
import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build private full purchases CSV from Amazon Retail.OrderHistory export."
        )
    )
    parser.add_argument(
        "--input", required=True, help="Path to Retail.OrderHistory*.csv"
    )
    parser.add_argument(
        "--out",
        default="data-private/amazon_purchases_full.csv",
        help="Output path for full CSV",
    )
    parser.add_argument(
        "--tag",
        required=True,
        help="Amazon Associates tag, e.g. joshuapsteele-20",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    # Keep only rows with ASIN
    df = df[df["ASIN"].notna()].copy()

    # Normalize date
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    # Build affiliate URL using Amazon-documented format
    df["affiliate_url"] = df["ASIN"].apply(
        lambda asin: f"https://www.amazon.com/dp/{asin}/ref=nosim?tag={args.tag}"
    )

    # Create a stable, useful private schema (keep extras if present)
    # Some exports vary; handle missing columns gracefully.
    def col(name: str, fallback: str = ""):
        return df[name] if name in df.columns else fallback

    full = pd.DataFrame(
        {
            "order_date": df["Order Date"].dt.strftime("%Y-%m-%d"),
            "product_name": col("Product Name"),
            "asin": df["ASIN"],
            "quantity": col("Quantity"),
            "unit_price": col("Unit Price"),
            "order_id": col("Order ID") if "Order ID" in df.columns else col("Order Number"),
            "affiliate_url": df["affiliate_url"],
        }
    )

    # Drop obvious empties
    full = full.dropna(subset=["asin", "product_name"])

    full.to_csv(out_path, index=False)
    print(f"Wrote {len(full):,} rows -> {out_path}")


if __name__ == "__main__":
    main()
