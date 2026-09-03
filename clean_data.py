import pandas as pd
import os

# making folder for clean stuff
if not os.path.exists("cleaned_files"):
    os.mkdir("cleaned_files")

print("starting...")

# ==========================================
# SALES FILE - this one is huge
# ==========================================
print("\n--- sales_transactions.csv ---")

# loading
df1 = pd.read_csv("sales_transactions.csv")
print("rows at start:", len(df1))

# i saw there were duplicates so removing them
df1 = df1.drop_duplicates()
print("after removing dups:", len(df1))

# promo_id has lots of blanks
# i think its because most sales dont have promotion
# filling with NO_PROMO so it doesnt break later
df1["promo_id"] = df1["promo_id"].fillna("NO_PROMO")

# converting date
df1["date"] = pd.to_datetime(df1["date"])

# adding year month quarter
df1["year"] = df1["date"].dt.year
df1["month"] = df1["date"].dt.month
df1["quarter"] = df1["date"].dt.quarter

# checking if total_value is correct
# i made my own revenue column just in case
df1["my_revenue"] = df1["quantity"] * df1["unit_price"]

# saving
df1.to_csv("cleaned_files/sales_clean.csv", index=False)
print("saved sales_clean.csv")

# ==========================================
# OTHER FILES - these were mostly clean
# ==========================================

# customers
print("\n--- customer_master.csv ---")
df2 = pd.read_csv("customer_master.csv")
df2 = df2.drop_duplicates()
df2.to_csv("cleaned_files/customers_clean.csv", index=False)
print("saved")

# stores
print("\n--- store_master.csv ---")
df3 = pd.read_csv("store_master.csv")
df3 = df3.drop_duplicates()
df3.to_csv("cleaned_files/stores_clean.csv", index=False)
print("saved")

# skus
print("\n--- sku_master.csv ---")
df4 = pd.read_csv("sku_master.csv")
df4 = df4.drop_duplicates()
df4.to_csv("cleaned_files/skus_clean.csv", index=False)
print("saved")

# inventory
print("\n--- inventory_snapshot.csv ---")
df5 = pd.read_csv("inventory_snapshot.csv")
df5 = df5.drop_duplicates()
df5.to_csv("cleaned_files/inventory_clean.csv", index=False)
print("saved")

# promotions
print("\n--- promotions.csv ---")
df6 = pd.read_csv("promotions.csv")
df6 = df6.drop_duplicates()
df6.to_csv("cleaned_files/promotions_clean.csv", index=False)
print("saved")

# flags - this one had missing dates
print("\n--- sku_inventory_flags.csv ---")
df7 = pd.read_csv("sku_inventory_flags.csv")
df7 = df7.drop_duplicates()
# dropping rows with missing window dates
df7 = df7.dropna(subset=["window_start", "window_end"])
df7.to_csv("cleaned_files/flags_clean.csv", index=False)
print("saved")

print("\nDONE!")