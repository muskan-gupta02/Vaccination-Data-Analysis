"""
Vaccination Data Analysis Project
Data Cleaning — saves cleaned CSVs (no MySQL needed)
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════
# LOAD & CLEAN
# ══════════════════════════════════════════════

def load_and_clean_coverage():
    df = pd.read_excel("coverage-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={"dodge": "doses"}, errors="ignore", inplace=True)

    df["year"]          = pd.to_numeric(df["year"], errors="coerce")
    df["target_number"] = pd.to_numeric(df["target_number"], errors="coerce")
    df["doses"]         = pd.to_numeric(df["doses"], errors="coerce")
    df["coverage"]      = pd.to_numeric(df["coverage"], errors="coerce")
    df["coverage"]      = df["coverage"].clip(0, 100)

    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year", "antigen"], inplace=True)

    print(f"[coverage]       rows={len(df)}  missing_coverage={df['coverage'].isna().sum()}")
    return df


def load_and_clean_incidence():
    df = pd.read_excel("incidence-rate-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()

    df["year"]          = pd.to_numeric(df["year"], errors="coerce")
    df["incidence_rate"]= pd.to_numeric(df["incidence_rate"], errors="coerce")

    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year", "disease"], inplace=True)

    print(f"[incidence]      rows={len(df)}  missing_rate={df['incidence_rate'].isna().sum()}")
    return df


def load_and_clean_reported_cases():
    df = pd.read_excel("reported-cases-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()

    df["year"]  = pd.to_numeric(df["year"], errors="coerce")
    df["cases"] = pd.to_numeric(df["cases"], errors="coerce")

    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year", "disease"], inplace=True)

    print(f"[reported_cases] rows={len(df)}  missing_cases={df['cases'].isna().sum()}")
    return df


def load_and_clean_vax_intro():
    df = pd.read_excel("vaccine-introduction-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={
        "iso_3_code":  "code",
        "countryname": "name",
        "description": "vaccine_description"
    }, inplace=True)

    df["year"]  = pd.to_numeric(df["year"], errors="coerce")
    df["intro"] = df["intro"].astype(str).str.strip()

    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year"], inplace=True)

    print(f"[vax_intro]      rows={len(df)}")
    return df


def load_and_clean_vax_schedule():
    df = pd.read_excel("vaccine-schedule-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={
        "iso_3_code":  "code",
        "countryname": "name"
    }, inplace=True)

    df["year"]          = pd.to_numeric(df["year"], errors="coerce")
    df["schedulerounds"]= pd.to_numeric(df["schedulerounds"], errors="coerce")

    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year", "vaccinecode"], inplace=True)

    print(f"[vax_schedule]   rows={len(df)}")
    return df


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("Loading & Cleaning Data...")
    print("=" * 50)

    cov   = load_and_clean_coverage()
    inc   = load_and_clean_incidence()
    rep   = load_and_clean_reported_cases()
    intro = load_and_clean_vax_intro()
    sched = load_and_clean_vax_schedule()

    cov.to_csv("cleaned_coverage.csv",   index=False)
    inc.to_csv("cleaned_incidence.csv",  index=False)
    rep.to_csv("cleaned_cases.csv",      index=False)
    intro.to_csv("cleaned_intro.csv",    index=False)
    sched.to_csv("cleaned_schedule.csv", index=False)

    print("\nDone! 5 cleaned CSV files saved in project folder.")
