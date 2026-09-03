from pathlib import Path

import gdown


DATA_DIR = Path(__file__).resolve().parent / "cleaned_files"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "sales_clean.csv.gz": "YOUR_SALES_FILE_ID",
    "stores_clean.csv": "YOUR_STORES_FILE_ID",
    "skus_clean.csv": "YOUR_SKUS_FILE_ID",
    "forecast_backtest.csv.gz": "YOUR_FORECAST_FILE_ID",
    "risk_final.csv.gz": "YOUR_RISK_FILE_ID",
    "wape_summary.csv": "YOUR_WAPE_FILE_ID",
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

