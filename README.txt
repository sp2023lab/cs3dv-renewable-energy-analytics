CS3DV — CASE STUDY A — STEP 3 ETL PACKAGE
================================================

CONTENTS
  README.txt                        This guide
  renewable_energy_adoption.csv     Original provided dataset (unchanged)
  CS3DV_step3_etl.py                Complete Python/Pandas ETL script
  etl_output/DimCountry.csv         Country dimension (10 rows)
  etl_output/DimYear.csv            Year dimension (14 rows)
  etl_output/DimEnergySource.csv    Source dimension (5 rows)
  etl_output/FactEnergyProduction.csv  Production fact table (700 rows)
  etl_output/renewable_energy_star_schema.db  SQLite star schema with PK/FK constraints
  etl_output/validation_report.txt  Data-quality and integrity checks

RUNNING ON YOUR WINDOWS PC
  1. Extract the ZIP.
  2. Place renewable_energy_adoption.csv in the coursework folder named
     in the SOURCE variable of CS3DV_step3_etl.py.
  3. Install pandas if needed: py -m pip install pandas
  4. From Command Prompt, run: py CS3DV_step3_etl.py
  5. Generated files will appear in an 'etl_output' folder beside the input CSV.

NOTE: The supplied Python script uses the exact Windows path you previously gave.
Edit SOURCE only if the CSV resides somewhere else. Running the script
recreates the ETL tables, SQLite database and validation report. The source
CSV is never overwritten.

KEY DATA NOTES
  * Fact table grain: one country x year x energy source.
  * Renewable share percentages are non-additive across sources.
  * Installed capacity should not be summed across successive years.
  * Data quality anomalies are flagged, not silently removed.
  * These files cover Step 3 (ETL), not the Tableau workbook or report.
