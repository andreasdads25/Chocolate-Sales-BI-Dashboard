import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Chocolate Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# LOADING SCREEN
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
    animation: fadeOut 0.8s ease-out 1.2s forwards;
}
.loader {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #0a84ff;
    border-radius: 50%;
    width: 42px;
    height: 42px;
    animation: spin 0.9s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }
.loading-text {
    margin-top: 12px;
    font-size: 16px;
    font-weight: 500;
    color: #0f172a;
}
@keyframes fadeOut { to { opacity: 0; visibility: hidden; } }
</style>

<div id="loading-screen">
    <div class="loader"></div>
    <div class="loading-text">Preparing your analytics...</div>
</div>
"""
st.markdown(loading_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# PREMIUM CSS (Deloitte + Apple Hybrid)
# ---------------------------------------------------------
css = """
<style>

html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"],
main, section, header, footer, .block-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

.theme-wrapper { padding-top: 0 !important; margin-top: 0 !important; }

.theme-light {
    --bg: #ffffff;
    --bg-header: #0b1120;
    --text: #0f172a;
    --text-muted: #6b7280;
    --accent: #0a84ff;
    --accent-soft: #38bdf8;
    --border: #e5e7eb;
}
.theme-dark {
    --bg: #020617;
    --bg-header: #020617;
    --text: #e5e7eb;
    --text-muted: #9ca3af;
    --accent: #38bdf8;
    --accent-soft: #0a84ff;
    --border: #1f2937;
}

[data-testid="stSidebar"] {
    width: 340px !important;
    font-size: 1.05rem !important;
}

.app-header {
    position: sticky;
    top: 0;
    z-index: 900;
    background: linear-gradient(90deg, var(--bg-header), #020617);
    padding: 0.75rem;
    margin: 0 -1rem 0 -1rem !important;
    box-shadow: 0 10px 25px rgba(15,23,42,0.45);
}
.app-logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: #e5e7eb;
}
.app-logo-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    background: radial-gradient(circle at 30% 30%, #facc15, #f97316);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.kpi-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0.9rem;
    margin-bottom: 0.75rem;
}
.kpi-card {
    background: linear-gradient(135deg, rgba(15,23,42,0.02), rgba(148,163,184,0.08));
    border-radius: 12px;
    padding: 0.75rem;
    border: 1px solid var(--border);
    box-shadow: 0 10px 25px rgba(15,23,42,0.08);
}
.kpi-header {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.kpi-icon {
    width: 22px;
    height: 22px;
    border-radius: 999px;
    background: radial-gradient(circle at 30% 30%, var(--accent-soft), var(--accent));
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 12px;
}
.kpi-value {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text);
}

.chart-card {
    background: var(--bg);
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid var(--border);
    box-shadow: 0 12px 30px rgba(15,23,42,0.08);
}

/* Fade-in */
.fade-in-up {
    opacity: 0;
    transform: translateY(15px);
    animation: fadeInUp 0.8s ease-out forwards;
}
.fade-delay-1 { animation-delay: 0.2s; }
.fade-delay-2 { animation-delay: 0.4s; }
.fade-delay-3 { animation-delay: 0.6s; }

@keyframes fadeInUp {
    0% { opacity: 0; transform: translateY(15px);}
    100% { opacity: 1; transform: translateY(0);}
}

</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ---------------------------------------------------------
# THEME TOGGLE
# ---------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

dark_mode = st.toggle("Dark mode", value=st.session_state["theme"] == "dark")
st.session_state["theme"] = "dark" if dark_mode else "light"
theme_class = "theme-dark" if st.session_state["theme"] == "dark" else "theme-light"

st.markdown(f'<div class="theme-wrapper {theme_class}">', unsafe_allow_html=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="app-header fade-in-up">
  <div class="app-logo">
    <div class="app-logo-icon">🍫</div>
    <div>
      <div style="font-weight:700; font-size:15px;">Chocolate Sales BI</div>
      <div style="font-size:11px; color:#9ca3af;">Executive Analytics Dashboard</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "Data", "Data.xlsx")
    df = pd.read_excel(path, sheet_name="Data_Raw")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.strftime("%b")
    df["Month"] = pd.Categorical(
        df["Month"],
        categories=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        ordered=True
    )
    if "Profitability" in df.columns:
        df["Profitability"] = df["Profitability"].map({"High":3,"Medium":2,"Low":1})
    return df

df = load_data()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("🍫 Filters")
    year = st.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True))
    countries = st.multiselect(
        "Select Country",
        sorted(df["Country"].unique()),
        default=sorted(df["Country"].unique())
    )
    search = st.text_input("🔍 Search Product")
    drill = st.selectbox("Focus Country", ["All"] + sorted(df["Country"].unique()))

filtered = df[(df["Year"] == year) & (df["Country"].isin(countries))]
if search:
    filtered = filtered[filtered["Product"].str.contains(search, case=False)]

if filtered.empty:
    st.warning("No data available for this selection.")
    st.stop()

# για συγκεκριμένη χώρα
drill_df = filtered if drill.strip().lower() == "all" else filtered[filtered["Country"] == drill]

# ---------------------------------------------------------
# KPI SECTION
# ---------------------------------------------------------
st.subheader("Executive Summary")

total_rev = filtered["Amount"].sum()
total_boxes = filtered["Boxes Shipped"].sum() if "Boxes Shipped" in filtered.columns else 0
avg_sale = filtered["Amount"].mean()
active_products = filtered["Product"].nunique()
avg_profit = filtered["Profitability"].mean() if "Profitability" in filtered.columns else None
avg_profit_display = f"{avg_profit:.2f}" if avg_profit is not None else "N/A"

kpi_html = f"""
<div class="kpi-row fade-in-up fade-delay-1">
  <div class="kpi-card">
    <div class="kpi-header"><div class="kpi-icon">💰</div><span>Total Revenue</span></div>
    <div class="kpi-value">${total_rev:,.0f}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-header"><div class="kpi-icon">📦</div><span>Total Boxes Shipped</span></div>
    <div class="kpi-value">{total_boxes:,.0f}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-header"><div class="kpi-icon">💳</div><span>Avg Sale Value</span></div>
    <div class="kpi-value">${avg_sale:,.2f}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-header"><div class="kpi-icon">🍬</div><span>Active Products</span></div>
    <div class="kpi-value">{active_products}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-header"><div class="kpi-icon">📈</div><span>Avg Profitability</span></div>
    <div class="kpi-value">{avg_profit_display}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-header"><div class="kpi-icon">📊</div><span>MoM Growth</span></div>
    <div class="kpi-value">N/A</div>
  </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# OVERVIEW CHARTS
# ---------------------------------------------------------
st.subheader("Overview")

col1, col2 = st.columns(2)

with col1:
    monthly = filtered.groupby("Month")["Amount"].sum()
    rolling = monthly.rolling(2).mean()
    st.markdown('<div class="chart-card fade-in-up fade-delay-2">', unsafe_allow_html=True)
    fig = px.line(
        x=monthly.index,
        y=monthly.values,
        markers=True,
        title="Monthly Sales Trend",
        labels={"x": "Month", "y": "Amount"}
    )
    fig.add_scatter(
        x=monthly.index,
        y=rolling,
        mode="lines",
        name="Rolling_2M",
        line=dict(color="#0a84ff", width=3)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    country_sales = filtered.groupby("Country")["Amount"].sum().sort_values(ascending=False)
    st.markdown('<div class="chart-card fade-in-up fade-delay-2">', unsafe_allow_html=True)
    fig2 = px.bar(
        x=country_sales.index,
        y=country_sales.values,
        title="Sales by Country",
        labels={"x": "Country", "y": "Amount"},
        color=country_sales.values,
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Products & Profitability",
    "👥 Sales Performance",
    "🔍 Drill-down Country View"
])

with tab1:
    st.subheader("Products & Profitability")
    if "Profitability" in filtered.columns:
        prod = filtered.groupby("Product")[["Amount", "Profitability"]].mean()
        st.markdown('<div class="chart-card fade-in-up fade-delay-3">', unsafe_allow_html=True)
        figp = px.scatter(
            prod,
            x="Profitability",
            y="Amount",
            size="Amount",
            color="Amount",
            hover_name=prod.index,
            title="Product Profitability Map",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(figp, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Profitability data not available.")

with tab2:
    st.subheader("Sales Performance")
    if "Boxes Shipped" in filtered.columns:
        monthly_boxes = filtered.groupby("Month")["Boxes Shipped"].sum()
        st.markdown('<div class="chart-card fade-in-up fade-delay-3">', unsafe_allow_html=True)
        figb = px.line(
            x=monthly_boxes.index,
            y=monthly_boxes.values,
            markers=True,
            title="Monthly Boxes Shipped",
            labels={"x": "Month", "y": "Boxes Shipped"}
        )
        st.plotly_chart(figb, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Boxes Shipped column not available in dataset.")

with tab3:
    st.subheader("Drill-down Country View")

    if drill.strip().lower() == "all":
        # Drill-down for ALL: breakdown by Country
        drill_group = filtered.groupby("Country")["Amount"].sum().sort_values(ascending=False)
        title = "Sales Breakdown — All Countries"
        x_label = "Country"
    else:
        # Drill-down for specific country: breakdown by Product
        drill_group = drill_df.groupby("Product")["Amount"].sum().sort_values(ascending=False)
        title = f"Sales Breakdown — {drill}"
        x_label = "Product"

    st.markdown('<div class="chart-card fade-in-up fade-delay-3">', unsafe_allow_html=True)
    figd = px.bar(
        x=drill_group.index,
        y=drill_group.values,
        title=title,
        labels={"x": x_label, "y": "Amount"},
        color=drill_group.values,
        color_continuous_scale="Blues"
    )
    st.plotly_chart(figd, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# DOWNLOADS
# ---------------------------------------------------------
st.subheader("Download Options")

colA, colB = st.columns(2)

with colA:
    st.write("### Download Filtered Data")
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv, "filtered_data.csv", "text/csv")

with colB:
    st.write("### Download BI PDF Report")

    def generate_pdf(df_in):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("<b>Chocolate Sales BI Report</b>", styles["Title"]))
        story.append(Spacer(1, 12))
        summary = [
            ["Metric","Value"],
            ["Total Revenue", f"${df_in['Amount'].sum():,.0f}"],
            ["Total Boxes Shipped", f"{df_in['Boxes Shipped'].sum():,.0f}" if "Boxes Shipped" in df_in.columns else "N/A"],
            ["Avg Sale Value", f"${df_in['Amount'].mean():,.2f}"],
            ["Active Products", f"{df_in['Product'].nunique()}"],
        ]
        table = Table(summary)
        table.setStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey)
        ])
        story.append(table)
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    pdf_file = generate_pdf(filtered)
    st.download_button("📄 Download PDF Report", pdf_file, "BI_Report.pdf", "application/pdf")

st.markdown("</div>", unsafe_allow_html=True)
