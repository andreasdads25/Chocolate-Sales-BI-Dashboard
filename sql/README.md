#  **SQL Layer Documentation**

This folder contains the full SQL pipeline for the **Chocolate Sales BI Dashboard**.  
The structure follows consulting‑grade BI standards and is organized into four layers:



## 1️ RAW LAYER — `/01_raw`
Contains scripts related to the initial ingestion of data.

**Files:**
- `01_create_sales_table.sql` → Creates the raw table structure.
- `02_insert_raw_data.sql` → Documents the loading of raw data (via Python ETL).

**Purpose:**
- Store the unmodified transactional data exactly as received.
- Provide a single source of truth before any transformations.



## 2️ CLEANING LAYER — `/02_cleaning`
Contains transformations that clean, standardize, and validate the raw data.

**Files:**
- `01_clean_sales.sql` → Cleans and standardizes fields (dates, profitability, etc.)

**Purpose:**
- Ensure data quality.
- Convert raw fields into analysis‑ready formats.
- Apply business rules (e.g., profitability mapping).



## 3️ ANALYSIS LAYER — `/03_analysis`
Contains analytical SQL queries used to compute KPIs and business metrics.

**Files:**
- `01_total_revenue_per_product.sql`
- `02_monthly_revenue_trend.sql`
- `03_top_5_customers.sql`
- `04_revenue_by_region.sql`
- `05_average_order_value.sql`

**Purpose:**
- Provide reusable analytical queries.
- Support dashboard visualizations and PDF reporting.
- Demonstrate business understanding through SQL.



## 4️ SEMANTIC LAYER — `/04_final_views`
Contains final SQL views consumed directly by the dashboard.

**Files:**
- `01_sales_dashboard_view.sql`

**Purpose:**
- Provide a unified, analysis‑ready dataset.
- Improve dashboard performance.
- Serve as the “single version of truth” for BI reporting.



##  Summary
This SQL folder demonstrates a complete BI pipeline:

**Raw → Clean → Analyze → Serve**

This structure ensures:
- maintainability  
- scalability  
- clarity  
- professional BI engineering standards  

It mirrors how real BI teams organize SQL in enterprise environments.
