
import pandas as pd
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent

reports = project / "reports"

# Load the category performance report
df = pd.read_csv(
    reports / "all_category_performance.csv"
)

print("RETAIL360 - CATEGORY KPI ANALYSIS")
print("=" * 55)

# Calculate average item price
df["Average_Item_Price_BRL"] = (
    df["Merchandise_Value_BRL"] / df["Items_Sold"]
).round(2)

# Calculate freight as a percentage
# of merchandise value
df["Freight_to_Value_Percent"] = (
    df["Freight_Value_BRL"]
    / df["Merchandise_Value_BRL"].replace(0, float("nan"))
    * 100
).round(2)

# Top 5 by merchandise value
top_value = df.nlargest(
    5, "Merchandise_Value_BRL"
)

print("\nTOP 5 BY MERCHANDISE VALUE:")
print(
    top_value[
        [
            "category",
            "Items_Sold",
            "Merchandise_Value_BRL",
            "Average_Item_Price_BRL"
        ]
    ].to_string(index=False)
)

# Top 5 by items sold
top_volume = df.nlargest(
    5, "Items_Sold"
)

print("\nTOP 5 BY ITEMS SOLD:")
print(
    top_volume[
        [
            "category",
            "Items_Sold",
            "Merchandise_Value_BRL",
            "Average_Item_Price_BRL"
        ]
    ].to_string(index=False)
)

# Calculate top 10 contribution
top_10 = df.nlargest(
    10, "Merchandise_Value_BRL"
)

total_value = df["Merchandise_Value_BRL"].sum()

top_10_share = (
    top_10["Merchandise_Value_BRL"].sum()
    / total_value * 100
)

print("\nTOP 10 CATEGORY CONTRIBUTION:")
print(f"{top_10_share:.2f}%")

# Save the enhanced KPI report
output_file = reports / "category_kpi_analysis.csv"

df.to_csv(output_file, index=False)

print("\nKPI analysis completed successfully!")
print("Report saved to:", output_file)
