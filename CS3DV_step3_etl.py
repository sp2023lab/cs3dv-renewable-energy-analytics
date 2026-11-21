from pathlib import Path
import sqlite3
import pandas as pd

# Change only this path if the CSV is moved.
SOURCE = Path(r"C:\Users\samsung\OneDrive\Documents 1\Shyam Work\University\Coursework\Year 4\Data Intergration and Visualisation\Coursework\renewable_energy_adoption.csv")
OUTPUT = SOURCE.parent / "etl_output"
OUTPUT.mkdir(parents=True, exist_ok=True)

# 1. EXTRACT
raw = pd.read_csv(SOURCE)
columns = {
    "Country/Region": "country_name",
    "Year": "year",
    "Energy Source": "source_name",
    "Energy Production (MWh)": "energy_production_mwh",
    "Investment in Renewable Infrastructure (USD)": "investment_usd",
    "Policy Changes": "policy_changes",
    "Environmental Impact (CO2 Reduction)": "co2_text",
    "Installed Capacity (MW)": "installed_capacity_mw",
    "Renewable Energy Share (%)": "renewable_share_pct",
    "Jobs Created": "jobs_created",
}
if set(raw.columns) != set(columns):
    raise ValueError(f"Unexpected CSV columns: {list(raw.columns)}")

df = raw.rename(columns=columns).copy()

# 2. TRANSFORM / VALIDATE
for col in ["country_name", "source_name", "policy_changes", "co2_text"]:
    df[col] = df[col].astype("string").str.strip()

if df.isna().any().any() or (df[["country_name", "source_name"]] == "").any().any():
    raise ValueError("Missing or blank source values found")

# Convert values such as '47419999 tons' into integers.
co2_numbers = df["co2_text"].str.extract(r"^(\d+)\s+tons$", expand=False)
if co2_numbers.isna().any():
    raise ValueError("CO2 values do not match '<number> tons'")
df["co2_reduction_tons"] = co2_numbers.astype("int64")

integer_cols = ["year", "energy_production_mwh", "investment_usd",
                "installed_capacity_mw", "jobs_created"]
for col in integer_cols:
    df[col] = pd.to_numeric(df[col], errors="raise").astype("int64")
df["renewable_share_pct"] = pd.to_numeric(df["renewable_share_pct"], errors="raise")

grain = ["country_name", "year", "source_name"]
if df.duplicated(subset=grain).any():
    raise ValueError("Duplicate country-year-energy-source records found")
if not df["renewable_share_pct"].between(0, 100).all():
    raise ValueError("Renewable share percentage outside 0–100")
if (df[integer_cols[1:] + ["co2_reduction_tons"]] < 0).any().any():
    raise ValueError("Unexpected negative measures found")

# 3. CREATE DIMENSIONS (stable, reproducible surrogate keys)
dim_year = pd.DataFrame({"year": sorted(df["year"].unique())})
dim_year.insert(0, "year_key", range(1, len(dim_year) + 1))

dim_country = pd.DataFrame({"country_name": sorted(df["country_name"].unique())})
dim_country.insert(0, "country_key", range(1, len(dim_country) + 1))

dim_source = pd.DataFrame({"source_name": sorted(df["source_name"].unique())})
dim_source.insert(0, "source_key", range(1, len(dim_source) + 1))

# 4. CREATE FACT TABLE
fact = (df.merge(dim_year, on="year", validate="many_to_one")
          .merge(dim_country, on="country_name", validate="many_to_one")
          .merge(dim_source, on="source_name", validate="many_to_one"))

fact = fact[["year_key", "country_key", "source_key",
             "energy_production_mwh", "investment_usd", "installed_capacity_mw",
             "co2_reduction_tons", "renewable_share_pct", "jobs_created"]]

if len(fact) != len(raw):
    raise AssertionError("Row count changed after joins")
if fact.duplicated(["year_key", "country_key", "source_key"]).any():
    raise AssertionError("Fact composite key is not unique")
if int(fact["energy_production_mwh"].sum()) != int(raw["Energy Production (MWh)"].sum()):
    raise AssertionError("Energy production totals do not match")

# 5. WRITE FOUR CSV TABLES
for name, frame in {
    "DimYear": dim_year,
    "DimCountry": dim_country,
    "DimEnergySource": dim_source,
    "FactEnergyProduction": fact,
}.items():
    frame.to_csv(OUTPUT / f"{name}.csv", index=False)

# 6. BUILD SQLITE DATABASE WITH REAL PK/FK CONSTRAINTS
database = OUTPUT / "renewable_energy_star_schema.db"
if database.exists():
    database.unlink()  # Replaces only the previously generated database.
with sqlite3.connect(database) as connection:
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript("""
        CREATE TABLE DimYear (
            year_key INTEGER PRIMARY KEY,
            year INTEGER NOT NULL UNIQUE
        );
        CREATE TABLE DimCountry (
            country_key INTEGER PRIMARY KEY,
            country_name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE DimEnergySource (
            source_key INTEGER PRIMARY KEY,
            source_name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE FactEnergyProduction (
            year_key INTEGER NOT NULL REFERENCES DimYear(year_key),
            country_key INTEGER NOT NULL REFERENCES DimCountry(country_key),
            source_key INTEGER NOT NULL REFERENCES DimEnergySource(source_key),
            energy_production_mwh INTEGER NOT NULL,
            investment_usd INTEGER NOT NULL,
            installed_capacity_mw INTEGER NOT NULL,
            co2_reduction_tons INTEGER NOT NULL,
            renewable_share_pct REAL NOT NULL,
            jobs_created INTEGER NOT NULL,
            PRIMARY KEY (year_key, country_key, source_key)
        );
    """)
    for name, frame in {
        "DimYear": dim_year,
        "DimCountry": dim_country,
        "DimEnergySource": dim_source,
        "FactEnergyProduction": fact,
    }.items():
        placeholders = ", ".join("?" for _ in frame.columns)
        connection.executemany(
            f"INSERT INTO {name} VALUES ({placeholders})",
            list(frame.itertuples(index=False, name=None))
        )
    connection.commit()
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    result = connection.execute("SELECT COUNT(*), SUM(energy_production_mwh) FROM FactEnergyProduction").fetchone()
    assert result == (len(raw), int(raw["Energy Production (MWh)"].sum()))

# 7. QUALITY REPORT (flag suspicious values; do not silently remove them)
share_totals = df.groupby(["country_name", "year"])["renewable_share_pct"].sum()
share_flags = int((share_totals > 100).sum())
capacity_flags = int((df["energy_production_mwh"] > df["installed_capacity_mw"] * 8760).sum())
report = (
    f"Raw records: {len(raw)}\n"
    f"DimCountry: {len(dim_country)} rows\n"
    f"DimYear: {len(dim_year)} rows\n"
    f"DimEnergySource: {len(dim_source)} rows\n"
    f"FactEnergyProduction: {len(fact)} rows\n"
    f"Source & fact production total: {int(fact['energy_production_mwh'].sum()):,} MWh\n"
    f"Missing cells: {int(raw.isna().sum().sum())}\n"
    f"Duplicate source rows: {int(raw.duplicated().sum())}\n"
    f"Country-year groups with source shares summing above 100%: {share_flags}\n"
    f"Rows with production above capacity * 8760 hours: {capacity_flags}\n"
    "Policy Changes excluded: generic text, not a usable policy event dimension.\n"
    "WARNING: Renewable share percentages must not be summed across sources.\n"
    "WARNING: Installed capacity is not additive across years.\n"
)
(OUTPUT / "validation_report.txt").write_text(report, encoding="utf-8")
print(report)
print(f"Outputs saved in: {OUTPUT}")
