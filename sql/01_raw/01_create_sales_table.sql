/* ============================================================================
   File: 01_create_sales_table.sql
   Purpose: Create raw sales table for Chocolate Sales BI project.
   Business Goal:
       - Store transactional sales data for analysis.
   Technical Notes:
       - Schema based on Data.xlsx structure.
   ============================================================================ */

CREATE TABLE sales_raw (
    sales_person        VARCHAR(100),
    country             VARCHAR(50),
    product             VARCHAR(100),
    order_date          DATE,
    amount              NUMERIC(12,2),
    boxes_shipped       INT,
    year                INT,
    month               VARCHAR(10),
    profitability       VARCHAR(10)
);
