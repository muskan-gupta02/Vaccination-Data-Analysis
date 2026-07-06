"""
Vaccination Data Analysis Project
Data Cleaning + MySQL Loading
"""

import pandas as pd
import numpy as np
import mysql.connector
import warnings
warnings.filterwarnings('ignore')

DB_CONFIG = {
    "host":     "127.0.0.1",
    "port":     3306,
    "user":     "root",
    "password": "Muskan@243",
}

def load_and_clean_coverage():
    df = pd.read_excel("coverage-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={"dodge": "doses"}, errors="ignore", inplace=True)
    df["year"]          = pd.to_numeric(df["year"], errors="coerce")
    df["target_number"] = pd.to_numeric(df["target_number"], errors="coerce")
    df["doses"]         = pd.to_numeric(df["doses"], errors="coerce")
    df["coverage"]      = pd.to_numeric(df["coverage"], errors="coerce").clip(0, 100)
    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year", "antigen"], inplace=True)
    print(f"[coverage]       rows={len(df)}")
    return df

def load_and_clean_incidence():
    df = pd.read_excel("incidence-rate-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()
    df["year"]           = pd.to_numeric(df["year"], errors="coerce")
    df["incidence_rate"] = pd.to_numeric(df["incidence_rate"], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year", "disease"], inplace=True)
    print(f"[incidence]      rows={len(df)}")
    return df

def load_and_clean_reported_cases():
    df = pd.read_excel("reported-cases-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()
    df["year"]  = pd.to_numeric(df["year"], errors="coerce")
    df["cases"] = pd.to_numeric(df["cases"], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year", "disease"], inplace=True)
    print(f"[reported_cases] rows={len(df)}")
    return df

def load_and_clean_vax_intro():
    df = pd.read_excel("vaccine-introduction-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={"iso_3_code": "code", "countryname": "name",
                        "description": "vaccine_description"}, inplace=True)
    df["year"]  = pd.to_numeric(df["year"], errors="coerce")
    df["intro"] = df["intro"].astype(str).str.strip()
    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year"], inplace=True)
    print(f"[vax_intro]      rows={len(df)}")
    return df

def load_and_clean_vax_schedule():
    df = pd.read_excel("vaccine-schedule-data.xlsx", sheet_name="Data")
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={"iso_3_code": "code", "countryname": "name"}, inplace=True)
    df["year"]           = pd.to_numeric(df["year"], errors="coerce")
    df["schedulerounds"] = pd.to_numeric(df["schedulerounds"], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.dropna(subset=["code", "year", "vaccinecode"], inplace=True)
    print(f"[vax_schedule]   rows={len(df)}")
    return df

def get_conn(db=None):
    cfg = DB_CONFIG.copy()
    if db:
        cfg["database"] = db
    return mysql.connector.connect(**cfg)

def setup_database():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS vaccination_db CHARACTER SET utf8mb4;")
    cur.execute("USE vaccination_db;")

    tables = {
        "coverage_data": """
            CREATE TABLE IF NOT EXISTS coverage_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `group` VARCHAR(2000), code VARCHAR(2000), name VARCHAR(500),
                year INT, antigen VARCHAR(500), antigen_description TEXT,
                coverage_category VARCHAR(500), coverage_category_description TEXT,
                target_number DOUBLE, doses DOUBLE, coverage DOUBLE
            )""",
        "incidence_rate_data": """
            CREATE TABLE IF NOT EXISTS incidence_rate_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `group` VARCHAR(2000), code VARCHAR(2000), name VARCHAR(500),
                year INT, disease VARCHAR(500), disease_description TEXT,
                denominator VARCHAR(500), incidence_rate DOUBLE
            )""",
        "reported_cases_data": """
            CREATE TABLE IF NOT EXISTS reported_cases_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `group` VARCHAR(2000), code VARCHAR(2000), name VARCHAR(500),
                year INT, disease VARCHAR(500), disease_description TEXT,
                cases DOUBLE
            )""",
        "vaccine_introduction_data": """
            CREATE TABLE IF NOT EXISTS vaccine_introduction_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(2000), name VARCHAR(500), who_region VARCHAR(500),
                year INT, vaccine_description TEXT, intro VARCHAR(2000)
            )""",
        "vaccine_schedule_data": """
            CREATE TABLE IF NOT EXISTS vaccine_schedule_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(2000), name VARCHAR(500), who_region VARCHAR(500),
                year INT, vaccinecode VARCHAR(2000), vaccine_description TEXT,
                schedulerounds DOUBLE, targetpop VARCHAR(500),
                targetpop_description TEXT, geoarea VARCHAR(500),
                ageadministered VARCHAR(500), sourcecomment TEXT
            )"""
    }

    for tname, ddl in tables.items():
        cur.execute(ddl)
        print(f"  Table ready: {tname}")

    conn.commit()
    cur.close()
    conn.close()
    print("Database ready!\n")

def clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    return v

def df_to_mysql(df, table, cols):
    conn = get_conn("vaccination_db")
    cur  = conn.cursor()
    cur.execute(f"DELETE FROM `{table}`")
    col_str = ", ".join([f"`{c}`" for c in cols])
    ph      = ", ".join(["%s"] * len(cols))
    sql     = f"INSERT INTO `{table}` ({col_str}) VALUES ({ph})"
    data    = [tuple(clean_val(v) for v in row)
               for row in df[cols].itertuples(index=False)]
    cur.executemany(sql, data)
    conn.commit()
    print(f"  Inserted {cur.rowcount} rows -> {table}")
    cur.close()
    conn.close()

def load_all(cov, inc, rep, intro, sched):
    df_to_mysql(cov, "coverage_data",
        ["group","code","name","year","antigen","antigen_description",
         "coverage_category","coverage_category_description","target_number","doses","coverage"])
    df_to_mysql(inc, "incidence_rate_data",
        ["group","code","name","year","disease","disease_description","denominator","incidence_rate"])
    df_to_mysql(rep, "reported_cases_data",
        ["group","code","name","year","disease","disease_description","cases"])
    df_to_mysql(intro, "vaccine_introduction_data",
        ["code","name","who_region","year","vaccine_description","intro"])
    df_to_mysql(sched, "vaccine_schedule_data",
        ["code","name","who_region","year","vaccinecode","vaccine_description",
         "schedulerounds","targetpop","targetpop_description","geoarea","ageadministered","sourcecomment"])

if __name__ == "__main__":
    print("=" * 50)
    print("STEP 1 — Cleaning Data")
    print("=" * 50)
    cov   = load_and_clean_coverage()
    inc   = load_and_clean_incidence()
    rep   = load_and_clean_reported_cases()
    intro = load_and_clean_vax_intro()
    sched = load_and_clean_vax_schedule()

    print("\n" + "=" * 50)
    print("STEP 2 — Setting up MySQL")
    print("=" * 50)
    setup_database()

    print("=" * 50)
    print("STEP 3 — Loading into MySQL")
    print("=" * 50)
    load_all(cov, inc, rep, intro, sched)

    print("\nAll done! vaccination_db is ready in MySQL.")