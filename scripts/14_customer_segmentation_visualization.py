
import pandas as pd
import matplotlib

# Save the chart without opening a separate window
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from pathlib import Path

# Locate our project folders
project = Path(__file__).resolve().parent.parent

reports = project / "reports"
assets = project / "assets"

assets.mkdir(parents=True, exist_ok=True)

# Read our customer KPI report
df = pd.read_csv(
    reports / "customer_repeat_summary.csv"
)

print("RETAIL360 - CUSTOMER SEGMENTATION")
print("=" * 55)

# Extract customer metrics
total_customers = int(
    df.loc[0, "Unique_Customers"]
)

one_time = int(
    df.loc[0, "One_Time_Customers"]
)

repeat = int(
    df.loc[0, "Repeat_Customers"]
)

# Validate our data
if total_customers <= 0:
    raise ValueError("No customer records found.")

if one_time + repeat != total_customers:
    raise ValueError(
        "Customer segment totals do not match!"
    )

# Calculate percentages
one_time_percent = (
    one_time / total_customers * 100
)

repeat_percent = (
    repeat / total_customers * 100
)

# Display KPI results
print("\nCUSTOMER SEGMENTATION SUMMARY")
print("-" * 40)

print("Total Unique Customers:", total_customers)
print("One-Time Customers:", one_time)
print("Repeat Customers:", repeat)

print(
    f"One-Time Customer Rate: {one_time_percent:.2f}%"
)

print(
    f"Repeat Customer Rate: {repeat_percent:.2f}%"
)

# Prepare our chart data
segments = [
    "One-Time Customers",
    "Repeat Customers"
]

counts = [one_time, repeat]

percentages = [
    one_time_percent,
    repeat_percent
]

colors = ["#244D87", "#219E8F"]

# Create the chart
fig, ax = plt.subplots(figsize=(11, 5.5))

bars = ax.barh(
    segments,
    counts,
    color=colors,
    height=0.45
)

# Display one-time customers at the top
ax.invert_yaxis()

# Add labels
max_count = max(counts)

for bar, count, percent in zip(
    bars,
    counts,
    percentages
):
    ax.text(
        count + max_count * 0.02,
        bar.get_y() + bar.get_height() / 2,
        f"{count:,} ({percent:.2f}%)",
        va="center",
        fontsize=11,
        fontweight="bold"
    )

# Add chart title
ax.set_title(
    "Retail360 | Customer Purchase Segmentation",
    fontsize=17,
    fontweight="bold",
    pad=25
)

ax.set_xlabel(
    "Number of Unique Customers",
    fontsize=11
)

ax.set_xlim(0, max_count * 1.35)

# Format the numerical axis
ax.xaxis.set_major_formatter(
    StrMethodFormatter("{x:,.0f}")
)

# Add professional formatting
ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.25
)

ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Add data context
fig.text(
    0.5,
    0.05,
    "Source: Olist | Historical delivered orders | "
    "Repeat = 2 or more delivered orders",
    ha="center",
    fontsize=9,
    color="gray"
)

plt.tight_layout(rect=[0, 0.12, 1, 1])

# Save chart
output_file = (
    assets / "customer_segmentation_chart.png"
)

plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

# Save an aggregated report
segment_summary = pd.DataFrame({
    "Customer_Segment": segments,
    "Customer_Count": counts,
    "Percentage": [
        round(value, 2) for value in percentages
    ]
})

segment_summary.to_csv(
    reports / "customer_segment_summary.csv",
    index=False
)

print("\nCustomer visualization created successfully!")
print("Chart saved to:", output_file)
print("Customer segment summary saved successfully!")
