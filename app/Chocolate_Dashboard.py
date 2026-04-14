import time
import streamlit as st
import pandas as pd
import plotly.express as px

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors

# ---------------------------------------------------------
# 1. PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Chocolate Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. CUSTOM LOADING SPLASH SCREEN (HTML + CSS)
# ---------------------------------------------------------
loading_html = """
<style>
#loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.loader {
    border: 6px solid #f3f3f3;
    border-top: 6px solid #003366;
    border-radius: 50%;
    width: 55px;
    height: 55px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-text {
    margin-top: 15px;
    font-size: 18px;
    font-weight: 600;
    color: #003366;
}
</style>

<div id="loading-screen">
    <div class="loader"></div>
    <div class="loading-text">Loading..</div>
</div>

<script>
document.addEventListener("DOMContentLoaded", function(){
    setTimeout(function(){
        var loadingScreen = document.getElementById("loading-screen");
        if (loadingScreen) {
            loadingScreen.style.opacity = "0";
            loadingScreen.style.transition = "opacity 0.5s ease-out";
            setTimeout(function(){ loadingScreen.style.display = "none"; }, 500);
        }
    }, 1200);
});
</script>
"""

st.markdown(loading_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. CUSTOM CSS (ENTERPRISE UI)
# ---------------------------------------------------------
st.markdown("""
<style>
div.block-container {padding-top: 0.5rem;}

.kpi-card {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    text-align: left;
}
.kpi-label {
    font-size: 13px;
    color: #888;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 22px;
    font-weight: 700;
}
.kpi-sub {
    font-size: 12px;
    color: #4CAF50;
}

[data-testid="stSidebar"] {
    background-color: #fafafa;
}

h1, h2, h3 {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. LOAD DATA (CACHED)
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    # Διόρθωση εσοχής εδώ [cite: 8, 39]
    df = pd.read_excel("data/Data.xlsx", sheet_name="Data_Raw")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.strftime("%b")

    months_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    df["Month"] = pd.Categorical(df["Month"], categories=months_order, ordered=True)

    profit_map = {"High": 3, "Medium": 2, "Low": 1}
    if "Profitability" in df.columns:
        df["Profitability"] = df["Profitability"].map(profit_map)

    return df

with st.spinner("Loading Chocolate Sales Dashboard..."):
    time.sleep(0.5)
    df = load_data()

# ---------------------------------------------------------
# 5. SIDEBAR FILTERS
# ---------------------------------------------------------
with st.sidebar:
    st.title("🍫 Filters")

    year_list = sorted(df["Year"].unique(), reverse=True)
    year_filter = st.selectbox("Select Year", year_list, key="year_filter_main")

    country_list = sorted(df["Country"].unique())
    country_filter = st.multiselect("Select Country", country_list, default=country_list)

    product_search = st.text_input("🔍 Search Product")

    st.markdown("---")
    st.markdown("**Drill‑down**")
    drill_country = st.selectbox("Focus Country", ["All"] + country_list, key="drill_country")

filtered_df = df[(df["Year"] == year_filter) & (df["Country"].isin(country_filter))]

if product_search:
    filtered_df = filtered_df[filtered_df["Product"].str.contains(product_search, case=False)]

if filtered_df.empty:
    st.warning("No data available for this selection.")
    st.stop()

drill_df = filtered_df[filtered_df["Country"] == drill_country] if drill_country != "All" else filtered_df.copy()

# ---------------------------------------------------------
# 6. KPI CALCULATIONS
# ---------------------------------------------------------
total_sales = filtered_df["Amount"].sum()
total_boxes = filtered_df["Boxes Shipped"].sum()
avg_sale = filtered_df["Amount"].mean()
active_products = filtered_df["Product"].nunique()
avg_profitability = filtered_df["Profitability"].mean() if "Profitability" in filtered_df.columns else None

# YoY & MoM Logic
prev_year = year_filter - 1
prev_year_df = df[(df["Year"] == prev_year) & (df["Country"].isin(country_filter))]
prev_sales = prev_year_df["Amount"].sum() if not prev_year_df.empty else None
yoy_growth = (total_sales - prev_sales) / prev_sales * 100 if prev_sales and prev_sales != 0 else None

monthly_sales_full = filtered_df.groupby("Month", observed=True)["Amount"].sum().reset_index().sort_values("Month")
monthly_sales_full["Prev"] = monthly_sales_full["Amount"].shift(1)
if len(monthly_sales_full) > 1 and not pd.isna(monthly_sales_full["Prev"].iloc[-1]) and monthly_sales_full["Prev"].iloc[-1] != 0:
    mom_growth = (monthly_sales_full["Amount"].iloc[-1] - monthly_sales_full["Prev"].iloc[-1]) / monthly_sales_full["Prev"].iloc[-1] * 100
else:
    mom_growth = None

# ---------------------------------------------------------
# 7. PLOT BUILDERS (CACHED)
# ---------------------------------------------------------
@st.cache_resource
def build_monthly_sales_fig(ms_df):
    ms = ms_df.copy()
    ms["Rolling_3M"] = ms["Amount"].rolling(3).mean()
    fig = px.line(ms, x="Month", y=["Amount", "Rolling_3M"], markers=True, line_shape="spline", color_discrete_sequence=["#E67E22", "#3498DB"])
    return fig

@st.cache_resource
def build_generic_bar(df, x, y, color_scale):
    return px.bar(df, x=x, y=y, color=y, color_continuous_scale=color_scale)

# ---------------------------------------------------------
# 8. UI - KPI CARDS
# ---------------------------------------------------------
st.markdown("## 📊 Executive Summary")
col1, col2, col3, col4, col5, col6 = st.columns(6)

def kpi_card(col, label, value, sub=""):
    with col:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

kpi_card(col1, "Total Revenue", f"${total_sales:,.0f}")
kpi_card(col2, "Total Boxes", f"{total_boxes:,.0f}")
kpi_card(col3, "Avg Sale Value", f"${avg_sale:,.2f}")
kpi_card(col4, "Active Products", f"{active_products}")
kpi_card(col5, "Avg Profitability", f"{avg_profitability:.2f}" if avg_profitability is not None else "N/A")

growth_val = yoy_growth if yoy_growth is not None else (mom_growth if mom_growth is not None else 0)
growth_label = "YoY Growth" if yoy_growth is not None else "MoM Growth"
sub_text = "vs last year" if yoy_growth is not None else ("vs last month" if mom_growth is not None else "")
kpi_card(col6, growth_label, f"{growth_val:.2f}%", sub_text)

st.markdown("---")

# ---------------------------------------------------------
# 9. TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🏆 Products", "👥 Sales", "🔍 Drill‑down"])

with tab1:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📈 Monthly Sales Trend")
        st.plotly_chart(build_monthly_sales_fig(monthly_sales_full), use_container_width=True)
    with c2:
        st.subheader("🌍 Sales by Country")
        country_sales = filtered_df.groupby("Country")["Amount"].sum().reset_index().sort_values("Amount", ascending=False)
        st.plotly_chart(build_generic_bar(country_sales, "Country", "Amount", "Blues"), use_container_width=True)

with tab2:
    st.subheader("🏆 Top 10 Products by Revenue")
    top_p = filtered_df.groupby("Product")["Amount"].sum().nlargest(10).reset_index()
    st.plotly_chart(px.bar(top_p, x="Amount", y="Product", orientation="h", color="Amount", color_continuous_scale="Oranges"), use_container_width=True)

with tab3:
    st.subheader("👥 Salesperson Leaderboard")
    leader = filtered_df.groupby("Sales Person")["Amount"].sum().sort_values(ascending=False).reset_index()
    st.plotly_chart(build_generic_bar(leader, "Sales Person", "Amount", "Purples"), use_container_width=True)

with tab4:
    st.subheader(f"🔍 Focus: {drill_country}")
    drill_sales = drill_df.groupby("Sales Person")["Amount"].sum().reset_index()
    st.plotly_chart(build_generic_bar(drill_sales, "Sales Person", "Amount", "Blues"), use_container_width=True)

# ---------------------------------------------------------
# 10. PDF BUILDER
# ---------------------------------------------------------
def build_bi_pdf(filtered_df, year_filter, country_filter):
    BLUE = colors.HexColor("#003366")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = []
    story.append(Paragraph(f"Chocolate Sales Report - {year_filter}", styles["Title"]))
    story.append(Spacer(1, 12))
    
    # Summary Table
    data = [
        ["Total Revenue", f"${filtered_df['Amount'].sum():,.0f}"],
        ["Total Boxes", f"{filtered_df['Boxes Shipped'].sum():,.0f}"],
        ["Avg Sale", f"${filtered_df['Amount'].mean():,.2f}"]
    ]
    t = Table(data, colWidths=[200, 200])
    t.setStyle([('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)])
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Download Button
st.sidebar.download_button(
    label="📥 Download PDF Report",
    data=build_bi_pdf(filtered_df, year_filter, country_filter),
    file_name="Report.pdf",
    mime="application/pdf"
)
