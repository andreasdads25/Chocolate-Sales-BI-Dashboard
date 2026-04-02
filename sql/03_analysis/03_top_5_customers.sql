/* ============================================================================
   Query 03: Top 5 Customers
   Business Purpose:
       Identify the most valuable customers.
   Technical Notes:
       Aggregates revenue per customer and returns top 5.
   ============================================================================ */

SELECT 
    sales_person AS customer_name,
    SUM(amount) AS revenue
FROM sales_clean
GROUP BY sales_person
ORDER BY revenue DESC
LIMIT 5;
