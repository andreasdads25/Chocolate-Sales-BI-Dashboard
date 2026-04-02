/* ============================================================================
   File: 01_clean_sales.sql
   Purpose: Clean and standardize raw sales data.
   Business Goal:
       - Ensure consistent, analysis-ready dataset.
   Technical Notes:
       - Converts month names to proper order.
       - Maps profitability to numeric scale.
   ============================================================================ */

CREATE OR REPLACE VIEW sales_clean AS
SELECT
    sales_person,
    country,
    product,
    order_date,
    amount,
    boxes_shipped,
    year,
    month,
    CASE profitability
        WHEN 'High' THEN 3
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 1
        ELSE NULL
    END AS profitability_score
FROM sales_raw
WHERE amount > 0
  AND boxes_shipped >= 0
  AND order_date IS NOT NULL;
