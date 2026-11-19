
import pandas as pd
import matplotlib

# Save the chart directly without opening
# a separate Matplotlib window
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Locate the project folders
project = Path(__file__).resolve().parent.parent

reports = project / "reports"
assets = project / "assets"

# Load monthly sales data
df = pd.read_csv(
    reports / "monthly_sales_trends.csv"
)

print("RETAIL360 - MONTHLY SALES VISUALIZATION")
print("=" * 55)

# Convert month into a date
df["Month"] = pd.to_datetime(
    df["purchase_month"],
    format="%Y-%m"
)

# Sort chronologically
df = df.sort_values("Month")

# Convert merchandise value to millions
df["Value_Millions"] = (
    df["Merchandise_Value_BRL"] / 1_000_000
)

# Create the chart
fig, ax = plt.subplots(figsize=(13, 6))

ax.plot(
    df["Month"],
    df["Value_Millions"],
    color="#2563EB",
    linewidth=2.5,
    marker="o",
    markersize=4
)

# Highlight the highest-value month
best_month = df.loc[
    df["Merchandise_Value_BRL"].idxmax()
]

ax.scatter(
    best_month["Month"],
    best_month["Value_Millions"],
    color="#DC2626",
    s=100,
    zorder=5
)

ax.annotate(
    f'Highest: R$ {best_month["Value_Millions"]:.2f}M',
    xy=(
        best_month["Month"],
        best_month["Value_Millions"]
    ),
    xytext=(0, 18),
    textcoords="offset points",
    ha="center",
    fontsize=10,
    fontweight="bold"
)

# Add chart title and labels
ax.set_title(
    "Retail360 | Monthly Merchandise Value Trend",
    fontsize=16,
    fontweight="bold",
    pad=20
)

ax.set_xlabel("Purchase Month")
ax.set_ylabel("Delivered Merchandise Value (R$ Millions)")

# Format the date axis
ax.xaxis.set_major_locator(
    mdates.MonthLocator(interval=3)
)

ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%b %Y")
)

plt.xticks(rotation=45)

# Add professional formatting
ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Add data source information
fig.text(
    0.5,
    0.01,
    "Source: Olist | Historical purchase months | "
    "Eventually delivered orders | "
    "Boundary months may be incomplete",
    ha="center",
    fontsize=9,
    color="gray"
)

plt.tight_layout(rect=[0, 0.06, 1, 1])

# Save the chart
output_file = assets / "monthly_sales_trend.png"

plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

# Display results
print("\nHighest merchandise value month:")
print(best_month["purchase_month"])

print("\nMerchandise Value (BRL):")
print(round(best_month["Merchandise_Value_BRL"], 2))

print("\nMonthly sales chart created successfully!")
print("Chart saved to:", output_file)
