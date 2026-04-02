/* ============================================================================
   Query 04: Revenue by Region
   Business Purpose:
       Compare performance across countries.
   Technical Notes:
       Groups revenue by country.
   ============================================================================ */

SELECT 
    country,
    SUM(amount) AS revenue
FROM sales_clean
GROUP BY country
ORDER BY revenue DESC;
