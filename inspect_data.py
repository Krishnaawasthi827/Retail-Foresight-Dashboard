# This script checks all CSV files one by one
# I am using pandas because it makes reading CSVs easy

import pandas as pd
import os

print("========================================")
print("MY CURRENT LOCATION")
print("========================================")
print(os.getcwd())
print()

print("========================================")
print("LOOKING FOR CSV FILES")
print("========================================")

# Get everything in this folder
everything = os.listdir('.')

# Pick out only CSV files
csv_files = []
for item in everything:
    if item.endswith('.csv'):
        csv_files.append(item)

print("Found", len(csv_files), "CSV file(s):")
for f in csv_files:
    print("  -", f)

if len(csv_files) == 0:
    print("ERROR: No CSV files found in this folder.")
    print("Make sure you are in the right place.")
    exit()

print()
print("========================================")
print("CHECKING EACH FILE ONE BY ONE")
print("========================================")

for file_name in csv_files:
    print()
    print("----------------------------------------")
    print("FILE:", file_name)
    print("----------------------------------------")

    # Read it
    df = pd.read_csv(file_name)

    # Basic shape
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Column names:", list(df.columns))

    # Missing values
    print("Missing values per column:")
    for col in df.columns:
        count = df[col].isnull().sum()
        if count > 0:
            print("  ", col, ":", count)
        else:
            print("  ", col, ": 0")

    # Duplicates
    dups = df.duplicated().sum()
    print("Duplicate rows:", dups)

    # Check for bad numbers in transaction files
    name_lower = file_name.lower()
    if "transaction" in name_lower or "sales" in name_lower:
        if "quantity" in df.columns:
            bad_qty = 0
            for q in df["quantity"]:
                if q < 0:
                    bad_qty = bad_qty + 1
            print("Negative quantities:", bad_qty)

        if "unit_price" in df.columns:
            bad_price = 0
            for p in df["unit_price"]:
                if p <= 0:
                    bad_price = bad_price + 1
            print("Zero or negative prices:", bad_price)

print()
print("========================================")
print("ALL DONE")
print("========================================")