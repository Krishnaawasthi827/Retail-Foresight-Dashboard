import os

import pandas as pd

print("Compressing files for GitHub...")

files = [
    "cleaned_files/sales_clean.csv",
    "cleaned_files/forecast_backtest.csv",
    "cleaned_files/latest_forecast.csv",
    "cleaned_files/risk_final.csv"
]

for f in files:
    if os.path.exists(f):
        print(f"Compressing {f}...")
        df = pd.read_csv(f)
        gz_name = f + ".gz"
        df.to_csv(gz_name, index=False, compression="gzip")
        print(f"  Saved: {gz_name}")

        # Check sizes
        orig_size = os.path.getsize(f) / (1024 * 1024)
        new_size = os.path.getsize(gz_name) / (1024 * 1024)
        print(f"  Original: {orig_size:.1f} MB → Compressed: {new_size:.1f} MB")
    else:
        print(f"Skipping {f} (not found)")

print("\nDone! Now delete the .csv files and keep only .csv.gz files.")
