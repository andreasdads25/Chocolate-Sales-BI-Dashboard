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
# 2. CUSTOM CSS (ENTERPRISE UI)
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
# 3. LOAD DATA (CACHED)
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
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

# Custom loading spinner για όλο το dashboard
with st.spinner("Loading Chocolate Sales Dashboard..."):
    time.sleep(3)  # μικρό τεχνητό delay για πιο smooth εμπειρία
    df = load_data()

# ---------------------------------------------------------
# 4. SIDEBAR FILTERS
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

if drill_country != "All":
    drill_df = filtered_df[filtered_df["Country"] == drill_country]
else:
    drill_df = filtered_df.copy()

# ---------------------------------------------------------
# 5. KPI CALCS
# ---------------------------------------------------------
total_sales = filtered_df["Amount"].sum()
total_boxes = filtered_df["Boxes Shipped"].sum()
avg_sale = filtered_df["Amount"].mean()
active_products = filtered_df["Product"].nunique()
avg_profitability = filtered_df["Profitability"].mean() if "Profitability" in filtered_df.columns else None

prev_year = year_filter - 1
prev_year_df = df[(df["Year"] == prev_year) & (df["Country"].isin(country_filter))]
prev_sales = prev_year_df["Amount"].sum() if not prev_year_df.empty else None

if prev_sales and prev_sales != 0:
    yoy_growth = (total_sales - prev_sales) / prev_sales * 100
else:
    yoy_growth = None

monthly_sales_full = (
    filtered_df.groupby("Month")["Amount"]
    .sum()
    .reset_index()
    .sort_values("Month")
)
monthly_sales_full["Prev"] = monthly_sales_full["Amount"].shift(1)
if len(monthly_sales_full) > 1 and monthly_sales_full["Prev"].iloc[-1] not in [0, None]:
    mom_growth = (monthly_sales_full["Amount"].iloc[-1] - monthly_sales_full["Prev"].iloc[-1]) / monthly_sales_full["Prev"].iloc[-1] * 100
else:
    mom_growth = None

country_sales = (
    filtered_df.groupby("Country")["Amount"]
    .sum()
    .reset_index()
    .sort_values("Amount", ascending=False)
)

top_products = (
    filtered_df.groupby("Product")["Amount"]
    .sum()
    .nlargest(10)
    .reset_index()
)

leaderboard = (
    filtered_df.groupby("Sales Person")["Amount"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

monthly_sales = (
    filtered_df.groupby("Month")["Amount"]
    .sum()
    .reset_index()
    .sort_values("Month")
)

# ---------------------------------------------------------
# 6. CACHED PLOT BUILDERS (PERFORMANCE TUNING)
# ---------------------------------------------------------
@st.cache_resource
def build_monthly_sales_fig(monthly_sales_df):
    ms = monthly_sales_df.copy()
    ms["Rolling_3M"] = ms["Amount"].rolling(3).mean()
    fig = px.line(
        ms,
        x="Month",
        y=["Amount", "Rolling_3M"],
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#E67E22", "#3498DB"],
    )
    fig.update_layout(legend_title_text="Metric")
    return fig

@st.cache_resource
def build_country_sales_fig(country_sales_df):
    fig = px.bar(
        country_sales_df,
        x="Country",
        y="Amount",
        color="Amount",
        color_continuous_scale="Blues"
    )
    return fig

@st.cache_resource
def build_top_products_fig(top_products_df):
    fig = px.bar(
        top_products_df,
        x="Amount",
        y="Product",
        orientation="h",
        color="Amount",
        color_continuous_scale="Oranges"
    )
    return fig

@st.cache_resource
def build_profitability_scatter_fig(prod_profit_df):
    fig = px.scatter(
        prod_profit_df,
        x="Amount",
        y="Profitability",
        size="Amount",
        color="Profitability",
        hover_name="Product",
        color_continuous_scale="Greens"
    )
    return fig

@st.cache_resource
def build_salesperson_fig(leaderboard_df):
    fig = px.bar(
        leaderboard_df,
        x="Sales Person",
        y="Amount",
        color="Amount",
        color_continuous_scale="Purples"
    )
    return fig

@st.cache_resource
def build_boxes_fig(boxes_df):
    fig = px.bar(
        boxes_df,
        x="Sales Person",
        y="Boxes Shipped",
        color="Boxes Shipped",
        color_continuous_scale="Teal"
    )
    return fig

@st.cache_resource
def build_drill_products_fig(drill_top_products_df):
    fig = px.bar(
        drill_top_products_df,
        x="Amount",
        y="Product",
        orientation="h",
        color="Amount",
        color_continuous_scale="Oranges"
    )
    return fig

@st.cache_resource
def build_drill_sales_fig(drill_sales_df):
    fig = px.bar(
        drill_sales_df,
        x="Sales Person",
        y="Amount",
        color="Amount",
        color_continuous_scale="Blues"
    )
    return fig

# ---------------------------------------------------------
# 7. KPI ROW UI
# ---------------------------------------------------------
st.markdown("## 📊 Executive Summary")

col1, col2, col3, col4, col5, col6 = st.columns(6)

def kpi_card(col, label, value, sub=None):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{sub if sub else ""}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

kpi_card(col1, "Total Revenue", f"${total_sales:,.0f}")
kpi_card(col2, "Total Boxes", f"{total_boxes:,.0f}")
kpi_card(col3, "Avg Sale Value", f"${avg_sale:,.2f}")
kpi_card(col4, "Active Products", f"{active_products}")
kpi_card(col5, "Avg Profitability", f"{avg_profitability:.2f}" if avg_profitability is not None else "N/A")
kpi_card(
    col6,
    "YoY Growth" if yoy_growth is not None else "MoM Growth",
    f"{(yoy_growth if yoy_growth is not None else (mom_growth if mom_growth is not None else 0)):.2f}%" if (yoy_growth is not None or mom_growth is not None) else "N/A",
    "vs last year" if yoy_growth is not None else ("vs last month" if mom_growth is not None else "")
)

st.markdown("---")

# ---------------------------------------------------------
# 8. TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview",
    "🏆 Products & Profitability",
    "👥 Sales Performance",
    "🔍 Drill‑down Country View"
])

# ---------------------------------------------------------
# TAB 1 — OVERVIEW
# ---------------------------------------------------------
with tab1:
    c1, c2 = st.columns([2, 1])

    # Monthly Sales Trend
    with c1:
        st.subheader("📈 Monthly Sales Trend")
        fig_line = build_monthly_sales_fig(monthly_sales)
        st.plotly_chart(fig_line, use_container_width=True, key="monthly_sales_trend")

    # Sales by Country
    with c2:
        st.subheader("🌍 Sales by Country")
        fig_country = build_country_sales_fig(country_sales)
        st.plotly_chart(fig_country, use_container_width=True, key="sales_by_country")

# ---------------------------------------------------------
# TAB 2 — PRODUCTS & PROFITABILITY
# ---------------------------------------------------------
with tab2:
    c3, c4 = st.columns([2, 2])

    # Top 10 Products
    with c3:
        st.subheader("🏆 Top 10 Products by Revenue")
        fig_top = build_top_products_fig(top_products)
        st.plotly_chart(fig_top, use_container_width=True, key="top_products")

    # Profitability Scatter
    with c4:
        st.subheader("💹 Profitability vs Revenue (Top Products)")
        if "Profitability" in filtered_df.columns:
            prod_profit = (
                filtered_df.groupby("Product")[["Amount", "Profitability"]]
                .mean()
                .reset_index()
            )
            top_prod_profit = prod_profit.sort_values("Amount", ascending=False).head(15)

            fig_scatter = build_profitability_scatter_fig(top_prod_profit)
            st.plotly_chart(fig_scatter, use_container_width=True, key="profitability_scatter")
        else:
            st.info("No numeric Profitability column available.")

# ---------------------------------------------------------
# TAB 3 — SALES PERFORMANCE
# ---------------------------------------------------------
with tab3:
    st.subheader("👥 Salesperson Leaderboard")

    fig_salesperson = build_salesperson_fig(leaderboard)
    st.plotly_chart(fig_salesperson, use_container_width=True, key="salesperson_leaderboard")

    st.subheader("📦 Boxes Shipped by Salesperson")
    boxes_leaderboard = (
        filtered_df.groupby("Sales Person")["Boxes Shipped"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_boxes = build_boxes_fig(boxes_leaderboard)
    st.plotly_chart(fig_boxes, use_container_width=True, key="boxes_by_salesperson")

# ---------------------------------------------------------
# TAB 4 — DRILL‑DOWN COUNTRY VIEW
# ---------------------------------------------------------
with tab4:
    st.subheader(f"🔍 Drill‑down: {drill_country if drill_country != 'All' else 'All Countries'}")

    if drill_df.empty:
        st.info("No data for this country selection.")
    else:
        c5, c6 = st.columns([2, 2])

        # Top Products in Focus Country
        with c5:
            st.markdown("**Top Products in Focus Country**")
            drill_top_products = (
                drill_df.groupby("Product")["Amount"]
                .sum()
                .nlargest(10)
                .reset_index()
            )
            fig_drill_prod = build_drill_products_fig(drill_top_products)
            st.plotly_chart(fig_drill_prod, use_container_width=True, key="drilldown_products")

        # Salesperson Performance in Focus Country
        with c6:
            st.markdown("**Salesperson Performance in Focus Country**")
            drill_sales = (
                drill_df.groupby("Sales Person")["Amount"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            fig_drill_sales = build_drill_sales_fig(drill_sales)
            st.plotly_chart(fig_drill_sales, use_container_width=True, key="drilldown_salespersons")

# ---------------------------------------------------------
# 9. PDF BUILDER — STYLE A2 (CLEAN + McKINSEY BLUE)
# ---------------------------------------------------------
def build_bi_pdf(df, filtered_df, drill_df, year_filter, country_filter, drill_country):
    BLUE = colors.HexColor("#003366")
    LIGHT_GREY = colors.HexColor("#F2F2F2")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    Title = styles["Title"]
    Title.textColor = BLUE

    H1 = styles["Heading1"]
    H1.textColor = BLUE
    H1.fontSize = 18
    H1.spaceAfter = 10

    H2 = styles["Heading2"]
    H2.textColor = BLUE
    H2.fontSize = 14
    H2.spaceAfter = 6

    Body = styles["BodyText"]
    Body.fontSize = 10
    Body.leading = 14

    story = []

    # COVER PAGE
    story.append(Paragraph("Chocolate Sales BI Report", Title))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Year: {year_filter}", Body))
    story.append(Paragraph(f"Countries: {', '.join(country_filter)}", Body))
    story.append(Spacer(1, 24))

    # Divider line
    story.append(Table([[""]], colWidths=[500], style=[
        ("LINEBELOW", (0,0), (-1,-1), 1, BLUE)
    ]))
    story.append(Spacer(1, 18))

    # EXECUTIVE SUMMARY BLOCK
    story.append(Paragraph("Executive Summary", H1))

    avg_profit_pdf = filtered_df["Profitability"].mean() if "Profitability" in filtered_df.columns else None
    avg_profit_str = f"{avg_profit_pdf:.2f}" if avg_profit_pdf is not None else "N/A"

    summary_block = [
        [Paragraph(
            f"""
            <para align=left>
            <b>Total Revenue:</b> ${filtered_df['Amount'].sum():,.0f}<br/>
            <b>Total Boxes:</b> {filtered_df['Boxes Shipped'].sum():,.0f}<br/>
            <b>Avg Sale Value:</b> ${filtered_df['Amount'].mean():,.2f}<br/>
            <b>Active Products:</b> {filtered_df['Product'].nunique()}<br/>
            <b>Avg Profitability:</b> {avg_profit_str}
            </para>
            """,
            Body
        )]
    ]

    summary_table = Table(
        summary_block,
        colWidths=[500],
        style=[
            ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
            ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ("TOPPADDING", (0,0), (-1,-1), 12),
            ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ]
    )

    story.append(summary_table)
    story.append(Spacer(1, 24))

    # MONTHLY SALES TABLE
    story.append(Paragraph("Monthly Sales Overview", H1))

    monthly_sales_pdf = (
        filtered_df.groupby("Month")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Month")
    )

    ms_data = [["Month", "Revenue"]]
    for _, row in monthly_sales_pdf.iterrows():
        ms_data.append([row["Month"], f"${row['Amount']:,.0f}"])

    ms_table = Table(
        ms_data,
        style=[
            ("BACKGROUND", (0,0), (-1,0), BLUE),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ]
    )

    story.append(ms_table)
    story.append(Spacer(1, 24))

    # COUNTRY SALES TABLE
    story.append(Paragraph("Sales by Country", H1))

    country_sales_pdf = (
        filtered_df.groupby("Country")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=False)
    )

    cs_data = [["Country", "Revenue"]]
    for _, row in country_sales_pdf.iterrows():
        cs_data.append([row["Country"], f"${row['Amount']:,.0f}"])

    cs_table = Table(
        cs_data,
        style=[
            ("BACKGROUND", (0,0), (-1,0), BLUE),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ]
    )

    story.append(cs_table)
    story.append(Spacer(1, 24))

    # TOP PRODUCTS TABLE
    story.append(Paragraph("Top Products by Revenue", H1))

    top_products_pdf = (
        filtered_df.groupby("Product")["Amount"]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    tp_data = [["Product", "Revenue"]]
    for _, row in top_products_pdf.iterrows():
        tp_data.append([row["Product"], f"${row['Amount']:,.0f}"])

    tp_table = Table(
        tp_data,
        style=[
            ("BACKGROUND", (0,0), (-1,0), BLUE),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("ALIGN", (1,1), (-1,-1), "RIGHT"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ]
    )

    story.append(tp_table)
    story.append(Spacer(1, 24))

    # INSIGHTS SECTION
    story.append(Paragraph("Insights & Strategic Observations", H1))

    insights = []

    if not country_sales_pdf.empty:
        insights.append(f"- Strongest market: {country_sales_pdf.iloc[0]['Country']}")
        insights.append(f"- Weakest market: {country_sales_pdf.iloc[-1]['Country']}")

    if not top_products_pdf.empty:
        share_top10 = top_products_pdf["Amount"].sum() / filtered_df["Amount"].sum() * 100
        insights.append(f"- Top 10 products contribute {share_top10:.1f}% of total revenue.")

    insights.append("- Consider targeted campaigns in low-performing regions.")
    insights.append("- High-performing products could be bundled for cross-selling.")
    insights.append("- Review pricing strategy for low-profitability items.")

    for line in insights:
        story.append(Paragraph(line, Body))
        story.append(Spacer(1, 6))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ---------------------------------------------------------
# 10. DOWNLOADS
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 📥 Download Filtered Data")
st.download_button(
    "Download CSV",
    filtered_df.to_csv(index=False),
    file_name=f"filtered_sales_data_{year_filter}.csv",
    mime="text/csv"
)

st.markdown("### 📄 Download BI PDF Report")
pdf_bytes = build_bi_pdf(df, filtered_df, drill_df, year_filter, country_filter, drill_country)

st.download_button(
    label="Download PDF Report",
    data=pdf_bytes,
    file_name=f"Chocolate_Sales_BI_Report_{year_filter}.pdf",
    mime="application/pdf"
)
