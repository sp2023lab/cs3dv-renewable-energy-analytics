# CS3DV — Renewable Energy Analytics

**Module:** CS3DV — Data Integration and Information Visualisation  
**Academic Year:** 2026/27  
**Case Study A:** Renewable Energy Adoption and Climate Change Response

## 1. Project Overview

This project explores renewable energy production through data integration, dimensional modelling, SQL-based aggregation and interactive information visualisation.

The coursework uses a renewable energy dataset containing **700 observations**, representing 10 countries, five renewable energy sources and 14 years (2010–2023).

The project addresses two analytical questions:

1. What is the total energy production by renewable energy source and geographical location?
2. How does energy production change over time for different renewable energy sources?

The implementation uses **Python, Pandas, SQLite and Tableau Desktop** to transform the original dataset into a dimensional model, construct two analytical data marts and produce an interactive dashboard.

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | ETL pipeline and data processing |
| Pandas | Data cleaning, transformation and validation |
| SQLite | Dimensional database and SQL data marts |
| SQL | Aggregation, querying and reconciliation |
| Tableau Desktop | Interactive visualisation and dashboard development |
| GitHub | Version control and project documentation |

## 3. Repository Structure

```text
cs3dv-renewable-energy-analytics/
│
├── README.md
├── renewable_energy_adoption.csv
│
├── CS3DV_step3_etl.py
├── CS3DV_step4_etl.py
│
├── CS3DV_Renewable_Energy_Dashboard.twbx
├── Dashboard Coursework (2.3).twb
│
└── etl_output/
    ├── DimCountry.csv
    ├── DimYear.csv
    ├── DimEnergySource.csv
    ├── FactEnergyProduction.csv
    ├── renewable_energy_star_schema.db
    └── validation_report.txt
```

## 4. Data Integration and ETL

The ETL process is implemented in `CS3DV_step3_etl.py`.

The script performs the following operations:

**Extraction**
- Loads the original renewable energy CSV dataset.
- Validates expected column names and input structure.

**Transformation**
- Standardises attribute names and data types.
- Converts CO₂ reduction measurements into numerical tonnes.
- Checks for missing values, duplicate records and invalid numerical measurements.
- Assigns surrogate keys to dimension records.

**Loading**
- Constructs three dimension tables and one fact table.
- Creates a SQLite star schema with primary-key and foreign-key constraints.
- Exports the dimensional tables as CSV files.
- Generates a data-quality validation report.

The source dataset is preserved, and suspicious measurements are flagged rather than silently modified.

## 5. Dimensional Modelling

The database follows a **star schema**, developed using Kimball's four-step dimensional modelling approach.

The fact table has the grain of **one country, one year and one energy source per record**.

| Table | Description | Records |
|---|---|---:|
| `DimCountry` | Geographical dimension | 10 |
| `DimYear` | Temporal dimension | 14 |
| `DimEnergySource` | Renewable energy source dimension | 5 |
| `FactEnergyProduction` | Numerical production and related measurements | 700 |

The fact table includes energy production, infrastructure investment, installed capacity, CO₂ reduction, renewable energy share and jobs created.

Energy production is used as the primary additive measure for analytical queries.

## 6. SQL Data Marts

The script `CS3DV_step4_etl.py` creates two dependent data marts through SQLite views.

### Data Mart 1 — Geographic Production

**View:** `Mart_GeographicProduction`

This mart addresses the first analytical question by aggregating energy production across countries and renewable energy sources.

- Dimensions: Country and Energy Source
- Measure: Total Energy Production (MWh)
- Aggregation: `SUM()`
- Output: **50 country-source combinations**

It supports the Tableau bar chart, geographic map and heatmap.

### Data Mart 2 — Production Trends

**View:** `Mart_ProductionTrends`

This mart addresses the second analytical question by aggregating energy production by year and renewable energy source.

- Dimensions: Year and Energy Source
- Measure: Total Energy Production (MWh)
- Aggregation: `SUM()`
- Output: **70 year-source combinations**

It supports the Tableau multi-line chart.

Both marts reconcile to the fact table's total of **85,461,988,543 MWh**.

## 7. Tableau Dashboard

The interactive dashboard is available in:

**`CS3DV_Renewable_Energy_Dashboard.twbx`**

The packaged Tableau workbook contains the necessary data mart CSVs.

The dashboard combines four visualisations:

1. **Horizontal Bar Chart:** Total production by renewable energy source.
2. **Choropleth Map:** Geographical distribution of renewable energy production.
3. **Multi-Line Chart:** Annual renewable energy production trends from 2010 to 2023.
4. **Heatmap:** Country-source production comparisons.

### Dashboard Interactivity

The dashboard provides energy-source selection and geographical filtering.

Selecting a country on the map filters the geographical bar chart and heatmap.

The annual trends chart remains aggregated across all countries because the underlying production-trends mart does not retain the country dimension.

This demonstrates the trade-off between pre-aggregated analytical datasets and cross-dimensional filtering flexibility.

## 8. Data Validation

The ETL pipeline performs integrity and data-quality checks.

| Validation Check | Result |
|---|---:|
| Original observations | 700 |
| Fact table records | 700 |
| Missing values | 0 |
| Duplicate source records | 0 |
| Foreign-key violations | 0 |
| Total Energy Production | 85,461,988,543 MWh |
| Potentially inconsistent renewable-share totals | 122 |
| Production-capacity anomalies | 31 |

The 122 renewable-share flags represent country-year groups where the sum of the reported source percentages exceeds 100%.

The 31 production-capacity flags identify observations where annual energy production exceeds installed capacity multiplied by 8,760 hours.

These results indicate potential data-quality issues requiring further verification. The flagged measurements were retained rather than modified without supporting evidence.

## 9. Key Findings

The supplied dataset produces the following results:

- **Hydro** recorded the highest cumulative energy production, approximately 17.97 billion MWh.
- **Geothermal** followed with approximately 17.73 billion MWh.
- **Biomass** recorded the lowest cumulative production, approximately 16.07 billion MWh.
- The **USA** recorded the highest cumulative national production at approximately 8.88 billion MWh.
- **2021** recorded the highest annual production at approximately 6.52 billion MWh.

These findings describe the provided coursework dataset and should not be interpreted as independently verified national energy statistics.

## 10. Running the Project

### Prerequisites

- Python 3
- Pandas
- SQLite (included with Python)
- Tableau Desktop for dashboard visualisation

### Step 1 — Install Dependencies

```bash
python -m pip install pandas
```

### Step 2 — Run the ETL Pipeline

Update the `SOURCE` path in `CS3DV_step3_etl.py` to the location of `renewable_energy_adoption.csv`.

Then run:

```bash
python CS3DV_step3_etl.py
```

This generates the dimensional CSV tables, SQLite database and validation report inside `etl_output`.

### Step 3 — Generate the Data Marts

Update the `DB_PATH` variable in `CS3DV_step4_etl.py` to point to the generated SQLite database.

Run:

```bash
python CS3DV_step4_etl.py
```

This creates the two SQL views and exports their aggregated datasets.

**Note:** Step 3 recreates the SQLite database when executed. Step 4 should therefore be run afterwards.

### Step 4 — Open the Tableau Dashboard

Open `CS3DV_Renewable_Energy_Dashboard.twbx` in Tableau Desktop.

Use the packaged `.twbx` workbook rather than the standalone `.twb` file because the packaged version contains the required data sources.

## 11. Limitations

The analysis is subject to limitations in the supplied dataset, including potentially inconsistent renewable-energy percentages and production values relative to installed capacity.

Additionally, aggregating the geographical and temporal data marts separately restricts certain cross-dimensional filtering operations.

Future improvements could include enhanced data-quality verification, more detailed geographical and temporal dimensions, and a unified data mart supporting additional interactive filtering.

## 12. Project Scope

This repository documents the implementation of the CS3DV coursework, demonstrating the complete analytical workflow from raw data to an interactive Tableau dashboard.

The project focuses on **data integration, dimensional modelling, SQL aggregation, data validation and information visualisation**, rather than making definitive claims about real-world renewable energy performance.
