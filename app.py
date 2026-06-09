"""
Cafe Sales Interactive Dashboard
Author: Urbanus Kathitu | github.com/KathituCodes

Run: streamlit run app.py
Expects: cafe_sales_clean.csv in the same directory.
         If not found, generates synthetic demo data automatically.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Cafe Sales Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand palette (matches CV / notebook aesthetic) ──────────────────────────

NAVY   = "#1F3864"
TEAL   = "#2E75B6"
MINT   = "#52B69A"
AMBER  = "#E9C46A"
CORAL  = "#E76F51"
SLATE  = "#264653"
LIGHT  = "#F4F9FF"
MID    = "#D0E4F7"

ITEM_COLORS = {
    "Coffee":   TEAL,
    "Salad":    MINT,
    "Sandwich": AMBER,
    "Cake":     CORAL,
    "Juice":    "#A8DADC",
    "Tea":      "#457B9D",
    "Unknown":  "#AAAAAA",
}

# ── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #F0F4FA; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1F3864;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {
        color: #D0E4F7 !important;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* KPI metric cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid #2E75B6;
        box-shadow: 0 2px 8px rgba(31,56,100,0.08);
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6B7A99;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1F3864;
        line-height: 1.1;
    }
    .kpi-delta {
        font-size: 0.8rem;
        color: #52B69A;
        margin-top: 2px;
        font-weight: 600;
    }
    .kpi-delta.negative { color: #E76F51; }

    /* Section headers */
    .section-header {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #2E75B6;
        border-bottom: 2px solid #D0E4F7;
        padding-bottom: 6px;
        margin-bottom: 16px;
        margin-top: 28px;
    }

    /* Chart cards */
    .chart-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(31,56,100,0.06);
        margin-bottom: 16px;
    }

    /* Page title */
    .dashboard-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1F3864;
        letter-spacing: -0.02em;
    }
    .dashboard-subtitle {
        font-size: 0.9rem;
        color: #6B7A99;
        margin-top: 2px;
    }

    /* Hide default Streamlit header decoration */
    header[data-testid="stHeader"] { background: transparent; }

    /* Dataframe styling */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ─────────────────────────────────────────────────────────────

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Transaction Date"])
    df.columns = df.columns.str.strip()
    df["Month"]      = df["Transaction Date"].dt.to_period("M").dt.to_timestamp()
    df["DayOfWeek"]  = df["Transaction Date"].dt.day_name()
    df["Hour"]       = df["Transaction Date"].dt.hour
    df["Week"]       = df["Transaction Date"].dt.to_period("W").dt.to_timestamp()
    return df


@st.cache_data
def make_demo_data() -> pd.DataFrame:
    """
    Generates ~9,500 rows of synthetic cafe sales data that mirrors the
    cleaned dataset structure. Used only when cafe_sales_clean.csv is absent.
    """
    rng = np.random.default_rng(42)
    n   = 9500

    items  = ["Coffee", "Salad", "Sandwich", "Cake", "Juice", "Tea"]
    prices = {"Coffee": 2.0, "Salad": 5.0, "Sandwich": 4.0,
              "Cake": 3.0, "Juice": 3.0, "Tea": 2.0}
    weights = [0.30, 0.18, 0.17, 0.14, 0.12, 0.09]

    item_col     = rng.choice(items, size=n, p=weights)
    qty_col      = rng.integers(1, 6, size=n).astype(float)
    price_col    = np.array([prices[i] for i in item_col])
    total_col    = qty_col * price_col
    payment_col  = rng.choice(
        ["Cash", "Credit Card", "Digital Wallet"], size=n, p=[0.30, 0.28, 0.42])
    location_col = rng.choice(
        ["Takeaway", "In-store"], size=n, p=[0.62, 0.38])
    dates        = pd.date_range("2023-01-01", "2023-12-31", periods=n)

    df = pd.DataFrame({
        "Transaction ID":   np.arange(1, n + 1),
        "Item":             item_col,
        "Quantity":         qty_col,
        "Price Per Unit":   price_col,
        "Total Spent":      total_col,
        "Payment Method":   payment_col,
        "Location":         location_col,
        "Transaction Date": dates,
    })
    df["Month"]     = df["Transaction Date"].dt.to_period("M").dt.to_timestamp()
    df["DayOfWeek"] = df["Transaction Date"].dt.day_name()
    df["Hour"]      = df["Transaction Date"].dt.hour
    df["Week"]      = df["Transaction Date"].dt.to_period("W").dt.to_timestamp()
    return df


# Try loading real data; fall back to demo
try:
    df_raw = load_data("cafe_sales_clean.csv")
    data_source_label = "cafe_sales_clean.csv"
except FileNotFoundError:
    df_raw = make_demo_data()
    data_source_label = "demo data (place cafe_sales_clean.csv here to use your real dataset)"


# ── Sidebar filters ───────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")

    # Date range
    min_date = df_raw["Transaction Date"].min().date()
    max_date = df_raw["Transaction Date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.markdown("---")

    # Item filter
    all_items = sorted(df_raw["Item"].dropna().unique().tolist())
    selected_items = st.multiselect(
        "Items",
        options=all_items,
        default=all_items,
    )

    st.markdown("---")

    # Payment method
    all_payments = sorted(df_raw["Payment Method"].dropna().unique().tolist())
    selected_payments = st.multiselect(
        "Payment Method",
        options=all_payments,
        default=all_payments,
    )

    st.markdown("---")

    # Location
    all_locations = sorted(df_raw["Location"].dropna().unique().tolist())
    selected_locations = st.multiselect(
        "Location",
        options=all_locations,
        default=all_locations,
    )

    st.markdown("---")
    st.markdown(
        f"<span style='font-size:0.72rem;color:#A0B4CC;'>Source: {data_source_label}</span>",
        unsafe_allow_html=True,
    )


# ── Apply filters ─────────────────────────────────────────────────────────────

if len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = pd.Timestamp(min_date), pd.Timestamp(max_date)

df = df_raw[
    (df_raw["Transaction Date"] >= start_date) &
    (df_raw["Transaction Date"] <= end_date) &
    (df_raw["Item"].isin(selected_items)) &
    (df_raw["Payment Method"].isin(selected_payments)) &
    (df_raw["Location"].isin(selected_locations))
].copy()

# Guard: empty filter result
if df.empty:
    st.warning("No data matches the current filters. Adjust the sidebar selections.")
    st.stop()


# ── KPI calculations ──────────────────────────────────────────────────────────

total_revenue   = df["Total Spent"].sum()
total_txns      = len(df)
avg_order_value = df["Total Spent"].mean()
total_qty       = df["Quantity"].sum()
top_item        = df.groupby("Item")["Total Spent"].sum().idxmax()
top_payment     = df["Payment Method"].value_counts().idxmax()

# Period-over-period: split filtered range in half for delta
mid_point   = start_date + (end_date - start_date) / 2
df_first    = df[df["Transaction Date"] <= mid_point]
df_second   = df[df["Transaction Date"] > mid_point]
rev_delta   = (
    (df_second["Total Spent"].sum() - df_first["Total Spent"].sum())
    / df_first["Total Spent"].sum() * 100
    if df_first["Total Spent"].sum() > 0 else 0
)


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="dashboard-title">Cafe Sales Dashboard</div>'
    '<div class="dashboard-subtitle">Interactive sales performance tracker '
    '-- use the sidebar to filter by date, item, payment method, or location</div>',
    unsafe_allow_html=True,
)

st.markdown("&nbsp;", unsafe_allow_html=True)


# ── KPI row ───────────────────────────────────────────────────────────────────

k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, label, value, delta_text="", negative=False):
    delta_class = "kpi-delta negative" if negative else "kpi-delta"
    col.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="{delta_class}">{delta_text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

kpi(k1, "Total Revenue",      f"${total_revenue:,.0f}",
    f"{'+ ' if rev_delta >= 0 else ''}{rev_delta:.1f}% vs prior half", rev_delta < 0)
kpi(k2, "Transactions",       f"{total_txns:,}")
kpi(k3, "Avg Order Value",    f"${avg_order_value:.2f}")
kpi(k4, "Units Sold",         f"{total_qty:,.0f}")
kpi(k5, "Top Item",           top_item, top_payment)


# ── Row 1: Revenue trend  +  Item revenue breakdown ──────────────────────────

st.markdown('<div class="section-header">Revenue Trends</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:
    # Granularity toggle
    granularity = st.radio(
        "Time granularity",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True,
        key="gran",
    )
    gran_col = {"Daily": "Transaction Date", "Weekly": "Week", "Monthly": "Month"}[granularity]

    trend = (
        df.groupby(gran_col)["Total Spent"]
        .sum()
        .reset_index()
        .rename(columns={gran_col: "Date", "Total Spent": "Revenue"})
    )

    fig_trend = px.area(
        trend, x="Date", y="Revenue",
        color_discrete_sequence=[TEAL],
        labels={"Revenue": "Revenue ($)", "Date": ""},
    )
    fig_trend.update_traces(
        fill="tozeroy",
        line=dict(color=TEAL, width=2),
        fillcolor="rgba(46,117,182,0.12)",
    )
    fig_trend.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=280,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        yaxis=dict(gridcolor="#EEF2F7", showline=False),
        xaxis=dict(showgrid=False),
        hovermode="x unified",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    item_rev = (
        df.groupby("Item")["Total Spent"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )
    fig_item = px.bar(
        item_rev, x="Total Spent", y="Item",
        orientation="h",
        color="Item",
        color_discrete_map=ITEM_COLORS,
        labels={"Total Spent": "Revenue ($)", "Item": ""},
    )
    fig_item.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        height=280,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        xaxis=dict(gridcolor="#EEF2F7", showline=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_item, use_container_width=True)


# ── Row 2: Payment share  +  Location split  +  Qty vs Revenue scatter ───────

st.markdown('<div class="section-header">Behaviour Breakdown</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    pay_counts = df["Payment Method"].value_counts().reset_index()
    pay_counts.columns = ["Payment Method", "Count"]
    fig_pay = px.pie(
        pay_counts, names="Payment Method", values="Count",
        color_discrete_sequence=[TEAL, MINT, AMBER],
        hole=0.45,
    )
    fig_pay.update_traces(textposition="outside", textinfo="percent+label")
    fig_pay.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        height=260,
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        title=dict(text="Payment Methods", font=dict(size=13, color=NAVY), x=0.5),
        annotations=[dict(
            text=f"{total_txns:,}<br>transactions",
            x=0.5, y=0.5, font_size=12, showarrow=False,
            font=dict(color=NAVY, family="Arial"),
        )],
    )
    st.plotly_chart(fig_pay, use_container_width=True)

with c2:
    loc_rev = df.groupby("Location")["Total Spent"].sum().reset_index()
    fig_loc = px.bar(
        loc_rev, x="Location", y="Total Spent",
        color="Location",
        color_discrete_sequence=[CORAL, TEAL],
        labels={"Total Spent": "Revenue ($)", "Location": ""},
        text_auto="$.0f",
    )
    fig_loc.update_traces(textposition="outside")
    fig_loc.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
        height=260,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        yaxis=dict(gridcolor="#EEF2F7", showline=False),
        xaxis=dict(showgrid=False),
        title=dict(text="Revenue by Location", font=dict(size=13, color=NAVY), x=0.5),
    )
    st.plotly_chart(fig_loc, use_container_width=True)

with c3:
    # Average order value by item
    avg_by_item = df.groupby("Item")["Total Spent"].mean().reset_index()
    avg_by_item.columns = ["Item", "Avg Order Value"]
    avg_by_item = avg_by_item.sort_values("Avg Order Value", ascending=False)
    fig_avg = px.bar(
        avg_by_item, x="Item", y="Avg Order Value",
        color="Item",
        color_discrete_map=ITEM_COLORS,
        labels={"Avg Order Value": "Avg ($)", "Item": ""},
        text_auto="$.2f",
    )
    fig_avg.update_traces(textposition="outside")
    fig_avg.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0),
        height=260,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        yaxis=dict(gridcolor="#EEF2F7", showline=False),
        xaxis=dict(showgrid=False),
        title=dict(text="Avg Order Value by Item", font=dict(size=13, color=NAVY), x=0.5),
    )
    st.plotly_chart(fig_avg, use_container_width=True)


# ── Row 3: Heatmap (day of week x item)  +  Revenue by item+payment ──────────

st.markdown('<div class="section-header">Cross-Dimensional Analysis</div>', unsafe_allow_html=True)

col_heat, col_pivot = st.columns([1, 1])

with col_heat:
    DOW_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heatmap_df = (
        df.groupby(["DayOfWeek", "Item"])["Total Spent"]
        .sum()
        .reset_index()
        .pivot(index="DayOfWeek", columns="Item", values="Total Spent")
        .reindex(DOW_ORDER)
        .fillna(0)
    )
    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns.tolist(),
        y=heatmap_df.index.tolist(),
        colorscale=[[0, "#EEF2F7"], [0.5, TEAL], [1, NAVY]],
        hoverongaps=False,
        hovertemplate="<b>%{y} / %{x}</b><br>Revenue: $%{z:,.0f}<extra></extra>",
    ))
    fig_heat.update_layout(
        title=dict(text="Revenue by Day x Item", font=dict(size=13, color=NAVY), x=0.0),
        margin=dict(l=0, r=0, t=40, b=0),
        height=280,
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        xaxis=dict(side="bottom"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col_pivot:
    pivot = (
        df.pivot_table(
            values="Total Spent",
            index="Item",
            columns="Payment Method",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    payment_cols = [c for c in pivot.columns if c != "Item"]
    pay_colors   = [TEAL, MINT, AMBER, CORAL]

    fig_pivot = go.Figure()
    for i, pay in enumerate(payment_cols):
        fig_pivot.add_trace(go.Bar(
            name=pay,
            x=pivot["Item"],
            y=pivot[pay],
            marker_color=pay_colors[i % len(pay_colors)],
        ))
    fig_pivot.update_layout(
        barmode="group",
        title=dict(text="Revenue by Item and Payment Method", font=dict(size=13, color=NAVY), x=0.0),
        margin=dict(l=0, r=0, t=40, b=0),
        height=280,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        yaxis=dict(gridcolor="#EEF2F7", showline=False, title="Revenue ($)"),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_pivot, use_container_width=True)


# ── Row 4: Transaction value distribution ────────────────────────────────────

st.markdown('<div class="section-header">Transaction Distribution</div>', unsafe_allow_html=True)

col_dist, col_box = st.columns([1, 1])

with col_dist:
    fig_hist = px.histogram(
        df, x="Total Spent", nbins=20,
        color_discrete_sequence=[TEAL],
        labels={"Total Spent": "Transaction Value ($)", "count": "Transactions"},
    )
    fig_hist.update_traces(marker_line_width=0.5, marker_line_color="white")
    fig_hist.update_layout(
        title=dict(text="Transaction Value Distribution", font=dict(size=13, color=NAVY), x=0.0),
        margin=dict(l=0, r=0, t=40, b=0),
        height=260,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        yaxis=dict(gridcolor="#EEF2F7", showline=False, title="Count"),
        xaxis=dict(showgrid=False),
        bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_box:
    fig_box = px.box(
        df, x="Item", y="Total Spent",
        color="Item",
        color_discrete_map=ITEM_COLORS,
        labels={"Total Spent": "Transaction Value ($)", "Item": ""},
        points="outliers",
    )
    fig_box.update_layout(
        showlegend=False,
        title=dict(text="Spread by Item", font=dict(size=13, color=NAVY), x=0.0),
        margin=dict(l=0, r=0, t=40, b=0),
        height=260,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12, color="#444"),
        yaxis=dict(gridcolor="#EEF2F7", showline=False),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_box, use_container_width=True)


# ── Row 5: Raw data explorer ──────────────────────────────────────────────────

st.markdown('<div class="section-header">Data Explorer</div>', unsafe_allow_html=True)

show_cols = ["Transaction Date", "Item", "Quantity", "Price Per Unit",
             "Total Spent", "Payment Method", "Location"]

with st.expander("View filtered records", expanded=False):
    st.markdown(
        f"Showing **{len(df):,}** records matching current filters.",
        unsafe_allow_html=True,
    )
    sort_col = st.selectbox("Sort by", show_cols, index=4)
    sort_asc = st.checkbox("Ascending", value=False)
    st.dataframe(
        df[show_cols].sort_values(sort_col, ascending=sort_asc).reset_index(drop=True),
        use_container_width=True,
        height=320,
    )
    csv_bytes = df[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data as CSV",
        data=csv_bytes,
        file_name="cafe_sales_filtered.csv",
        mime="text/csv",
    )


# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<span style="font-size:0.75rem;color:#9AAABF;">'
    'Cafe Sales Dashboard  |  Urbanus Kathitu  |  '
    '<a href="https://github.com/KathituCodes" style="color:#2E75B6;">github.com/KathituCodes</a>'
    '</span>',
    unsafe_allow_html=True,
)
