import pandas as pd
import numpy as np

print("=" * 60)
print("FORECAST WITH BASELINE + BACKTEST")
print("=" * 60)

# Load sales
df = pd.read_csv("cleaned_files/sales_clean.csv")
df["date"] = pd.to_datetime(df["date"])

# Create year and week number
df["year"] = df["date"].dt.isocalendar().year
df["week"] = df["date"].dt.isocalendar().week

# Weekly demand per SKU
weekly = df.groupby(["sku_id", "year", "week"])["quantity"].sum().reset_index()
weekly.columns = ["sku_id", "year", "week", "actual_demand"]
print("Total SKU-week combinations:", len(weekly))

# ========================================
# BASELINE: Same week last year average
# ========================================
print("\nBuilding seasonal-naive baseline...")

baseline_results = []

for sku in weekly["sku_id"].unique():
    sku_data = weekly[weekly["sku_id"] == sku].copy()

    for _, row in sku_data.iterrows():
        current_year = row["year"]
        current_week = row["week"]

        # Look at same week in PREVIOUS years only
        history = sku_data[
            (sku_data["week"] == current_week) &
            (sku_data["year"] < current_year)
            ]["actual_demand"]

        if len(history) > 0:
            pred = history.mean()
        else:
            # No history: use overall average for this SKU
            pred = sku_data["actual_demand"].mean()

        baseline_results.append({
            "sku_id": sku,
            "year": current_year,
            "week": current_week,
            "actual": row["actual_demand"],
            "baseline_pred": pred
        })

baseline_df = pd.DataFrame(baseline_results)

# ========================================
# SIMPLE MODEL: Average of last 4 weeks
# ========================================
print("Building rolling-4-week model...")

model_results = []

for sku in weekly["sku_id"].unique():
    sku_data = weekly[weekly["sku_id"] == sku].sort_values(["year", "week"])

    for i in range(len(sku_data)):
        current_year = sku_data.iloc[i]["year"]
        current_week = sku_data.iloc[i]["week"]
        actual = sku_data.iloc[i]["actual_demand"]

        if i < 4:
            # Not enough history: use baseline
            pred = baseline_df[
                (baseline_df["sku_id"] == sku) &
                (baseline_df["year"] == current_year) &
                (baseline_df["week"] == current_week)
                ]["baseline_pred"].values[0]
        else:
            # Average of previous 4 weeks
            pred = sku_data.iloc[i - 4:i]["actual_demand"].mean()

        model_results.append({
            "sku_id": sku,
            "year": current_year,
            "week": current_week,
            "actual": actual,
            "model_pred": pred
        })

model_df = pd.DataFrame(model_results)

# ========================================
# MERGE AND CALCULATE WAPE
# WAPE = average of |actual - predicted| / actual
# ========================================
print("\nCalculating WAPE...")

final = baseline_df.merge(model_df, on=["sku_id", "year", "week", "actual"])

# Calculate errors using simple loops so you can explain every step
baseline_errors = []
model_errors = []

for _, row in final.iterrows():
    # Skip if actual is 0 (can't divide by 0)
    if row["actual"] > 0:
        be = abs(row["actual"] - row["baseline_pred"]) / row["actual"]
        me = abs(row["actual"] - row["model_pred"]) / row["actual"]
        baseline_errors.append(be)
        model_errors.append(me)

baseline_wape = np.mean(baseline_errors) * 100
model_wape = np.mean(model_errors) * 100

print("Baseline WAPE:", round(baseline_wape, 2), "%")
print("Model WAPE:", round(model_wape, 2), "%")

if model_wape < baseline_wape:
    print("Model beats baseline by", round(baseline_wape - model_wape, 2), "%")
    final["best_pred"] = final["model_pred"]
    winner = "Model"
else:
    print("Baseline wins. Using baseline for deployment.")
    final["best_pred"] = final["baseline_pred"]
    winner = "Baseline"

# Save everything
final.to_csv("cleaned_files/forecast_backtest.csv", index=False)

# Save summary for report
summary = pd.DataFrame({
    "Model": ["Seasonal-Naive Baseline", "Rolling-4Week Model"],
    "WAPE": [baseline_wape, model_wape]
})
summary.to_csv("cleaned_files/wape_summary.csv", index=False)

# Save latest forecast for each SKU (for dashboard)
latest = final.groupby("sku_id").last().reset_index()
latest.to_csv("cleaned_files/latest_forecast.csv", index=False)

print("\nSaved all forecast files.")
print("Winner:", winner)