**SQL Layer Documentation** <br><br>

This folder contains the full SQL pipeline for the **Chocolate Sales BI Dashboard**.  <br><br>
The structure follows consulting‑grade BI standards and is organized into four layers: <br><br>



**1️ RAW LAYER — `/01_raw`** <br><br>

Contains scripts related to the initial ingestion of data. <br><br>

**Files:** <br><br>

- `01_create_sales_table.sql` → Creates the raw table structure. <br><br>
- `02_insert_raw_data.sql` → Documents the loading of raw data (via Python ETL). <br><br>

**Purpose:** <br><br>

- Store the unmodified transactional data exactly as received. <br><br>
- Provide a single source of truth before any transformations. <br><br>



**2️ CLEANING LAYER — `/02_cleaning`** <br><br>

Contains transformations that clean, standardize, and validate the raw data. <br><br>

**Files:** <br><br>
- `01_clean_sales.sql` → Cleans and standardizes fields (dates, profitability, etc.) <br><br>

**Purpose:** <br><br>
- Ensure data quality. <br><br>
- Convert raw fields into analysis‑ready formats. <br><br>
- Apply business rules (e.g., profitability mapping). <br><br>



**3️ ANALYSIS LAYER — `/03_analysis`** <br><br>
Contains analytical SQL queries used to compute KPIs and business metrics. <br><br>

**Files:** <br><br>
- `01_total_revenue_per_product.sql` <br><br>
- `02_monthly_revenue_trend.sql` <br><br>
- `03_top_5_customers.sql` <br><br>
- `04_revenue_by_region.sql` <br><br>
- `05_average_order_value.sql` <br><br>

**Purpose:** <br><br>
- Provide reusable analytical queries. <br><br>
- Support dashboard visualizations and PDF reporting. <br><br>
- Demonstrate business understanding through SQL. <br><br>



**4️ SEMANTIC LAYER — `/04_final_views`** <br><br>
Contains final SQL views consumed directly by the dashboard. <br><br>

**Files:** <br><br>
- `01_sales_dashboard_view.sql` <br><br>

**Purpose:** <br><br>
- Provide a unified, analysis‑ready dataset. <br><br>
- Improve dashboard performance. <br><br>
- Serve as the “single version of truth” for BI reporting. <br><br>



**Summary** <br><br>
This SQL folder demonstrates a complete BI pipeline: <br><br>

**Raw → Clean → Analyze → Serve** <br><br>

This structure ensures: <br><br>
- maintainability  <br><br>
- scalability  <br><br>
- clarity  <br><br>
- professional BI engineering standards  <br><br>

It mirrors how real BI teams organize SQL in enterprise environments. <br><br>
