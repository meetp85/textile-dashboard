"""
Lakshmi Textile & Clothing — Sales Analytics Dashboard
Sector: Textile & Clothing
Mobile-friendly | Built with Streamlit + Plotly + Pandas

HOW TO RUN LOCALLY:
    pip install streamlit pandas plotly openpyxl
    streamlit run textile_dashboard.py

HOW TO DEPLOY:
    Push to GitHub → share.streamlit.io → Deploy
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Lakshmi Textile Dashboard",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
* { box-sizing: border-box; }
.block-container {
    padding: 0.8rem 0.8rem 2rem !important;
    max-width: 100% !important;
}
div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; }
div[data-testid="stMetricLabel"] { font-size: 12px !important; }
div[data-testid="metric-container"] {
    background: #faf5ff;
    border-radius: 10px;
    padding: 10px 12px !important;
    border-left: 3px solid #7B3F9E;
    margin-bottom: 8px;
}
h1 { font-size: 20px !important; line-height: 1.3 !important; }
h2 { font-size: 17px !important; }
h3 { font-size: 15px !important; margin-top: 0.8rem !important; }
div[data-testid="stDataFrame"] { overflow-x: auto !important; font-size: 12px !important; }
div[data-testid="stAlert"] { font-size: 13px !important; padding: 8px 12px !important; }
@media (min-width: 768px) {
    .block-container { padding: 1.5rem 2rem 3rem !important; }
    div[data-testid="stMetricValue"] { font-size: 26px !important; }
    h1 { font-size: 26px !important; }
    h3 { font-size: 17px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Colours (purple textile theme) ───────────────────
PURPLE      = "#7B3F9E"
PURPLE_DARK = "#2D1B4E"
PURPLE_LT   = "#C084FC"
TEAL        = "#0D9488"
AMBER       = "#B45309"
CORAL       = "#DC2626"
GRAY        = "#64748B"
CHART_COLORS = [PURPLE, TEAL, AMBER, CORAL, "#EC4899", GRAY]

CATEGORIES = [
    "Sarees", "Salwar Suits", "Kurtis",
    "Men's Wear", "Kids Wear", "Fabrics", "Lehengas & Ethnic",
]
CHANNELS = ["Walk-in", "WhatsApp Order", "Online"]
PAYMENTS = ["Cash", "UPI", "Card", "Credit"]


# ── Data loader ───────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_excel(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name="Sales Data - March 2026", header=3)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Date"])
    df["Date"]         = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df                 = df.dropna(subset=["Date"])
    df["Day"]          = df["Date"].dt.day_name()
    df["Total Amount"] = pd.to_numeric(df["Total Amount (Rs.)"],  errors="coerce").fillna(0)
    df["Qty"]          = pd.to_numeric(df["Qty"],                  errors="coerce").fillna(0)
    df["Unit Price"]   = pd.to_numeric(df["Unit Price (Rs.)"],     errors="coerce").fillna(0)
    df["Discount Amt"] = pd.to_numeric(df["Discount Amt (Rs.)"],   errors="coerce").fillna(0)
    df["Discount %"]   = pd.to_numeric(df["Discount (%)"],         errors="coerce").fillna(0)
    df["Category"]     = df["Category"].fillna("Other")
    df["Channel"]      = df["Channel"].fillna("Unknown")
    df["Item Name"]    = df["Item Name"].fillna("—")
    df["Payment Mode"] = df["Payment Mode"].fillna("Unknown")
    return df


# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👗 Lakshmi Textile")
    st.markdown("---")
    uploaded = st.file_uploader("Upload Sales Excel", type=["xlsx"])
    st.markdown("---")
    st.markdown("### Filters")

if uploaded:
    df_full = load_excel(uploaded)
else:
    try:
        df_full = load_excel("Lakshmi_Textile_Sales_March2026.xlsx")
    except Exception:
        st.error("Demo file not found. Upload your Excel using the sidebar.")
        st.stop()

with st.sidebar:
    sel_cat = st.multiselect("Category", ["All"] + CATEGORIES, default=["All"])
    sel_ch  = st.selectbox("Channel", ["All Channels"] + CHANNELS)
    sel_pay = st.selectbox("Payment", ["All Payments"] + PAYMENTS)
    days    = ["All Days","Monday","Tuesday","Wednesday",
               "Thursday","Friday","Saturday","Sunday"]
    sel_day = st.selectbox("Day", days)
    st.caption("Dashboard by [Your Startup] · Nagpur")

df = df_full.copy()
if "All" not in sel_cat and sel_cat:
    df = df[df["Category"].isin(sel_cat)]
if sel_ch  != "All Channels":  df = df[df["Channel"]      == sel_ch]
if sel_pay != "All Payments":  df = df[df["Payment Mode"] == sel_pay]
if sel_day != "All Days":      df = df[df["Day"]          == sel_day]

if df.empty:
    st.warning("No data for selected filters. Try changing filters.")
    st.stop()


# ── Header ────────────────────────────────────────────
st.markdown("## 👗 Lakshmi Textile & Clothing")
st.caption(f"March 2026  ·  {len(df)} transactions  ·  {'Live data ✅' if uploaded else 'Demo data 📊'}")
st.markdown("---")


# ── KPI Cards ─────────────────────────────────────────
total_rev      = df["Total Amount"].sum()
total_orders   = len(df)
total_pieces   = int(df["Qty"].sum())
avg_order      = total_rev / total_orders if total_orders else 0
total_discount = df["Discount Amt"].sum()
best_item      = df.groupby("Item Name")["Total Amount"].sum().idxmax()
best_rev       = df.groupby("Item Name")["Total Amount"].sum().max()

c1, c2 = st.columns(2)
c1.metric("Total Revenue",    f"Rs.{total_rev:,.0f}")
c2.metric("Total Bills",      f"{total_orders:,}")

c3, c4 = st.columns(2)
c3.metric("Pieces Sold",      f"{total_pieces:,}")
c4.metric("Avg Bill Value",   f"Rs.{avg_order:,.0f}")

c5, c6 = st.columns(2)
c5.metric("Discount Given",   f"Rs.{total_discount:,.0f}",
          "check if too high", delta_color="inverse")
c6.metric("Top Item Revenue", f"Rs.{best_rev:,.0f}", best_item[:20])

st.markdown("---")


# ── Revenue by Category ───────────────────────────────
st.markdown("### Revenue by Category")
cat_rev = (
    df.groupby("Category")["Total Amount"].sum()
      .reset_index().sort_values("Total Amount")
      .rename(columns={"Total Amount": "Revenue"})
)
fig_cat = px.bar(
    cat_rev, x="Revenue", y="Category", orientation="h",
    color="Revenue",
    color_continuous_scale=["#E9D5FF", PURPLE],
    text=cat_rev["Revenue"].apply(lambda x: f"Rs.{x/1000:.0f}K"),
)
fig_cat.update_traces(textposition="outside", textfont_size=10)
fig_cat.update_layout(
    coloraxis_showscale=False,
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=0, r=60, t=10, b=0), height=300,
    xaxis=dict(showgrid=True, gridcolor="#f3f4f6", title=""),
    yaxis=dict(showgrid=False, title="", tickfont=dict(size=11)),
)
st.plotly_chart(fig_cat, use_container_width=True)


# ── Channel + Payment split ───────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Channel Split")
    ch_data = (
        df.groupby("Channel")["Total Amount"].sum()
          .reset_index().rename(columns={"Total Amount": "Revenue"})
    )
    fig_ch = px.pie(
        ch_data, values="Revenue", names="Channel",
        color_discrete_sequence=CHART_COLORS, hole=0.45,
    )
    fig_ch.update_traces(textposition="outside", textinfo="label+percent", textfont_size=10)
    fig_ch.update_layout(
        showlegend=False, margin=dict(l=5, r=5, t=10, b=5),
        height=260, paper_bgcolor="white",
    )
    st.plotly_chart(fig_ch, use_container_width=True)

with col2:
    st.markdown("### Payment Mode")
    pay_data = (
        df.groupby("Payment Mode")["Total Amount"].sum()
          .reset_index().rename(columns={"Total Amount": "Revenue"})
    )
    fig_pay = px.pie(
        pay_data, values="Revenue", names="Payment Mode",
        color_discrete_sequence=[TEAL, PURPLE, AMBER, CORAL], hole=0.45,
    )
    fig_pay.update_traces(textposition="outside", textinfo="label+percent", textfont_size=10)
    fig_pay.update_layout(
        showlegend=False, margin=dict(l=5, r=5, t=10, b=5),
        height=260, paper_bgcolor="white",
    )
    st.plotly_chart(fig_pay, use_container_width=True)


# ── Daily Revenue Trend ───────────────────────────────
st.markdown("### Daily Revenue Trend")
daily = (
    df.groupby(df["Date"].dt.date)["Total Amount"].sum()
      .reset_index().rename(columns={"Total Amount": "Revenue"})
)
daily["7-day avg"] = daily["Revenue"].rolling(7, min_periods=1).mean()

fig_trend = go.Figure()
fig_trend.add_trace(go.Bar(
    x=daily["Date"], y=daily["Revenue"],
    name="Daily", marker_color=PURPLE_LT, opacity=0.6,
))
fig_trend.add_trace(go.Scatter(
    x=daily["Date"], y=daily["7-day avg"],
    name="7-day avg", line=dict(color=PURPLE_DARK, width=2.5),
))
fig_trend.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=0, r=0, t=10, b=0), height=220,
    legend=dict(orientation="h", y=1.15, x=0, font=dict(size=11)),
    xaxis=dict(showgrid=False, tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor="#f3f4f6",
               tickformat=",", tickfont=dict(size=10)),
)
st.plotly_chart(fig_trend, use_container_width=True)


# ── Day of Week ───────────────────────────────────────
st.markdown("### Best Days of the Week")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
day_rev = (
    df.groupby("Day")["Total Amount"].sum()
      .reindex(day_order).fillna(0).reset_index()
      .rename(columns={"Total Amount": "Revenue"})
)
fig_day = px.bar(
    day_rev, x="Day", y="Revenue",
    color="Revenue",
    color_continuous_scale=["#E9D5FF", PURPLE],
    text=day_rev["Revenue"].apply(lambda x: f"Rs.{x/1000:.0f}K"),
)
fig_day.update_traces(textposition="outside", textfont_size=10)
fig_day.update_layout(
    coloraxis_showscale=False,
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=0, r=0, t=10, b=0), height=250,
    xaxis=dict(showgrid=False, title="", tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor="#f3f4f6", title="", tickfont=dict(size=10)),
)
st.plotly_chart(fig_day, use_container_width=True)


# ── Top 10 Items ──────────────────────────────────────
st.markdown("### Top 10 Best-Selling Items")
top_items = (
    df.groupby(["Item Name", "Category"])
      .agg(Qty=("Qty","sum"), Revenue=("Total Amount","sum"))
      .reset_index()
      .sort_values("Revenue", ascending=False)
      .head(10)
)
top_items["Revenue"] = top_items["Revenue"].apply(lambda x: f"Rs.{x:,.0f}")
top_items["Qty"]     = top_items["Qty"].astype(int)
st.dataframe(
    top_items.rename(columns={"Item Name": "Item"}),
    use_container_width=True, hide_index=True,
)


# ── Slow Movers ───────────────────────────────────────
st.markdown("### Slow-Moving Stock")
st.caption("Items sold fewer than 3 pieces this month — reduce stock or run an offer")
item_qty = (
    df.groupby(["Item Name", "Category"])["Qty"].sum()
      .reset_index().rename(columns={"Qty": "Pieces Sold"})
)
slow = item_qty[item_qty["Pieces Sold"] < 3].sort_values("Pieces Sold")
if slow.empty:
    st.success("No slow-moving stock this month! Great inventory health.")
else:
    slow["Action"] = slow["Pieces Sold"].apply(
        lambda x: "Clear stock / heavy discount" if x <= 1 else "Run combo offer / promote"
    )
    st.dataframe(slow, use_container_width=True, hide_index=True)


# ── Discount Analysis ─────────────────────────────────
st.markdown("### Discount Analysis")
st.caption("How much discount is being given per category")
disc_cat = (
    df.groupby("Category")
      .agg(
          Total_Revenue=("Total Amount", "sum"),
          Total_Discount=("Discount Amt", "sum"),
      )
      .reset_index()
)
disc_cat["Discount %"] = (
    disc_cat["Total_Discount"] / (disc_cat["Total_Revenue"] + disc_cat["Total_Discount"]) * 100
).round(1)
disc_cat["Total Revenue"]  = disc_cat["Total_Revenue"].apply(lambda x: f"Rs.{x:,.0f}")
disc_cat["Total Discount"] = disc_cat["Total_Discount"].apply(lambda x: f"Rs.{x:,.0f}")
disc_cat["Discount %"]     = disc_cat["Discount %"].apply(lambda x: f"{x}%")
st.dataframe(
    disc_cat[["Category", "Total Revenue", "Total Discount", "Discount %"]],
    use_container_width=True, hide_index=True,
)


# ── Staff Performance ─────────────────────────────────
st.markdown("### Staff Sales Performance")
staff_rev = (
    df.groupby("Staff")
      .agg(Bills=("Total Amount","count"), Revenue=("Total Amount","sum"))
      .reset_index()
      .sort_values("Revenue", ascending=False)
)
staff_rev["Revenue"] = staff_rev["Revenue"].apply(lambda x: f"Rs.{x:,.0f}")
st.dataframe(staff_rev, use_container_width=True, hide_index=True)


# ── AI Insights ───────────────────────────────────────
st.markdown("---")
st.markdown("### AI Insights")

best_day = day_rev.sort_values("Revenue", ascending=False).iloc[0]
st.success(
    f"Best day: **{best_day['Day']}** earns Rs.{best_day['Revenue']:,.0f}. "
    "Keep your best staff and full stock ready on this day."
)

top_ch  = ch_data.sort_values("Revenue", ascending=False).iloc[0]
ch_pct  = top_ch["Revenue"] / ch_data["Revenue"].sum() * 100
if ch_pct > 70:
    st.info(
        f"{top_ch['Channel']} brings {ch_pct:.0f}% of revenue. "
        "Start promoting WhatsApp ordering to reduce walk-in dependency."
    )
else:
    st.info(f"Good channel mix! {top_ch['Channel']} leads at {ch_pct:.0f}%.")

disc_total = df["Discount Amt"].sum()
disc_pct   = disc_total / (total_rev + disc_total) * 100
if disc_pct > 8:
    st.warning(
        f"Discount rate is {disc_pct:.1f}% — Rs.{disc_total:,.0f} given away this month. "
        "Review if discounts are converting or just reducing margin."
    )
else:
    st.success(f"Healthy discount rate at {disc_pct:.1f}%. Margins are protected.")

low_cat = cat_rev.sort_values("Revenue").iloc[0]
st.warning(
    f"Lowest performing category: **{low_cat['Category']}** — "
    "consider a combo offer or seasonal discount to clear slow stock."
)

st.markdown("---")
st.caption("Built by [Your Startup Name] · Nagpur · Data is private and confidential")
