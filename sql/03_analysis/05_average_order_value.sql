/* ============================================================================
   Query 05: Average Order Value (AOV)
   Business Purpose:
       Measure average revenue per order.
   Technical Notes:
       Total revenue / number of unique orders.
   ============================================================================ */

SELECT 
    SUM(amount) / COUNT(*) AS avg_order_value
FROM sales_clean;
