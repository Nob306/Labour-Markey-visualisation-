"""
FIT2179 Data Visualisation 2 — Data Preparation Script
=======================================================
Run this once before pushing to GitHub.

Usage:
    python prepare_data.py

Inputs (place raw downloads in raw_data/ folder):
    raw_data/h5_raw.csv          RBA Table H5 Labour Force (as downloaded)
    raw_data/h4_raw.csv          RBA Table H4 Labour Costs (as downloaded)
    raw_data/sa4_raw.csv         ABS MRM1 Table 2 Unemployed persons (as exported from xlsx)

Outputs (written to data/ folder, ready for Vega-Lite):
    data/h5_labour_force.csv
    data/h4_wage_price_index.csv
    data/sa4_unemployment_long.csv
    data/sa4_unemployment_latest.csv
"""

import pandas as pd
import re
import os

os.makedirs("data", exist_ok=True)
os.makedirs("raw_data", exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: robustly find the first data row in an RBA CSV
# RBA files have 11 header rows (confirmed from actual H4 and H5 files):
#   Row 0:  Sheet title (e.g. "H5 LABOUR FORCE")
#   Row 1:  Title row
#   Row 2:  Description row
#   Row 3:  Frequency row
#   Row 4:  Type row
#   Row 5:  Units row
#   Row 6:  blank
#   Row 7:  blank           <- two blanks, not one
#   Row 8:  Source row
#   Row 9:  Publication date row
#   Row 10: Series ID row
#   Row 11: FIRST DATA ROW  (e.g. "28/02/1978,6424.6,...")
# ─────────────────────────────────────────────────────────────────────────────
def find_rba_data_start(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        first_cell = line.split(",")[0].strip().strip('"')
        if re.match(r"^\d{2}/\d{2}/\d{4}$", first_cell):
            return i
    raise ValueError(f"Could not find data start row in {filepath}")


def load_rba_csv(filepath, col_names):
    start = find_rba_data_start(filepath)
    print(f"  Data starts at row {start} (expected 11)")
    if start != 11:
        print(f"  ⚠️  WARNING: Expected row 11, got row {start}. Check file structure.")

    df = pd.read_csv(
        filepath,
        skiprows=start,
        header=None,
        names=col_names,
        engine="python",
        on_bad_lines="skip"   # early rows have fewer columns (sparse data)
    )
    return df


def parse_rba_dates(series):
    return pd.to_datetime(series, dayfirst=True).dt.strftime("%Y-%m-%d")


# ─────────────────────────────────────────────────────────────────────────────
# 1. CLEAN H5 — Labour Force (RBA)
# ─────────────────────────────────────────────────────────────────────────────
print("Cleaning H5 Labour Force...")

H5_COLS = [
    "date", "labour_force", "participation_rate",
    "part_time_employment", "full_time_employment",
    "employment", "employment_growth_yoy", "employment_trend_growth",
    "employment_to_population", "unemployment", "unemployment_rate",
    "unemployment_rate_trend", "hours_worked", "hours_worked_trend",
    "hours_worked_trend_growth", "average_hours_worked",
    "job_vacancies", "private_job_vacancies", "vacancies_to_lf_ratio"
]

h5 = load_rba_csv("data/h5-data.csv", H5_COLS)

# Drop rows where date is not a valid date string
h5 = h5[h5["date"].astype(str).str.match(r"^\d{2}/\d{2}/\d{4}$")]

# Convert date
h5["date"] = parse_rba_dates(h5["date"])

# Convert all numeric columns
for col in H5_COLS[1:]:
    h5[col] = pd.to_numeric(h5[col], errors="coerce")

# Filter to 1997 onwards
h5 = h5[h5["date"] >= "1997-01-01"].reset_index(drop=True)

h5.to_csv("data/h5_labour_force.csv", index=False)
print(f"  → data/h5_labour_force.csv ({len(h5)} rows)")
print(f"  Date range: {h5['date'].min()} → {h5['date'].max()}")
print(f"  unemployment_rate non-null: {h5['unemployment_rate'].notna().sum()}")
print(f"  participation_rate non-null: {h5['participation_rate'].notna().sum()}")
print(f"  employment_growth_yoy non-null: {h5['employment_growth_yoy'].notna().sum()}")
print(f"  average_hours_worked non-null: {h5['average_hours_worked'].notna().sum()}")
print(f"  vacancies_to_lf_ratio non-null: {h5['vacancies_to_lf_ratio'].notna().sum()}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. CLEAN H4 — Wage Price Index (RBA)
# ─────────────────────────────────────────────────────────────────────────────
print("\nCleaning H4 Wage Price Index...")

H4_COLS = [
    "date", "wage_growth_yoy", "private_wage_growth_yoy",
    "public_wage_growth_yoy", "wage_growth_qoq", "private_wage_qoq",
    "public_wage_qoq", "unit_labour_costs", "avg_earnings_growth",
    "productivity_growth", "productivity_index"
]

h4 = load_rba_csv("data/h4-data.csv", H4_COLS)

h4 = h4[h4["date"].astype(str).str.match(r"^\d{2}/\d{2}/\d{4}$")]
h4["date"] = parse_rba_dates(h4["date"])

for col in H4_COLS[1:]:
    h4[col] = pd.to_numeric(h4[col], errors="coerce")

h4 = h4[h4["date"] >= "1997-01-01"].reset_index(drop=True)

h4.to_csv("data/h4_wage_price_index.csv", index=False)
print(f"  → data/h4_wage_price_index.csv ({len(h4)} rows)")
print(f"  Date range: {h4['date'].min()} → {h4['date'].max()}")
print(f"  wage_growth_yoy non-null: {h4['wage_growth_yoy'].notna().sum()}")
print(f"  productivity_growth non-null: {h4['productivity_growth'].notna().sum()}")
print(f"  private_wage_growth_yoy non-null: {h4['private_wage_growth_yoy'].notna().sum()}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. CLEAN SA4 — ABS MRM1 Table 2 (wide → long)
# ─────────────────────────────────────────────────────────────────────────────
print("\nCleaning SA4 Modelled Estimates (wide → long)...")

# Confirmed CSV structure from actual exported file:
#   Row 0: "Australian Bureau of Statistics,,,..."
#   Row 1: "6291.0.55.001 - Modelled estimates...,,,..."
#   Row 2: "Released at 11.30 am (Canberra time)...,,,..."
#   Row 3: "Table 2 - Unemployed persons ('000)...,,,..."
#   Row 4: SA4, Mar-26, Feb-26, Jan-26, ...    <- column headers
#   Row 5: 102 Central Coast, 9.2, 7.9, ...    <- first data row

sa4_raw = pd.read_csv(
    "data/sa4_raw.csv", 
    skiprows=4,
    header=0,
    engine="python",
    on_bad_lines="skip"
)

# Rename first column
sa4_raw = sa4_raw.rename(columns={sa4_raw.columns[0]: "sa4_raw"})

# Drop trailing empty columns from CSV trailing commas
sa4_raw = sa4_raw.loc[:, ~sa4_raw.columns.str.startswith("Unnamed")]

# Drop empty rows
sa4_raw = sa4_raw.dropna(subset=["sa4_raw"])

# Keep only rows that start with 3-digit SA4 code
sa4_raw = sa4_raw[sa4_raw["sa4_raw"].str.match(r"^\d{3}\s")]

# Validation check
first_val = sa4_raw["sa4_raw"].iloc[0]
print(f"  First SA4 row: '{first_val[:35]}' — {'✅ correct' if re.match(r'^\\d{3}\\s', str(first_val)) else '❌ WRONG — check skiprows'}")

# Split code and name
sa4_raw[["sa4_code", "sa4_name"]] = sa4_raw["sa4_raw"].str.split(" ", n=1, expand=True)
sa4_raw = sa4_raw.drop(columns=["sa4_raw"])

# Melt wide → long
date_columns = [c for c in sa4_raw.columns if c not in ["sa4_code", "sa4_name"]]

sa4_long = sa4_raw.melt(
    id_vars=["sa4_code", "sa4_name"],
    value_vars=date_columns,
    var_name="date_raw",
    value_name="unemployed"
)

# Convert ABS date format "Mar-26" → "2026-03-01"
def parse_abs_date(s):
    try:
        dt = pd.to_datetime(s, format="%b-%y")
        # pandas 2-digit year: 00-68=2000s, 69-99=1900s
        # All SA4 data is 2012 onwards so any 19xx must be corrected to 20xx
        if dt.year < 2000:
            dt = dt.replace(year=dt.year + 100)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None

sa4_long["date"] = sa4_long["date_raw"].apply(parse_abs_date)
sa4_long = sa4_long.dropna(subset=["date"])
sa4_long = sa4_long.drop(columns=["date_raw"])

# Convert unemployed to numeric
sa4_long["unemployed"] = pd.to_numeric(sa4_long["unemployed"], errors="coerce")
sa4_long = sa4_long.dropna(subset=["unemployed"])

# Reorder and sort
sa4_long = sa4_long[["sa4_code", "sa4_name", "date", "unemployed"]]
sa4_long = sa4_long.sort_values(["sa4_code", "date"]).reset_index(drop=True)

sa4_long.to_csv("data/sa4_unemployment_long.csv", index=False)
print(f"  → data/sa4_unemployment_long.csv ({len(sa4_long)} rows)")
print(f"  Regions: {sa4_long['sa4_code'].nunique()}")
print(f"  Date range: {sa4_long['date'].min()} → {sa4_long['date'].max()}")

# Write latest-month-only file for choropleth map
latest_date = sa4_long["date"].max()
sa4_latest = sa4_long[sa4_long["date"] == latest_date].copy()
sa4_latest.to_csv("data/sa4_unemployment_latest.csv", index=False)
print(f"  → data/sa4_unemployment_latest.csv ({len(sa4_latest)} regions, month: {latest_date})")


# ─────────────────────────────────────────────────────────────────────────────
# FINAL VALIDATION SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

checks = [
    ("H5 row count > 100",             len(h5) > 100),
    ("H5 unemployment_rate present",   h5["unemployment_rate"].notna().sum() > 50),
    ("H5 participation_rate present",  h5["participation_rate"].notna().sum() > 50),
    ("H5 average_hours_worked present",h5["average_hours_worked"].notna().sum() > 50),
    ("H5 employment_growth_yoy present",h5["employment_growth_yoy"].notna().sum() > 50),
    ("H4 row count > 50",              len(h4) > 50),
    ("H4 wage_growth_yoy present",     h4["wage_growth_yoy"].notna().sum() > 50),
    ("H4 productivity_growth present", h4["productivity_growth"].notna().sum() > 50),
    ("SA4 row count > 1000",           len(sa4_long) > 1000),
    ("SA4 regions > 80",               sa4_long["sa4_code"].nunique() > 80),
    ("SA4 latest file has rows",       len(sa4_latest) > 0),
    ("H5 date >= 1997",                h5["date"].min() >= "1997-01-01"),
    ("H4 date >= 1997",                h4["date"].min() >= "1997-01-01"),
    ("SA4 date >= 2012",               sa4_long["date"].min() >= "2012-01-01"),
]

all_passed = True
for label, result in checks:
    status = "✅" if result else "❌"
    if not result:
        all_passed = False
    print(f"  {status}  {label}")

print()
if all_passed:
    print("ALL CHECKS PASSED — data/ folder is ready for Vega-Lite.")
    print("Next step: add sa4_topo.json to data/ then push to GitHub.")
else:
    print("SOME CHECKS FAILED — review output above before pushing.")
