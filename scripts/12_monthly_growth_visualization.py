
import pandas as pd
import matplotlib

# Save chart without opening a separate window
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent

reports = project / "reports"
assets = project / "assets"

# Load monthly growth report
df = pd.read_csv(
    reports / "monthly_growth_analysis.csv"
)

print("RETAIL360 - MONTHLY GROWTH VISUALIZATION")
print("=" * 55)

# Prepare and sort the data
df["Month"] = pd.to_datetime(
    df["purchase_month"],
    format="%Y-%m"
)

df["MoM_Growth_Percent"] = pd.to_numeric(
    df["MoM_Growth_Percent"],
    errors="coerce"
)

df = df.sort_values(
    "Month"
).reset_index(drop=True)

# Select a comparable reporting period
# Exclude sparse startup and boundary months

chart_data = df.loc[
    (df["Month"] >= "2017-02-01") &
    (df["Month"] <= "2018-07-01")
].copy()

# Keep only valid growth calculations
chart_data = chart_data.dropna(
    subset=["MoM_Growth_Percent"]
).reset_index(drop=True)

if chart_data.empty:
    raise ValueError(
        "No valid monthly growth data available."
    )

# Set bar colours
# Green = Positive growth
# Red = Negative growth

colors = [
    "#218B68" if value >= 0 else "#DC5B57"
    for value in chart_data["MoM_Growth_Percent"]
]

# Create the chart
fig, ax = plt.subplots(figsize=(14, 7))

positions = range(len(chart_data))

bars = ax.bar(
    positions,
    chart_data["MoM_Growth_Percent"],
    color=colors,
    width=0.65
)

# Add horizontal zero line
ax.axhline(
    y=0,
    color="#374151",
    linewidth=1
)

# Identify strongest and weakest months

highest_index = chart_data[
    "MoM_Growth_Percent"
].idxmax()

lowest_index = chart_data[
    "MoM_Growth_Percent"
].idxmin()

# Highlight the highest and lowest growth values
for index in sorted(set([highest_index, lowest_index])):

    value = chart_data.loc[
        index, "MoM_Growth_Percent"
    ]

    ax.annotate(
        f"{value:+.1f}%",
        xy=(index, value),
        xytext=(0, 8 if value >= 0 else -16),
        textcoords="offset points",
        ha="center",
        fontsize=10,
        fontweight="bold"
    )

# Format month labels

labels = chart_data["Month"].dt.strftime("%b %Y")

ax.set_xticks(list(positions))

ax.set_xticklabels(
    labels,
    rotation=45,
    ha="right",
    fontsize=9
)

# Add title and axis labels

ax.set_title(
    "Retail360 | Month-over-Month Merchandise Value Growth",
    fontsize=16,
    fontweight="bold",
    pad=20
)

ax.set_xlabel("Purchase Month")

ax.set_ylabel("Month-over-Month Growth (%)")

# Add professional formatting

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

ax.set_axisbelow(True)

ax.margins(y=0.2)

for spine in ax.spines.values():
    spine.set_visible(False)

# Add data source information

fig.text(
    0.5,
    0.01,
    "Source: Olist | Delivered-order merchandise value | "
    "Reporting window: Feb 2017 - Jul 2018",
    ha="center",
    fontsize=9,
    color="gray"
)

plt.tight_layout(rect=[0, 0.05, 1, 1])

# Save the chart

output_file = assets / "monthly_growth_chart.png"

plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

# Display business findings

print("\nHIGHEST MONTHLY GROWTH:")

print(
    chart_data.loc[
        highest_index,
        ["purchase_month", "MoM_Growth_Percent"]
    ]
)

print("\nLOWEST MONTHLY GROWTH:")

print(
    chart_data.loc[
        lowest_index,
        ["purchase_month", "MoM_Growth_Percent"]
    ]
)

print("\nMonthly growth chart created successfully!")

print("Chart saved to:", output_file)
