
import pandas as pd
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent

processed = project / "data" / "processed"
reports = project / "reports"

# Load combined business data
df = pd.read_csv(
    processed / "order_item_analysis_base.csv"
)

print("RETAIL360 - GEOGRAPHIC SALES ANALYSIS")
print("=" * 55)

# Keep delivered orders only
delivered = df.loc[
    df["order_status"] == "delivered"
].copy()

# Check for missing customer states
print(
    "\nMissing customer states:",
    delivered["customer_state"].isna().sum()
)

# Group sales by customer state
state_summary = (
    delivered.groupby(
        "customer_state",
        as_index=False
    )
    .agg(
        Merchandise_Value_BRL=("price", "sum"),
        Freight_Value_BRL=("freight_value", "sum"),
        Unique_Orders=("order_id", "nunique"),
        Items_Sold=("order_item_id", "size"),
        Unique_Customers=("customer_unique_id", "nunique")
    )
)

# Calculate average merchandise value per order
state_summary["Avg_Order_Value_BRL"] = (
    state_summary["Merchandise_Value_BRL"]
    / state_summary["Unique_Orders"]
)

# Calculate each state's share
total_merchandise = (
    delivered["price"].sum()
)

state_summary["Value_Share_Percent"] = (
    state_summary["Merchandise_Value_BRL"]
    / total_merchandise * 100
)

# Round numerical values
money_columns = [
    "Merchandise_Value_BRL",
    "Freight_Value_BRL",
    "Avg_Order_Value_BRL",
    "Value_Share_Percent"
]

state_summary[money_columns] = (
    state_summary[money_columns].round(2)
)

# Rank states by merchandise value
state_summary = state_summary.sort_values(
    "Merchandise_Value_BRL",
    ascending=False
)

# Validate results
assert (
    state_summary["Items_Sold"].sum()
    == len(delivered)
), "State-level item counts do not reconcile!"

print("\nTOP 10 STATES BY MERCHANDISE VALUE:")

print(
    state_summary[
        [
            "customer_state",
            "Merchandise_Value_BRL",
            "Unique_Orders",
            "Avg_Order_Value_BRL",
            "Value_Share_Percent"
        ]
    ].head(10).to_string(index=False)
)

# Display leading state
top_state = state_summary.iloc[0]

print("\nHIGHEST-VALUE STATE:")
print("State:", top_state["customer_state"])
print(
    "Merchandise Value (BRL):",
    top_state["Merchandise_Value_BRL"]
)

# Save report
output_file = (
    reports / "geographic_sales_performance.csv"
)

state_summary.to_csv(
    output_file,
    index=False
)

print("\nGeographic analysis completed successfully!")
print("Report saved to:", output_file)
