
import pandas as pd
import matplotlib

# Save the chart without opening another window
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent

reports = project / "reports"
assets = project / "assets"

assets.mkdir(parents=True, exist_ok=True)

# Load geographic sales report
df = pd.read_csv(
    reports / "geographic_sales_performance.csv"
)

print("RETAIL360 - GEOGRAPHIC SALES VISUALIZATION")
print("=" * 55)

# Check required columns
required_columns = [
    "customer_state",
    "Merchandise_Value_BRL",
    "Value_Share_Percent"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Required column missing: {column}"
        )

# Get top 10 states
top_10 = df.nlargest(
    10,
    "Merchandise_Value_BRL"
).copy()

# Convert merchandise value to millions
top_10["Value_Millions"] = (
    top_10["Merchandise_Value_BRL"] / 1_000_000
)

# Translate Brazilian state codes
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
    "CE": "Ceara",
    "PA": "Para",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MA": "Maranhao",
    "PB": "Paraiba",
    "RN": "Rio Grande do Norte",
    "AL": "Alagoas",
    "PI": "Piaui",
    "SE": "Sergipe",
    "RO": "Rondonia",
    "TO": "Tocantins",
    "AM": "Amazonas",
    "AC": "Acre",
    "AP": "Amapa",
    "RR": "Roraima"
}

top_10["State_Name"] = (
    top_10["customer_state"]
    .map(state_names)
    .fillna(top_10["customer_state"])
)

# Sort for horizontal visualization
top_10 = top_10.sort_values(
    "Value_Millions",
    ascending=True
).reset_index(drop=True)

# Create chart
fig, ax = plt.subplots(figsize=(13, 7))

colors = [
    "#173B70" if i == len(top_10) - 1
    else "#4C78A8"
    for i in range(len(top_10))
]

bars = ax.barh(
    top_10["State_Name"],
    top_10["Value_Millions"],
    color=colors,
    height=0.65
)

# Add values and percentages
for bar, (_, row) in zip(
    bars,
    top_10.iterrows()
):
    width = bar.get_width()

    label = (
        f'R$ {width:.2f}M '
        f'({row["Value_Share_Percent"]:.2f}%)'
    )

    ax.text(
        width + top_10["Value_Millions"].max() * 0.02,
        bar.get_y() + bar.get_height() / 2,
        label,
        va="center",
        fontsize=10
    )

# Add chart title and labels
ax.set_title(
    "Retail360 | Top 10 States by Merchandise Value",
    fontsize=17,
    fontweight="bold",
    pad=22
)

ax.set_xlabel(
    "Delivered Merchandise Value (R$ Millions)",
    fontsize=11
)

ax.set_ylabel("Customer State")

# Improve chart formatting
ax.set_xlim(
    0,
    top_10["Value_Millions"].max() * 1.4
)

ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.25
)

ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# Add source information
fig.text(
    0.5,
    0.01,
    "Source: Olist | Historical delivered orders | "
    "Geography based on customer state",
    ha="center",
    fontsize=9,
    color="gray"
)

plt.tight_layout(rect=[0, 0.04, 1, 1])

# Save chart
output_file = (
    assets / "top_10_states_sales.png"
)

plt.savefig(
    output_file,
    dpi=200,
    bbox_inches="tight"
)

plt.close(fig)

# Print business findings
top_state = top_10.iloc[-1]

print("\nTOP PERFORMING STATE:")
print("State:", top_state["State_Name"])

print(
    "Merchandise Value (BRL):",
    round(top_state["Merchandise_Value_BRL"], 2)
)

print(
    "Share of Total Merchandise Value:",
    f'{top_state["Value_Share_Percent"]:.2f}%'
)

print("\nGEOGRAPHIC VISUALIZATION COMPLETED!")
print("Chart saved to:", output_file)
