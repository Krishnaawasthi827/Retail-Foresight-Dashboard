import numpy as np
import pandas as pd
import streamlit as st

# ========================================
# PAGE SETUP - PROFESSIONAL LOOK
# ========================================
st.set_page_config(
    page_title="FORESIGHT | NorthBay Living",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom header style
st.markdown("""
    <style>
    .main-header {
        font-size: 40px;
        font-weight: bold;
        color: #FAFAFA;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 18px;
        color: #A0AEC0;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #1E2530;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #4FD1C5;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📊 Project FORESIGHT</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Demand & Inventory Intelligence for NorthBay Living</p>', unsafe_allow_html=True)

# ========================================
# LOAD DATA - FAST WITH SESSION STATE
# ========================================

if "loaded" not in st.session_state:
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("Loading sales data...")
    sales = pd.read_csv("cleaned_files/sales_clean.csv.gz")
    progress_bar.progress(25)

    status_text.text("Loading store & product info...")
    stores = pd.read_csv("cleaned_files/stores_clean.csv")
    skus = pd.read_csv("cleaned_files/skus_clean.csv")
    sales = sales.merge(stores, on="store_id", how="left")
    sales = sales.merge(skus, on="sku_id", how="left")
    progress_bar.progress(50)

    status_text.text("Loading forecast & risk data...")
    forecast = pd.read_csv("cleaned_files/forecast_backtest.csv.gz")
    risk = pd.read_csv("cleaned_files/risk_final.csv.gz")
    wape = pd.read_csv("cleaned_files/wape_summary.csv")
    progress_bar.progress(75)

    status_text.text("Finalizing...")
    st.session_state.sales = sales
    st.session_state.forecast = forecast
    st.session_state.risk = risk
    st.session_state.skus = skus
    st.session_state.wape = wape
    st.session_state.loaded = True

    progress_bar.progress(100)
    status_text.empty()
    progress_bar.empty()

    st.success("✅ Dashboard ready! All data loaded into memory.")
    st.info("💡 Tip: Use the sidebar filters to explore specific categories or SKUs.")

# Pull from memory (instant)
sales = st.session_state.sales
forecast = st.session_state.forecast
risk = st.session_state.risk
skus = st.session_state.skus
wape = st.session_state.wape

# ========================================
# SIDEBAR - CLEAN & ORGANIZED
# ========================================
st.sidebar.markdown("## 🔍 Filters")

cats = sorted(skus["category"].unique())
sel_cat = st.sidebar.multiselect("Product Category", cats, default=cats)

sku_names = sorted(skus[skus["category"].isin(sel_cat)]["sku_name"].unique())
sel_sku = st.sidebar.selectbox("Select SKU", ["All SKUs"] + list(sku_names))

# Filter risk data
filtered_risk = risk[risk["category"].isin(sel_cat)]
if sel_sku != "All SKUs":
    filtered_risk = filtered_risk[filtered_risk["sku_name"] == sel_sku]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Forecast Accuracy")
st.sidebar.metric("Baseline WAPE", f"{wape.iloc[0]['WAPE']:.1f}%")
st.sidebar.metric("Model WAPE", f"{wape.iloc[1]['WAPE']:.1f}%")

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(filtered_risk)}** SKUs")

# ========================================
# TOP KPI CARDS - ALWAYS VISIBLE
# ========================================

total_rev = int(sales["my_revenue"].sum())
total_orders = sales["receipt_id"].nunique()
reorder_count = len(risk[risk["action"] == "REORDER NOW"])
markdown_count = len(risk[risk["action"] == "MARKDOWN / CLEAR"])

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Revenue", f"${total_rev:,}")
k2.metric("🧾 Total Orders", f"{total_orders:,}")
k3.metric("🚨 Reorder Now", reorder_count)
k4.metric("💰 Markdown", markdown_count)

st.markdown("---")

# ========================================
# TABS - PROFESSIONAL NAMES
# ========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive",
    "📈 Forecast vs Actual",
    "⚠️ Risk & Actions",
    "🎯 Decision Grid",
    "📋 Priority List",
    "💵 Rupee Impact"
])

# ---------- TAB 1: EXECUTIVE ----------
with tab1:
    st.subheader("Revenue Trends")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Monthly Revenue**")
        monthly = sales.groupby("month")["my_revenue"].sum()
        st.line_chart(monthly)

    with c2:
        st.markdown("**Revenue by Category**")
        cat_sales = sales.groupby("category")["my_revenue"].sum().sort_values(ascending=False)
        st.bar_chart(cat_sales)

# ---------- TAB 2: FORECAST ----------
with tab2:
    st.subheader("SKU-Level Demand Forecast")

    if sel_sku == "All SKUs":
        st.info("👈 Select a specific SKU from the sidebar to see its forecast vs actual demand.")
    else:
        sku_id = skus[skus["sku_name"] == sel_sku]["sku_id"].values[0]
        f = forecast[forecast["sku_id"] == sku_id].copy()

        if len(f) > 0:
            # Calculate SKU WAPE
            errors = []
            for _, row in f.iterrows():
                if row["actual"] > 0:
                    errors.append(abs(row["actual"] - row["best_pred"]) / row["actual"])
            sku_wape = np.mean(errors) * 100 if errors else 0

            st.metric("Forecast Accuracy (WAPE)", f"{sku_wape:.1f}%",
                      help="Lower is better. This shows how close the forecast is to actual demand.")

            chart_data = f[["week", "actual", "best_pred"]].set_index("week")
            chart_data.columns = ["Actual Demand", "Forecast"]
            st.line_chart(chart_data)

            st.caption(f"Showing {len(f)} weeks of history for **{sel_sku}**")
        else:
            st.warning("No forecast history available for this SKU.")

# ---------- TAB 3: RISK ----------
with tab3:
    st.subheader("Inventory Risk Overview")

    reorder = filtered_risk[filtered_risk["action"] == "REORDER NOW"]
    markdown = filtered_risk[filtered_risk["action"] == "MARKDOWN / CLEAR"]
    watch = filtered_risk[filtered_risk["action"] == "WATCH / VOLATILE"]
    healthy = filtered_risk[filtered_risk["action"] == "HEALTHY"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 Reorder", len(reorder))
    c2.metric("🟠 Markdown", len(markdown))
    c3.metric("🟡 Watch", len(watch))
    c4.metric("🟢 Healthy", len(healthy))

    st.markdown("---")
    st.markdown("**Detailed Risk Table**")

    display_df = filtered_risk[[
        "sku_name", "stock_on_hand", "forecast_4week",
        "action", "stockout_rupees", "overstock_rupees"
    ]].sort_values("stockout_rupees", ascending=False)

    st.dataframe(display_df, width='stretch', height=400)

# ---------- TAB 4: DECISION GRID ----------
with tab4:
    st.subheader("SKU Decisioning Grid")
    st.caption("Stockout Risk (Y) vs Overstock Risk (X) — Bubble size = Rupee impact")

    st.write("🔴 **Reorder Now** | 🟠 **Markdown** | 🟡 **Watch** | 🟢 **Healthy**")

    st.scatter_chart(
        filtered_risk,
        x="overstock_score",
        y="stockout_score",
        color="action",
        size="stockout_rupees"
    )

    st.info("""
    **How to read this chart:**
    - **Top-left:** High stockout risk, low overstock → Reorder immediately
    - **Bottom-right:** Low stockout, high overstock → Mark down to clear stock
    - **Top-right:** High on both → Watch closely, demand is erratic
    - **Bottom-left:** Low on both → Healthy, no action needed
    """)

# ---------- TAB 5: PRIORITY LIST ----------
with tab5:
    st.subheader("Prioritised Action List")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🚨 Top 10 Reorder Items**")
        if len(reorder) > 0:
            st.dataframe(
                reorder.sort_values("stockout_rupees", ascending=False)
                [["sku_name", "stock_on_hand", "forecast_4week", "stockout_rupees"]]
                .head(10),
                width='stretch'
            )
        else:
            st.success("No urgent reorders needed!")

    with col2:
        st.markdown("**💰 Top 10 Markdown Candidates**")
        if len(markdown) > 0:
            st.dataframe(
                markdown.sort_values("overstock_rupees", ascending=False)
                [["sku_name", "stock_on_hand", "forecast_4week", "overstock_rupees"]]
                .head(10),
                width='stretch'
            )
        else:
            st.success("No markdown candidates!")

# ---------- TAB 6: RUPEE IMPACT ----------
with tab6:
    st.subheader("Business Impact in Rupees")

    total_stockout = int(filtered_risk["stockout_rupees"].sum())
    total_overstock = int(filtered_risk["overstock_rupees"].sum())

    c1, c2 = st.columns(2)
    c1.metric("⚠️ Sales at Risk (Stockout)", f"₹{total_stockout:,}")
    c2.metric("💰 Capital Locked (Overstock)", f"₹{total_overstock:,}")

    st.markdown("---")
    st.markdown("**Impact by Category**")

    cat_impact = filtered_risk.groupby("category")[["stockout_rupees", "overstock_rupees"]].sum()
    st.bar_chart(cat_impact)