/* ============================================================================
   Query 02: Monthly Revenue Trend
   Business Purpose:
       Understand seasonality and monthly revenue evolution.
   Technical Notes:
       Uses DATE_TRUNC to group by month.
   ============================================================================ */

SELECT 
    DATE_TRUNC('month', order_date) AS month,
    SUM(amount) AS revenue
FROM sales_clean
GROUP BY month
ORDER BY month;
