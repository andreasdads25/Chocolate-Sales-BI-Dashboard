import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from streamlit_option_menu import option_menu
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

# ---------------------------------------------------------
# 1. PAGE CONFIG & UI STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="Chocolate Analytics Pro", layout="wide", initial_sidebar_state="expanded")

MAIN_BLUE = colors.HexColor("#002B5B")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E0E0E0; }
    div[data-testid="metric-container"] { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E0E0E0; }
    .chart-card { background: white; border-radius: 12px; padding: 20px; border: 1px solid #E0E0E0; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .app-header { background: #002B5B; padding: 1rem; margin: -1rem -1rem 1rem -1rem; color: white; border-radius: 0 0 10px 10px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DATA LOADING
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("../data/Data.xlsx")
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "Data", "Data.xlsx")
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_excel(path, sheet_name="Data_Raw")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.strftime("%b")
    df["Month"] = pd.Categorical(df["Month"], categories=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], ordered=True)
    if "Profitability" in df.columns:
        prof_map = {"High": 3, "Medium": 2, "Low": 1}
        df["Prof_Score"] = df["Profitability"].map(prof_map)
    return df

df = load_data()

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<div style='text-align:center;'><h2 style='color:#002B5B;'>🍫 CHOCO BI</h2></div>", unsafe_allow_html=True)
    selected = option_menu(menu_title=None, options=["Home", "Analytics", "Drill-down", "Export", "Exit"], 
                         icons=["house", "bar-chart", "search", "file-earmark-pdf", "box-arrow-right"], 
                         default_index=0, styles={"nav-link-selected": {"background-color": "#002B5B"}})
    st.markdown("---")
    year = st.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True))
    countries_list = sorted(df["Country"].unique())
    countries = st.multiselect("Select Countries", countries_list, default=countries_list)
    search = st.text_input("🔍 Search Product")

filtered = df[(df["Year"] == year) & (df["Country"].isin(countries))]
if search: filtered = filtered[filtered["Product"].str.contains(search, case=False)]

# ---------------------------------------------------------
# 4. BLUE THEMED PDF GENERATOR WITH DYNAMIC INSIGHTS
# ---------------------------------------------------------
def generate_pdf_report(data, sel_year, sel_countries):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], textColor=MAIN_BLUE, fontSize=18, spaceAfter=10)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], textColor=MAIN_BLUE, fontSize=14, spaceBefore=12, spaceAfter=6)
    insight_style = ParagraphStyle('InsightStyle', parent=styles['Normal'], fontSize=10, leading=14, leftIndent=20)
    
    story = []
    
    # --- ΣΕΛΙΔΑ 1: Executive Summary & Monthly ---
    story.append(Paragraph("Chocolate Sales BI Report", title_style))
    story.append(Paragraph(f"<b>Year:</b> {sel_year} | <b>Countries:</b> {', '.join(sel_countries)}", styles["Normal"]))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Executive Summary", heading_style))
    summary_data = [
        ["Metric", "Value"],
        ["Total Revenue", f"${data['Amount'].sum():,.0f}"],
        ["Total Boxes", f"{data['Boxes Shipped'].sum():,.0f}"],
        ["Avg Sale Value", f"${data['Amount'].mean():,.2f}"],
        ["Active Products", f"{data['Product'].nunique()}"],
        ["Avg Profitability", f"{data['Prof_Score'].mean():.2f}" if 'Prof_Score' in data.columns else "N/A"]
    ]
    t1 = Table(summary_data, colWidths=[200, 200])
    t1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), MAIN_BLUE), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, MAIN_BLUE), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')]))
    story.append(t1)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("Monthly Sales Overview", heading_style))
    monthly = data.groupby("Month", observed=True)["Amount"].sum().reset_index()
    m_list = [["Month", "Revenue"]] + [[r["Month"], f"${r['Amount']:,.0f}"] for _, r in monthly.iterrows()]
    t2 = Table(m_list, colWidths=[200, 200])
    t2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E6EEF5")), ('TEXTCOLOR', (0,0), (-1,0), MAIN_BLUE), ('GRID', (0,0), (-1,-1), 0.5, MAIN_BLUE)]))
    story.append(t2)

    # --- ΣΕΛΙΔΑ 2: Country Analysis & Strategic Insights ---
    story.append(PageBreak())
    story.append(Paragraph("Regional & Product Analysis", heading_style))
    
    c_sales = data.groupby("Country")["Amount"].sum().sort_values(ascending=False).reset_index()
    c_list = [["Country", "Revenue"]] + [[r["Country"], f"${r['Amount']:,.0f}"] for _, r in c_sales.iterrows()]
    t3 = Table(c_list, colWidths=[200, 200])
    t3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), MAIN_BLUE), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, MAIN_BLUE)]))
    story.append(t3)
    
    story.append(Spacer(1, 25))
    
    # ΝΕΑ ΕΝΟΤΗΤΑ: STRATEGIC BUSINESS INSIGHTS
    story.append(Paragraph("Strategic Business Insights", heading_style))
    story.append(Spacer(1, 10))
    
    # Δημιουργία δυναμικών προτάσεων βάσει δεδομένων
    top_country = c_sales.iloc[0]['Country'] if not c_sales.empty else "N/A"
    top_prod = data.groupby("Product")["Amount"].sum().idxmax() if not data.empty else "N/A"
    avg_val = data['Amount'].mean()
    
    insights = [
        f"• <b>Market Leadership:</b> {top_country} constitutes the primary revenue driver for the selected period, indicating a strong brand presence in the region.",
        f"• <b>Product Performance:</b> The product '{top_prod}' shows the highest consumer demand, suggesting it should be the focus of upcoming marketing campaigns.",
        f"• <b>Profitability Analysis:</b> The current average profitability score of {data['Prof_Score'].mean():.2f} reflects a stable margin, yet optimizations in the supply chain could further enhance ROI.",
        f"• <b>Sales Efficiency:</b> With an average transaction value of ${avg_val:,.0f}, there is a clear opportunity for cross-selling strategies to increase the basket size.",
        "• <b>Seasonal Trends:</b> Monthly fluctuations suggest a need for inventory adjustment ahead of high-demand periods to prevent stock-outs."
    ]
    
    for insight in insights:
        story.append(Paragraph(insight, insight_style))
        story.append(Spacer(1, 8))

    doc.build(story)
    return buffer.getvalue()

# ---------------------------------------------------------
# 5. MAIN PAGES (Home, Analytics, κτλ - Παραμένουν ίδια)
# ---------------------------------------------------------
if selected == "Home":
    st.markdown('<div class="app-header"><h3>Dashboard Overview</h3></div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Revenue", f"${filtered['Amount'].sum():,.0f}")
    k2.metric("Total Boxes", f"{filtered['Boxes Shipped'].sum():,.0f}")
    k3.metric("Avg Sale Value", f"${filtered['Amount'].mean():,.0f}")
    k4.metric("Active Products", filtered["Product"].nunique())
    k5.metric("Avg Profitability", f"{filtered['Prof_Score'].mean():.2f}" if 'Prof_Score' in filtered.columns else "N/A")
    k6.metric("Countries", len(countries))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(px.line(filtered.groupby("Month", observed=True)["Amount"].sum().reset_index(), x="Month", y="Amount", title="Monthly Trend", color_discrete_sequence=["#002B5B"]), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(px.bar(filtered.groupby("Country")["Amount"].sum().reset_index(), x="Country", y="Amount", title="Sales by Country", color_discrete_sequence=["#002B5B"]), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Analytics":
    st.title("📊 Strategic Analytics")
    analytics_country = st.selectbox("Select Country for Analytics:", ["All"] + countries_list)
    a_df = filtered if analytics_country == "All" else filtered[filtered["Country"] == analytics_country]
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        top_10 = a_df.groupby("Product")["Amount"].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(top_10, x="Amount", y="Product", orientation='h', title=f"Top 10 Products: {analytics_country}", color_discrete_sequence=["#002B5B"]), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(px.pie(a_df, values="Amount", names="Product", title="Product Revenue Split"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Drill-down":
    st.title("🔍 Deep Dive Analysis")
    drill_country = st.selectbox("Focus on Region:", ["All"] + countries_list, key="drill_p")
    d_df = filtered if drill_country == "All" else filtered[filtered["Country"] == drill_country]
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(px.bar(d_df.groupby("Product")["Amount"].sum().reset_index(), x="Product", y="Amount", title=f"Performance: {drill_country}", color_discrete_sequence=["#002B5B"]), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Export":
    st.title("📄 Report Center")
    colA, colB = st.columns(2)
    with colB:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.write("### PDF Report")
        pdf_bytes = generate_pdf_report(filtered, year, countries)
        st.download_button(label="📥 Download BI PDF Report", data=pdf_bytes, file_name=f"Chocolate_BI_Report_{year}.pdf", mime="application/pdf")
        st.markdown('</div>', unsafe_allow_html=True)
    with colA:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.write("### Raw Data Export")
        st.download_button("📥 Download CSV", filtered.to_csv(index=False).encode("utf-8"), "data.csv", "text/csv")
        st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Exit":
    st.stop()
