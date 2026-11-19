
import pandas as pd
import matplotlib

# Save charts without opening another window
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent

reports = project / "reports"
assets = project / "assets"

assets.mkdir(parents=True, exist_ok=True)

print("RETAIL360 - CUSTOMER SATISFACTION VISUALIZATION")
print("=" * 55)

# Load customer satisfaction report
file_path = reports / "customer_satisfaction_by_delivery.csv"

df = pd.read_csv(file_path)

# Check required columns
required_columns = [
    "Delivery_Status",
    "Reviewed_Orders",
    "Average_Review_Score",
    "Low_Rating_Percent"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Missing required column: {column}"
        )

# Arrange delivery categories
df = (
    df.set_index("Delivery_Status")
    .reindex(["On Time", "Late"])
    .reset_index()
)

if df[required_columns[1:]].isna().any().any():
    raise ValueError(
        "Missing values in customer satisfaction report."
    )

# Prepare chart data
statuses = df["Delivery_Status"].tolist()

average_scores = df[
    "Average_Review_Score"
].tolist()

low_rating_rates = df[
    "Low_Rating_Percent"
].tolist()

review_counts = df[
    "Reviewed_Orders"
].astype(int).tolist()

colors = ["#218B68", "#E07B39"]

# Create two charts side by side
fig, axes = plt.subplots(
    1, 2, figsize=(13, 6)
)

# CHART 1: Average customer rating
bars1 = axes[0].bar(
    statuses,
    average_scores,
    color=colors,
    width=0.55
)

axes[0].set_title(
    "Average Customer Review Rating",
    fontsize=14,
    fontweight="bold"
)

axes[0].set_ylabel("Average Rating (1-5 Stars)")
axes[0].set_ylim(0, 5.5)

# Add rating labels
for bar, score in zip(bars1, average_scores):
    axes[0].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.12,
        f"{score:.2f} / 5",
        ha="center",
        fontweight="bold",
        fontsize=11
    )

# CHART 2: Low-rating percentage
bars2 = axes[1].bar(
    statuses,
    low_rating_rates,
    color=colors,
    width=0.55
)

axes[1].set_title(
    "Low Customer Rating Percentage",
    fontsize=14,
    fontweight="bold"
)

axes[1].set_ylabel("Reviews Rated 1 or 2 Stars (%)")
axes[1].set_ylim(0, 105)

# Add percentage labels
for bar, rate in zip(bars2, low_rating_rates):
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        f"{rate:.2f}%",
        ha="center",
        fontweight="bold",
        fontsize=11
    )

# Add professional formatting
for ax in axes:
    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.25
    )

    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

# Add reviewed order counts
for ax in axes:
    for i, count in enumerate(review_counts):
        ax.text(
            i, -0.14,
            f"n = {count:,} reviewed orders",
            ha="center",
            va="top",
            fontsize=9,
            transform=ax.get_xaxis_transform(),
            clip_on=False
        )

# Add overall title
fig.suptitle(
    "Retail360 | Delivery Timing & Customer Satisfaction",
    fontsize=17,
    fontweight="bold"
)

# Add source and methodology note
fig.text(
    0.5, 0.025,
    "Source: Olist | Delivered orders purchased Feb 2017-Jul 2018 "
    "| Latest recorded review per order",
    ha="center",
    fontsize=9,
    color="gray"
)

plt.tight_layout(rect=[0, 0.10, 1, 0.91])

# Save visualization
output_file = (
    assets / "customer_satisfaction_dashboard.png"
)

plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

# Display actual findings
print("\nCUSTOMER SATISFACTION COMPARISON")
print("-" * 45)

print(
    df[required_columns].to_string(index=False)
)

print("\nVisualization created successfully!")
print("Chart saved to:", output_file)
