"""
Lakshmi Textile & Clothing — AI-Powered Sales Dashboard
AI Features powered by GROQ (100% FREE - no payment needed)
Model: llama-3.3-70b-versatile
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import json

st.set_page_config(
    page_title="Lakshmi Textile AI Dashboard",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
* { box-sizing: border-box; }
.block-container { padding: 0.8rem 0.8rem 2rem !important; max-width: 100% !important; }
div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 700 !important; }
div[data-testid="stMetricLabel"] { font-size: 12px !important; }
div[data-testid="metric-container"] {
    background: #faf5ff; border-radius: 10px;
    padding: 10px 12px !important; border-left: 3px solid #7B3F9E; margin-bottom: 8px;
}
div[data-testid="stDataFrame"] { overflow-x: auto !important; font-size: 12px !important; }
.ai-box {
    background: #faf5ff; border: 1px solid #d8b4fe;
    border-radius: 12px; padding: 16px; margin: 8px 0;
    font-size: 14px; line-height: 1.7;
}
.whatsapp-box {
    background: #dcfce7; border: 1px solid #16a34a;
    border-radius: 12px; padding: 16px; margin: 8px 0;
    font-size: 14px; line-height: 1.8;
}
@media (min-width: 768px) {
    .block-container { padding: 1.5rem 2rem 3rem !important; }
    div[data-testid="stMetricValue"] { font-size: 26px !important; }
}
</style>
""", unsafe_allow_html=True)

PURPLE      = "#7B3F9E"
PURPLE_DARK = "#2D1B4E"
PURPLE_LT   = "#C084FC"
TEAL        = "#0D9488"
AMBER       = "#B45309"
CORAL       = "#DC2626"
GRAY        = "#64748B"
CHART_COLORS = [PURPLE, TEAL, AMBER, CORAL, "#EC4899", GRAY]

CATEGORIES = ["Sarees","Salwar Suits","Kurtis","Men's Wear","Kids Wear","Fabrics","Lehengas & Ethnic"]
CHANNELS   = ["Walk-in","WhatsApp Order","Online"]
PAYMENTS   = ["Cash","UPI","Card","Credit"]


# ── FREE Groq AI helper ───────────────────────────────
def ask_ai(prompt: str, system: str = "") -> str:
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return (
                "⚠️ Groq API key not set.\n\n"
                "Go to share.streamlit.io → your app → Settings → Secrets → add:\n"
                "GROQ_API_KEY = \"your_key_here\""
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "system",
                    "content": system or (
                        "You are a smart business advisor for Indian textile shops. "
                        "Give practical, specific advice in simple language. "
                        "Use Rs. for currency. Keep answers under 200 words."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 700,
            "temperature": 0.7,
        }

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=30,
        )

        # Show full response if something goes wrong
        if r.status_code != 200:
            return f"API Error {r.status_code}: {r.text[:500]}"

        data = r.json()

        # Check if expected keys exist
        if "choices" not in data:
            return f"Unexpected response from Groq: {json.dumps(data)[:500]}"

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Groq API. Check your internet connection."
    except Exception as e:
        return f"Error: {str(e)}"


def build_data_summary(df: pd.DataFrame) -> str:
    total_rev   = df["Total Amount"].sum()
    total_bills = len(df)
    avg_bill    = total_rev / total_bills if total_bills else 0
    cat_rev     = df.groupby("Category")["Total Amount"].sum().sort_values(ascending=False)
    top_items   = df.groupby("Item Name")["Qty"].sum().sort_values(ascending=False).head(5)
    slow_items  = df.groupby("Item Name")["Qty"].sum()
    slow_items  = slow_items[slow_items < 3].sort_values().head(5)
    ch_rev      = df.groupby("Channel")["Total Amount"].sum().sort_values(ascending=False)
    day_rev     = df.groupby("Day")["Total Amount"].sum().sort_values(ascending=False)
    disc_total  = df["Discount Amt"].sum()
    disc_pct    = disc_total / (total_rev + disc_total) * 100 if (total_rev + disc_total) > 0 else 0
    staff_rev   = df.groupby("Staff")["Total Amount"].sum().sort_values(ascending=False)

    return f"""
TEXTILE SHOP SALES DATA - March 2026 - Nagpur, India:
- Total Revenue: Rs.{total_rev:,.0f}
- Total Bills: {total_bills}
- Average Bill: Rs.{avg_bill:,.0f}
- Category Revenue: {', '.join([f"{c}: Rs.{v:,.0f}" for c,v in cat_rev.items()])}
- Top 5 Items by Qty: {', '.join([f"{i}({int(q)}pcs)" for i,q in top_items.items()])}
- Slow Items (<3 sold): {', '.join(slow_items.index.tolist()) if len(slow_items)>0 else 'None'}
- Channels: {', '.join([f"{c}: Rs.{v:,.0f}" for c,v in ch_rev.items()])}
- Best Days: {', '.join(day_rev.index[:3].tolist())}
- Total Discount: Rs.{disc_total:,.0f} ({disc_pct:.1f}%)
- Staff Revenue: {', '.join([f"{s}: Rs.{v:,.0f}" for s,v in staff_rev.items()])}
"""


# ── Data loader ───────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_excel(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name="Sales Data - March 2026", header=3)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Date"])
    df["Date"]         = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df                 = df.dropna(subset=["Date"])
    df["Day"]          = df["Date"].dt.day_name()
    df["Total Amount"] = pd.to_numeric(df.get("Total Amount (Rs.)", pd.Series(dtype=float)), errors="coerce").fillna(0)
    df["Qty"]          = pd.to_numeric(df.get("Qty", pd.Series(dtype=float)), errors="coerce").fillna(0)
    df["Unit Price"]   = pd.to_numeric(df.get("Unit Price (Rs.)", pd.Series(dtype=float)), errors="coerce").fillna(0)
    df["Discount Amt"] = pd.to_numeric(df.get("Discount Amt (Rs.)", pd.Series(dtype=float)), errors="coerce").fillna(0)
    df["Category"]     = df["Category"].fillna("Other")
    df["Channel"]      = df["Channel"].fillna("Unknown")
    df["Item Name"]    = df["Item Name"].fillna("—")
    df["Payment Mode"] = df.get("Payment Mode", pd.Series(["Unknown"]*len(df))).fillna("Unknown")
    df["Staff"]        = df.get("Staff", pd.Series(["Unknown"]*len(df))).fillna("Unknown")
    return df


# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👗 Lakshmi Textile")
    st.markdown("**AI-Powered Dashboard**")
    st.markdown("---")
    uploaded = st.file_uploader("Upload Sales Excel", type=["xlsx"])
    st.markdown("---")
    st.markdown("### Filters")

if uploaded:
    df_full     = load_excel(uploaded)
    data_source = "Live data ✅"
else:
    try:
        df_full     = load_excel("Lakshmi_Textile_Sales_March2026.xlsx")
        data_source = "Demo data 📊"
    except Exception:
        st.error("Demo file not found. Upload your Excel using the sidebar.")
        st.stop()

with st.sidebar:
    sel_cat = st.multiselect("Category", ["All"] + CATEGORIES, default=["All"])
    sel_ch  = st.selectbox("Channel", ["All Channels"] + CHANNELS)
    sel_pay = st.selectbox("Payment", ["All Payments"] + PAYMENTS)
    days    = ["All Days","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    sel_day = st.selectbox("Day", days)
    st.caption("AI Dashboard by [Your Startup] · Nagpur")

df = df_full.copy()
if "All" not in sel_cat and sel_cat:
    df = df[df["Category"].isin(sel_cat)]
if sel_ch  != "All Channels":  df = df[df["Channel"]      == sel_ch]
if sel_pay != "All Payments":  df = df[df["Payment Mode"] == sel_pay]
if sel_day != "All Days":      df = df[df["Day"]          == sel_day]

if df.empty:
    st.warning("No data for selected filters.")
    st.stop()

DATA_SUMMARY = build_data_summary(df_full)


# ══════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════
st.markdown("## 👗 Lakshmi Textile & Clothing")
st.caption(f"March 2026  ·  {len(df)} transactions  ·  {data_source}")
st.markdown("---")


# ══════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════
total_rev      = df["Total Amount"].sum()
total_orders   = len(df)
total_pieces   = int(df["Qty"].sum())
avg_order      = total_rev / total_orders if total_orders else 0
total_discount = df["Discount Amt"].sum()
best_item      = df.groupby("Item Name")["Total Amount"].sum().idxmax()

c1, c2 = st.columns(2)
c1.metric("Total Revenue",  f"Rs.{total_rev:,.0f}")
c2.metric("Total Bills",    f"{total_orders:,}")
c3, c4 = st.columns(2)
c3.metric("Pieces Sold",    f"{total_pieces:,}")
c4.metric("Avg Bill Value", f"Rs.{avg_order:,.0f}")
c5, c6 = st.columns(2)
c5.metric("Discount Given", f"Rs.{total_discount:,.0f}", "check if too high", delta_color="inverse")
c6.metric("Top Item",       best_item[:22])
st.markdown("---")


# ══════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════
st.markdown("### Revenue by Category")
cat_rev = (
    df.groupby("Category")["Total Amount"].sum()
      .reset_index().sort_values("Total Amount")
      .rename(columns={"Total Amount": "Revenue"})
)
fig_cat = px.bar(cat_rev, x="Revenue", y="Category", orientation="h",
    color="Revenue", color_continuous_scale=["#E9D5FF", PURPLE],
    text=cat_rev["Revenue"].apply(lambda x: f"Rs.{x/1000:.0f}K"))
fig_cat.update_traces(textposition="outside", textfont_size=10)
fig_cat.update_layout(coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=0,r=60,t=10,b=0), height=300,
    xaxis=dict(showgrid=True, gridcolor="#f3f4f6", title=""),
    yaxis=dict(showgrid=False, title="", tickfont=dict(size=11)))
st.plotly_chart(fig_cat, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Channel Split")
    ch_data = df.groupby("Channel")["Total Amount"].sum().reset_index().rename(columns={"Total Amount":"Revenue"})
    fig_ch  = px.pie(ch_data, values="Revenue", names="Channel",
                     color_discrete_sequence=CHART_COLORS, hole=0.45)
    fig_ch.update_traces(textposition="outside", textinfo="label+percent", textfont_size=10)
    fig_ch.update_layout(showlegend=False, margin=dict(l=5,r=5,t=10,b=5),
                         height=260, paper_bgcolor="white")
    st.plotly_chart(fig_ch, use_container_width=True)

with col2:
    st.markdown("### Payment Mode")
    pay_data = df.groupby("Payment Mode")["Total Amount"].sum().reset_index().rename(columns={"Total Amount":"Revenue"})
    fig_pay  = px.pie(pay_data, values="Revenue", names="Payment Mode",
                      color_discrete_sequence=[TEAL,PURPLE,AMBER,CORAL], hole=0.45)
    fig_pay.update_traces(textposition="outside", textinfo="label+percent", textfont_size=10)
    fig_pay.update_layout(showlegend=False, margin=dict(l=5,r=5,t=10,b=5),
                          height=260, paper_bgcolor="white")
    st.plotly_chart(fig_pay, use_container_width=True)

st.markdown("### Daily Revenue Trend")
daily = df.groupby(df["Date"].dt.date)["Total Amount"].sum().reset_index().rename(columns={"Total Amount":"Revenue"})
daily["7-day avg"] = daily["Revenue"].rolling(7, min_periods=1).mean()
fig_trend = go.Figure()
fig_trend.add_trace(go.Bar(x=daily["Date"], y=daily["Revenue"],
    name="Daily", marker_color=PURPLE_LT, opacity=0.6))
fig_trend.add_trace(go.Scatter(x=daily["Date"], y=daily["7-day avg"],
    name="7-day avg", line=dict(color=PURPLE_DARK, width=2.5)))
fig_trend.update_layout(plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=0,r=0,t=10,b=0), height=220,
    legend=dict(orientation="h",y=1.15,x=0,font=dict(size=11)),
    xaxis=dict(showgrid=False, tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor="#f3f4f6", tickformat=",", tickfont=dict(size=10)))
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("### Best Days of the Week")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
day_rev = df.groupby("Day")["Total Amount"].sum().reindex(day_order).fillna(0).reset_index().rename(columns={"Total Amount":"Revenue"})
fig_day = px.bar(day_rev, x="Day", y="Revenue", color="Revenue",
    color_continuous_scale=["#E9D5FF", PURPLE],
    text=day_rev["Revenue"].apply(lambda x: f"Rs.{x/1000:.0f}K"))
fig_day.update_traces(textposition="outside", textfont_size=10)
fig_day.update_layout(coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=0,r=0,t=10,b=0), height=250,
    xaxis=dict(showgrid=False, title="", tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor="#f3f4f6", title="", tickfont=dict(size=10)))
st.plotly_chart(fig_day, use_container_width=True)

st.markdown("### Top 10 Best-Selling Items")
top_items = (
    df.groupby(["Item Name","Category"])
      .agg(Qty=("Qty","sum"), Revenue=("Total Amount","sum"))
      .reset_index().sort_values("Revenue", ascending=False).head(10)
)
top_items["Revenue"] = top_items["Revenue"].apply(lambda x: f"Rs.{x:,.0f}")
top_items["Qty"]     = top_items["Qty"].astype(int)
st.dataframe(top_items.rename(columns={"Item Name":"Item"}),
             use_container_width=True, hide_index=True)

st.markdown("### Slow-Moving Stock")
st.caption("Items sold fewer than 3 pieces — reduce stock or run an offer")
item_qty  = df.groupby(["Item Name","Category"])["Qty"].sum().reset_index().rename(columns={"Qty":"Pieces Sold"})
slow      = item_qty[item_qty["Pieces Sold"] < 3].sort_values("Pieces Sold")
slow_list = ", ".join(slow["Item Name"].tolist()[:5]) if not slow.empty else "None"
if slow.empty:
    st.success("No slow-moving stock this month!")
else:
    slow["Action"] = slow["Pieces Sold"].apply(
        lambda x: "Clear stock / heavy discount" if x <= 1 else "Run combo offer / promote"
    )
    st.dataframe(slow, use_container_width=True, hide_index=True)

st.markdown("### Staff Sales Performance")
staff_rev = (
    df.groupby("Staff").agg(Bills=("Total Amount","count"), Revenue=("Total Amount","sum"))
      .reset_index().sort_values("Revenue", ascending=False)
)
staff_rev["Revenue"] = staff_rev["Revenue"].apply(lambda x: f"Rs.{x:,.0f}")
st.dataframe(staff_rev, use_container_width=True, hide_index=True)

st.markdown("---")


# ══════════════════════════════════════════════════════
# AI FEATURES
# ══════════════════════════════════════════════════════
st.markdown("## 🤖 AI Business Intelligence")
st.caption("Powered by Groq AI — 100% FREE · No payment needed")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Ask AI Advisor",
    "📱 WhatsApp Generator",
    "📈 Sales Prediction",
    "👥 Customer Insights",
    "📦 Reorder Suggestions",
])


# ── Tab 1 ─────────────────────────────────────────────
with tab1:
    st.markdown("### Ask anything about your business")
    st.caption("AI reads your actual sales data to give specific answers")

    quick_qs = [
        "Which category should I focus on next month?",
        "How can I increase my average bill value?",
        "Which items should I stock more of?",
        "How can I get more WhatsApp orders?",
        "Why might my weekday sales be low?",
        "Which staff needs more training?",
    ]

    st.markdown("**Quick questions — click to ask:**")
    cols = st.columns(2)
    for i, q in enumerate(quick_qs):
        if cols[i % 2].button(q, key=f"qq_{i}"):
            st.session_state["advisor_q"] = q

    user_q = st.text_area(
        "Or type your own question:",
        value=st.session_state.get("advisor_q", ""),
        placeholder="E.g. Which sarees are not selling and what should I do?",
        height=80,
    )

    if st.button("Get AI Answer", type="primary", key="advisor_btn"):
        if user_q.strip():
            with st.spinner("AI is reading your data..."):
                prompt = f"""
Here is the sales data for a textile shop in Nagpur, India:
{DATA_SUMMARY}

Owner's question: {user_q}

Give a specific, practical answer based on this data.
Mention actual item names and numbers from the data.
Keep the answer under 200 words and use simple language.
"""
                answer = ask_ai(prompt)
            st.markdown('<div class="ai-box">', unsafe_allow_html=True)
            st.markdown(answer)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please type a question first.")


# ── Tab 2 ─────────────────────────────────────────────
with tab2:
    st.markdown("### Generate WhatsApp promotions instantly")
    st.caption("AI creates ready-to-send Hinglish messages based on your actual stock")

    promo_type   = st.selectbox("What kind of message?", [
        "Flash sale on slow-moving items",
        "Weekend special offer",
        "New stock arrival announcement",
        "Festival season promotion",
        "Summer collection launch",
        "Loyalty customer thank you + offer",
    ])
    shop_name = st.text_input("Shop name:", value="Lakshmi Textile & Clothing")
    shop_loc  = st.text_input("Location:", value="Sitabuldi, Nagpur")
    offer     = st.text_input("Offer:", value="20% off")
    phone     = st.text_input("Contact:", value="98XXXXXXXX")

    if st.button("Generate WhatsApp Message", type="primary", key="wa_btn"):
        with st.spinner("Creating message..."):
            top_3 = ", ".join(top_items["Item"].tolist()[:3]) if "Item" in top_items.columns else "top items"
            prompt = f"""
Textile shop: {shop_name}, {shop_loc}. Contact: {phone}
Offer: {offer}. Promotion type: {promo_type}
Slow items to clear: {slow_list}
Best sellers: {top_3}

Write a WhatsApp message in Hinglish (Hindi + English). Rules:
- Start with Namaste or friendly greeting
- Mention specific items and offer
- Create urgency (today only / limited stock)
- End with shop name, location, contact
- Under 80 words
- Warm and personal tone

Write ONLY the message text.
"""
            msg = ask_ai(prompt, system="You write short friendly WhatsApp messages for Indian textile shops in Hinglish. Output only the message text, nothing else.")

        st.markdown("**Copy and send this on WhatsApp:**")
        st.markdown(f'<div class="whatsapp-box">{msg}</div>', unsafe_allow_html=True)
        st.code(msg, language=None)


# ── Tab 3 ─────────────────────────────────────────────
with tab3:
    st.markdown("### Next month revenue prediction")
    st.caption("AI predicts April 2026 based on March data + Indian seasonal patterns")

    if st.button("Predict April 2026", type="primary", key="pred_btn"):
        with st.spinner("Predicting..."):
            prompt = f"""
March 2026 textile shop data from Nagpur:
{DATA_SUMMARY}

Predict April 2026. Consider:
- April = summer starts in Nagpur (very hot)
- Post-Holi — festive buying slows
- Pre-wedding season begins in May
- Cotton and light fabrics sell more in summer

Give me:
1. Expected revenue range (Rs. amounts)
2. Category that will grow — why
3. Category that may slow — why
4. Top 3 items to keep extra stock
5. One thing to avoid in April

Be specific with numbers from the data.
"""
            pred = ask_ai(prompt)
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("#### April 2026 Prediction")
        st.markdown(pred)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 4 ─────────────────────────────────────────────
with tab4:
    st.markdown("### Customer behaviour insights")

    if st.button("Analyse My Customers", type="primary", key="cust_btn"):
        with st.spinner("Analysing..."):
            pay_pct = df_full.groupby("Payment Mode")["Total Amount"].sum()
            pay_pct = (pay_pct / pay_pct.sum() * 100).round(1).to_dict()
            ch_pct  = df_full.groupby("Channel")["Total Amount"].sum()
            ch_pct  = (ch_pct / ch_pct.sum() * 100).round(1).to_dict()

            prompt = f"""
Textile shop data:
{DATA_SUMMARY}
Payment share: {pay_pct}
Channel share: {ch_pct}

Give 5 customer behaviour insights. For each:
INSIGHT: [what the data shows]
ACTION: [one specific thing owner should do]

Number them 1 to 5. Be practical for a Nagpur textile shop.
"""
            insights = ask_ai(prompt)
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown(insights)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 5 ─────────────────────────────────────────────
with tab5:
    st.markdown("### Smart reorder list for your supplier")

    budget = st.selectbox("Reorder budget:", [
        "Rs. 25,000 – 50,000",
        "Rs. 50,000 – 1,00,000",
        "Rs. 1,00,000+",
    ])
    focus = st.selectbox("April focus:", [
        "Summer — light fabrics and cotton",
        "Balanced — all categories",
        "Wedding season prep — heavy ethnic wear",
    ])

    if st.button("Generate Reorder List", type="primary", key="reorder_btn"):
        with st.spinner("Building reorder list..."):
            prompt = f"""
March 2026 textile shop data:
{DATA_SUMMARY}
Budget: {budget}. April focus: {focus}

Create supplier reorder list with 4 sections:

REORDER URGENTLY (fast sellers, likely running low):
REORDER MODERATE (steady sellers):
SKIP / REDUCE (slow movers):
NEW ITEM TO TRY (1-2 suggestions for April summer):

Add suggested quantities. Owner will show this to supplier directly.
April is summer in Nagpur — prefer light fabrics.
"""
            reorder = ask_ai(prompt)
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("#### Reorder List — April 2026")
        st.markdown(reorder)
        st.markdown('</div>', unsafe_allow_html=True)
        st.download_button(
            "Download Reorder List",
            data=reorder,
            file_name="reorder_april2026.txt",
            mime="text/plain",
        )

st.markdown("---")
st.caption("Built by [Your Startup Name] · Nagpur · AI by Groq (FREE) · Data is private")