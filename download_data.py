from pathlib import Path

import gdown


DATA_DIR = Path(__file__).resolve().parent / "cleaned_files"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "customer_segments.csv": "1a-Fwr3pOf4SnjbmmsF_yJXeN_lbYx2TW",
    "customers_clean.csv": "1N69NeCNhX-TomMwe0Pca-jiLs5Uf0MGE",
    "flags_clean.csv": "1vwNKRb0EqtI4wN1cwY-8Ey2Yu8cg3AYP",
    "forecast_backtest.csv.gz": "1GM8AXlWU0sZg1D_K_OD34i17ze5DvLjx",
    "forecast_data.csv": "1zaHWg-obOFtPJpH6rqk4Au7YI5umvDeN",
    "inventory_clean.csv": "1K-p758ZSornzJLRGCbjKRT2eB7IleuhK",
    "latest_forecast": "174yPDslDcrByboPPNkkVbLWKZdJsNXz1",
    "promotion_clean.csv": "1bBLGGxUsi83ldNRcnrUlB1SAhL8rhsQM",
    "risk_final.csv.gz": "1n-ZENF6_3sZplLN9z7jHV1Srlwhn0IIc",
    "sales_clean.csv.gz": "1DW5GgBkmAKtRPrGDim79mvY2q-QntRYw",
    "skus_clean.csv.gz": "1sB_6-MKAsF26NJpqqpHQE5rF8Qr3bKGM",
    "stores_clean.csv": "1COuhmL8daF3vpHLZ5j_GEk0VsQVQK7Hl",
    "wape_summary.csv": "1O8echCgXHHbmDvrpH98n_ak1KD5g2VUH",

   
}


def download_data():
    for filename, file_id in FILES.items():
        destination = DATA_DIR / filename

        if destination.exists() and destination.stat().st_size > 0:
            print(f"Already available: {filename}")
            continue

        print(f"Downloading {filename}...")

        result = gdown.download(
            id=file_id,
            output=str(destination),
            quiet=False,
        )

        if result is None or not destination.exists():
            raise RuntimeError(f"Download failed: {filename}")

        if destination.stat().st_size == 0:
            raise RuntimeError(f"Downloaded file is empty: {filename}")

        print(f"Downloaded: {filename}")

