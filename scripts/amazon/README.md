# Amazon purchases pipeline

This keeps your private purchase history out of the Hugo data directory while still generating a public, curated dataset.

## Files

- `data-private/amazon_purchases_full.csv` (private, gitignored)
- `data/amazon_purchases_allowlist.csv` (public, committed)
- `data/amazon_purchases_public.csv` (public, committed)

## Build full private dataset

```bash
python scripts/amazon/build_full.py \
  --input "Retail.OrderHistory.1.csv" \
  --tag "yourtag-20"
```

## Build public dataset from allow-list

```bash
python scripts/amazon/build_public.py
```

## Allow-list format

`data/amazon_purchases_allowlist.csv`

```csv
asin,category,notes
B0G6KKP4GT,tools,Use this weekly for X
B08XYZ123,home-office,Best charger I've owned
```

## Public dataset format

`data/amazon_purchases_public.csv`

```csv
product_name,asin,affiliate_url,category,notes
```
