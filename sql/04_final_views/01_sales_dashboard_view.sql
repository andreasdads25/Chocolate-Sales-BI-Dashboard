/* ============================================================================
   File: 01_sales_dashboard_view.sql
   Purpose: Final semantic layer for Streamlit dashboard.
   Business Goal:
       Provide a unified, analysis-ready dataset for BI reporting.
   Technical Notes:
       Combines multiple KPI queries into a single view.
   ============================================================================ */

CREATE OR REPLACE VIEW sales_dashboard_view AS
SELECT
    product,
    country,
    sales_person,
    order_date,
    amount,
    boxes_shipped,
    year,
    month,
    profitability_score
FROM sales_clean;
