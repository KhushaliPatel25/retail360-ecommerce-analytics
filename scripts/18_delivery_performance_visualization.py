
import pandas as pd
import matplotlib

# Create chart without opening a separate window
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path

# Locate our project folders
project = Path(__file__).resolve().parent.parent

reports = project / "reports"
assets = project / "assets"

assets.mkdir(parents=True, exist_ok=True)

print("RETAIL360 - DELIVERY PERFORMANCE VISUALIZATION")
print("=" * 55)

# Load delivery performance reports
summary = pd.read_csv(
    reports / "delivery_performance_summary.csv"
)

states = pd.read_csv(
    reports / "delivery_performance_by_state.csv"
)

# Get overall delivery performance
overall_rate = float(
    summary.loc[0, "On_Time_Rate_Percent"]
)

average_days = float(
    summary.loc[0, "Average_Delivery_Days"]
)

total_orders = int(
    summary.loc[0, "Analyzed_Orders"]
)

print("\nOVERALL DELIVERY PERFORMANCE")
print("-" * 40)

print("Analyzed Delivered Orders:", total_orders)

print(
    f"Overall On-Time Delivery Rate: {overall_rate:.2f}%"
)

print(
    f"Average Delivery Days: {average_days:.2f}"
)

# Find top 10 states by delivery volume
top_10 = states.nlargest(
    10,
    "Delivered_Orders"
).copy()

# Translate state abbreviations
state_names = {
    "SP": "Sao Paulo",
    "RJ": "Rio de Janeiro",
    "MG": "Minas Gerais",
    "RS": "Rio Grande do Sul",
    "PR": "Parana",
    "SC": "Santa Catarina",
    "BA": "Bahia",
    "DF": "Distrito Federal",
    "ES": "Espirito Santo",
    "GO": "Goias",
    "PE": "Pernambuco",
    "CE": "Ceara"
}

top_10["State_Name"] = (
    top_10["customer_state"]
    .map(state_names)
    .fillna(top_10["customer_state"])
)

# Sort states by on-time rate
top_10 = top_10.sort_values(
    "On_Time_Rate_Percent",
    ascending=True
).reset_index(drop=True)

# Choose chart colours
colors = [
    "#218B68" if rate >= overall_rate
    else "#E58A42"
    for rate in top_10["On_Time_Rate_Percent"]
]

# Create horizontal bar chart
fig, ax = plt.subplots(figsize=(13, 7))

bars = ax.barh(
    top_10["State_Name"],
    top_10["On_Time_Rate_Percent"],
    color=colors,
    height=0.65
)

# Add labels to the bars
for bar, (_, row) in zip(
    bars,
    top_10.iterrows()
):
    rate = row["On_Time_Rate_Percent"]
    count = int(row["Delivered_Orders"])

    label = f"{rate:.1f}% | {count:,} orders"

    ax.text(
        rate + 1,
        bar.get_y() + bar.get_height() / 2,
        label,
        va="center",
        fontsize=10
    )

# Add overall performance reference line
ax.axvline(
    overall_rate,
    color="#173B70",
    linestyle="--",
    linewidth=2,
    label=f"Overall On-Time Rate: {overall_rate:.2f}%"
)

# Add professional titles
ax.set_title(
    "Retail360 | On-Time Delivery Performance by State",
    fontsize=17,
    fontweight="bold",
    pad=22
)

ax.set_xlabel(
    "On-Time Delivery Rate (%)",
    fontsize=11
)

ax.set_ylabel("Customer State")

# Format chart
ax.set_xlim(0, 125)

ax.set_xticks([0, 25, 50, 75, 100])

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.25
)

ax.set_axisbelow(True)

ax.legend(
    loc="lower right",
    fontsize=10
)

for spine in ax.spines.values():
    spine.set_visible(False)

# Add data source information
fig.text(
    0.5,
    0.01,
    "Source: Olist | Purchases Feb 2017 - Jul 2018 | "
    "Delivered orders with valid dates | "
    "Top 10 states by delivery volume",
    ha="center",
    fontsize=9,
    color="gray"
)

plt.tight_layout(rect=[0, 0.05, 1, 1])

# Save chart
output_file = (
    assets / "delivery_performance_by_state.png"
)

plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

# Show business findings
print("\nTOP 10 STATES - DELIVERY PERFORMANCE")

print(
    top_10[
        [
            "State_Name",
            "Delivered_Orders",
            "Average_Delivery_Days",
            "On_Time_Rate_Percent"
        ]
    ].to_string(index=False)
)

print("\nDELIVERY PERFORMANCE VISUALIZATION COMPLETED!")

print("Chart saved to:", output_file)
