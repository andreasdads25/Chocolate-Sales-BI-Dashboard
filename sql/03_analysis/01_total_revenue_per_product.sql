/* ============================================================================
   Query 01: Total Revenue per Product
   Business Purpose:
       Identify top-performing products based on revenue contribution.
   Technical Notes:
       Aggregates total revenue grouped by product.
   ============================================================================ */

SELECT 
    product,
    SUM(amount) AS revenue
FROM sales_clean
GROUP BY product
ORDER BY revenue DESC;
