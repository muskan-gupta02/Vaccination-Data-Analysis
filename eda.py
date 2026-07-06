"""
Vaccination Data Analysis Project
EDA — Run AFTER data_cleaning.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Load cleaned CSVs
cov   = pd.read_csv("cleaned_coverage.csv")
inc   = pd.read_csv("cleaned_incidence.csv")
rep   = pd.read_csv("cleaned_cases.csv")
intro = pd.read_csv("cleaned_intro.csv")
sched = pd.read_csv("cleaned_schedule.csv")

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

print("Data loaded:")
for name, df in [("coverage", cov), ("incidence", inc),
                 ("cases", rep), ("intro", intro), ("schedule", sched)]:
    print(f"  {name}: {df.shape}")


# ── Chart 1: Coverage Trends ──────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Vaccination Coverage Analysis", fontsize=14, fontweight="bold")

cov_trend = cov.groupby("year")["coverage"].mean().reset_index()
axes[0,0].plot(cov_trend["year"], cov_trend["coverage"], marker="o", color="#2196F3")
axes[0,0].set_title("Global Avg Coverage Over Years")
axes[0,0].set_xlabel("Year"); axes[0,0].set_ylabel("Coverage (%)")

top_antigens = cov.groupby("antigen_description")["coverage"].mean().nlargest(10)
top_antigens.sort_values().plot(kind="barh", ax=axes[0,1], color="#4CAF50")
axes[0,1].set_title("Top 10 Vaccines by Avg Coverage")
axes[0,1].set_xlabel("Coverage (%)")

axes[1,0].hist(cov["coverage"].dropna(), bins=30, color="#FF9800", edgecolor="white")
axes[1,0].set_title("Coverage Distribution")
axes[1,0].set_xlabel("Coverage (%)"); axes[1,0].set_ylabel("Count")

cov_with_region = cov.merge(intro[["code","who_region"]].drop_duplicates(), on="code", how="left")
region_cov = cov_with_region.groupby("who_region")["coverage"].mean().dropna()
region_cov.sort_values().plot(kind="barh", ax=axes[1,1], color="#9C27B0")
axes[1,1].set_title("Avg Coverage by WHO Region")
axes[1,1].set_xlabel("Coverage (%)")

plt.tight_layout()
plt.savefig("chart1_coverage.png")
plt.show()
print("Saved: chart1_coverage.png")


# ── Chart 2: Disease Incidence ────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Disease Incidence Analysis", fontsize=14, fontweight="bold")

top_diseases = inc.groupby("disease_description")["incidence_rate"].mean().nlargest(8)
top_diseases.sort_values().plot(kind="barh", ax=axes[0], color="#F44336")
axes[0].set_title("Top 8 Diseases by Avg Incidence Rate")
axes[0].set_xlabel("Incidence Rate")

top3 = top_diseases.index[:3]
disease_trend = inc[inc["disease_description"].isin(top3)].groupby(
    ["year","disease_description"])["incidence_rate"].mean().reset_index()
for d in top3:
    sub = disease_trend[disease_trend["disease_description"] == d]
    axes[1].plot(sub["year"], sub["incidence_rate"], marker="o", label=d[:30])
axes[1].set_title("Top 3 Disease Incidence Over Years")
axes[1].set_xlabel("Year"); axes[1].set_ylabel("Incidence Rate")
axes[1].legend(fontsize=7)

plt.tight_layout()
plt.savefig("chart2_incidence.png")
plt.show()
print("Saved: chart2_incidence.png")


# ── Chart 3: Coverage vs Incidence ───────────
disease_map = {
    "MEASLES":    "MCV1",
    "DIPHTHERIA": "DIPHCV1",
    "PERTUSSIS":  "PAB",
    "POLIO":      "POL3"
}

rows = []
for disease, antigen in disease_map.items():
    c = cov[cov["antigen"] == antigen].groupby(["code","year"])["coverage"].mean().reset_index()
    i = inc[inc["disease"] == disease][["code","year","incidence_rate"]]
    merged = c.merge(i, on=["code","year"])
    merged["disease"] = disease
    rows.append(merged)
corr_df = pd.concat(rows, ignore_index=True)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle("Coverage vs Incidence Rate", fontsize=13, fontweight="bold")

for ax, disease in zip(axes.flat, disease_map.keys()):
    sub = corr_df[corr_df["disease"] == disease].dropna()
    if len(sub) > 5:
        ax.scatter(sub["coverage"], sub["incidence_rate"], alpha=0.4, color="#2196F3", s=10)
        z = np.polyfit(sub["coverage"], sub["incidence_rate"], 1)
        x_line = np.linspace(sub["coverage"].min(), sub["coverage"].max(), 100)
        ax.plot(x_line, np.poly1d(z)(x_line), "r--", linewidth=1.5)
        r = sub[["coverage","incidence_rate"]].corr().iloc[0,1]
        ax.set_title(f"{disease}  (r={r:.2f})")
    else:
        ax.set_title(f"{disease} (insufficient data)")
    ax.set_xlabel("Coverage (%)"); ax.set_ylabel("Incidence Rate")

plt.tight_layout()
plt.savefig("chart3_correlation.png")
plt.show()
print("Saved: chart3_correlation.png")


# ── Chart 4: Vaccine Introduction ────────────
intro_counts = intro.groupby(["vaccine_description","intro"]).size().unstack(fill_value=0)
top_v = intro_counts.sum(axis=1).nlargest(10).index
intro_counts.loc[top_v].plot(kind="bar", figsize=(13,5), colormap="Set2", edgecolor="white")
plt.title("Top 10 Vaccines — Countries Introduced vs Not")
plt.ylabel("Number of Countries")
plt.xticks(rotation=30, ha="right", fontsize=8)
plt.tight_layout()
plt.savefig("chart4_intro.png")
plt.show()
print("Saved: chart4_intro.png")


# ── Summary ───────────────────────────────────
print("\n─── Key Stats ───")
print(f"Countries : {cov['code'].nunique()}")
print(f"Year range: {int(cov['year'].min())} – {int(cov['year'].max())}")
print(f"Antigens  : {cov['antigen'].nunique()}")
print(f"Diseases  : {inc['disease'].nunique()}")
print(f"Avg coverage: {cov['coverage'].mean():.1f}%")
