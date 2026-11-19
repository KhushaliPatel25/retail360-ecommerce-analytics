
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Locate our project
project = Path(__file__).resolve().parent.parent

reports = project / "reports"
assets = project / "assets"

# Read our Top 10 category report
df = pd.read_csv(
    reports / "top_10_product_categories.csv"
)

# Prepare category names
df["Category_Name"] = (
    df["category"]
    .str.replace("_", " ", regex=False)
    .str.title()
)

# Sort values for a horizontal bar chart
df = df.sort_values(
    "Merchandise_Value_BRL",
    ascending=True
)

# Convert values to millions
df["Value_Millions"] = (
    df["Merchandise_Value_BRL"] / 1_000_000
)

# Create chart
fig, ax = plt.subplots(figsize=(12, 7))

bars = ax.barh(
    df["Category_Name"],
    df["Value_Millions"],
    color="#4C78A8",
    height=0.65
)

# Highlight the highest category
bars[-1].set_color("#173B70")

# Add value labels
for bar in bars:
    width = bar.get_width()

    ax.text(
        width + 0.02,
        bar.get_y() + bar.get_height() / 2,
        f"R$ {width:.2f}M",
        va="center",
        fontsize=10
    )

# Add professional formatting
ax.set_title(
    "Top 10 Product Categories by Merchandise Value",
    fontsize=16,
    fontweight="bold",
    pad=20
)

ax.set_xlabel(
    "Delivered Merchandise Value (R$ Millions)",
    fontsize=11
)

ax.set_ylabel("")

ax.set_xlim(
    0,
    df["Value_Millions"].max() * 1.22
)

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
    0.5, 0.01,
    "Source: Olist E-Commerce Dataset | Historical data | Delivered orders only",
    ha="center",
    fontsize=9,
    color="gray"
)

plt.tight_layout(rect=[0, 0.04, 1, 1])

# Save chart
output_file = assets / "top_10_categories.png"

plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)

print("Visualization created successfully!")
print("Chart saved to:", output_file)

# Display chart
plt.show()
