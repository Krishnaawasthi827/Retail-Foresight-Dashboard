import pandas as pd

print("=" * 60)
print("RISK SCORING WITH RUPEE IMPACT")
print("=" * 60)

# Load data
forecast = pd.read_csv("cleaned_files/latest_forecast.csv")
inv = pd.read_csv("cleaned_files/inventory_clean.csv")
skus = pd.read_csv("cleaned_files/skus_clean.csv")

# Sum inventory across all stores per SKU
inv_by_sku = inv.groupby("sku_id").agg({
    "stock_on_hand": "sum",
    "safety_stock": "sum",
    "reorder_point": "max"
}).reset_index()

# Merge
risk = forecast.merge(inv_by_sku, on="sku_id", how="left")
risk = risk.merge(skus[["sku_id", "sku_name", "category", "cost_price"]], on="sku_id", how="left")

# Fill missing
risk["stock_on_hand"] = risk["stock_on_hand"].fillna(0)
risk["safety_stock"] = risk["safety_stock"].fillna(0)
risk["cost_price"] = risk["cost_price"].fillna(0)

results = []

for _, row in risk.iterrows():
    sku = row["sku_name"]
    cat = row["category"]
    stock = row["stock_on_hand"]
    safety = row["safety_stock"]
    forecast_demand = row["best_pred"]
    cost = row["cost_price"]

    # Forecast over lead time (assume 4 weeks for simplicity)
    forecast_4week = forecast_demand * 4

    # Stockout score: how much of the forecast is NOT covered by stock
    if forecast_4week > 0:
        stockout_score = min(max((forecast_4week - stock) / forecast_4week, 0), 1)
    else:
        stockout_score = 0

    # Overstock score: how much stock exceeds 3x forecast need
    if stock > 0:
        overstock_score = min(max((stock - forecast_4week) / (stock + 1), 0), 1)
    else:
        overstock_score = 0

    # Determine quadrant and action
    if stockout_score > 0.5 and overstock_score < 0.5:
        action = "REORDER NOW"
        quadrant = "High Stockout - Low Overstock"
    elif stockout_score < 0.5 and overstock_score > 0.5:
        action = "MARKDOWN / CLEAR"
        quadrant = "Low Stockout - High Overstock"
    elif stockout_score > 0.5 and overstock_score > 0.5:
        action = "WATCH / VOLATILE"
        quadrant = "High on Both"
    else:
        action = "HEALTHY"
        quadrant = "No Action Needed"

    # Rupee impact
    stockout_rupees = max(0, forecast_4week - stock) * cost
    overstock_rupees = max(0, stock - forecast_4week * 2) * cost

    results.append({
        "sku_id": row["sku_id"],
        "sku_name": sku,
        "category": cat,
        "stock_on_hand": int(stock),
        "forecast_4week": int(forecast_4week),
        "stockout_score": round(stockout_score, 2),
        "overstock_score": round(overstock_score, 2),
        "action": action,
        "quadrant": quadrant,
        "stockout_rupees": int(stockout_rupees),
        "overstock_rupees": int(overstock_rupees)
    })

out = pd.DataFrame(results)
out.to_csv("cleaned_files/risk_final.csv", index=False)

print("\nDone. Saved risk_final.csv")
print("Actions breakdown:")
print(out["action"].value_counts())
print("\nTotal stockout risk (rupees):", out["stockout_rupees"].sum())
print("Total overstock risk (rupees):", out["overstock_rupees"].sum())