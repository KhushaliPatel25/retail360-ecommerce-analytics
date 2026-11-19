
import pandas as pd
from pathlib import Path

# Locate our project
project = Path(__file__).resolve().parent.parent

processed = project / "data" / "processed"
reports = project / "reports"

# Load our combined sales dataset
df = pd.read_csv(
    processed / "order_item_analysis_base.csv"
)

print("RETAIL360 - MONTHLY SALES ANALYSIS")
print("=" * 55)

# Convert purchase timestamps to dates
df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"],
    errors="coerce"
)

# Keep delivered orders
delivered = df[
    df["order_status"] == "delivered"
].copy()

# Remove records without valid purchase dates
delivered = delivered.dropna(
    subset=["order_purchase_timestamp"]
)

# Extract purchase month
delivered["purchase_month"] = (
    delivered["order_purchase_timestamp"]
    .dt.to_period("M")
)

# Calculate monthly business metrics
monthly = (
    delivered.groupby(
        "purchase_month",
        as_index=False
    )
    .agg(
        Merchandise_Value_BRL=("price", "sum"),
        Unique_Orders=("order_id", "nunique"),
        Items_Sold=("order_item_id", "size")
    )
)

# Calculate average merchandise value per order
monthly["Avg_Order_Merchandise_BRL"] = (
    monthly["Merchandise_Value_BRL"]
    / monthly["Unique_Orders"]
)

# Round monetary values
monthly["Merchandise_Value_BRL"] = (
    monthly["Merchandise_Value_BRL"].round(2)
)

monthly["Avg_Order_Merchandise_BRL"] = (
    monthly["Avg_Order_Merchandise_BRL"].round(2)
)

# Sort chronologically
monthly = monthly.sort_values(
    "purchase_month"
)

# Convert month to readable format
monthly["purchase_month"] = (
    monthly["purchase_month"].astype(str)
)

print("\nMONTHLY SALES PERFORMANCE:")
print(monthly.to_string(index=False))

# Identify highest-value month
best_month = monthly.loc[
    monthly["Merchandise_Value_BRL"].idxmax()
]

print("\nHIGHEST MERCHANDISE VALUE MONTH:")
print("Month:", best_month["purchase_month"])
print(
    "Merchandise Value (BRL):",
    best_month["Merchandise_Value_BRL"]
)

# Check overall totals
print("\nOVERALL SUMMARY:")

print(
    "Unique delivered orders:",
    delivered["order_id"].nunique()
)

print(
    "Total merchandise value (BRL):",
    round(delivered["price"].sum(), 2)
)

# Save monthly report
output_file = (
    reports / "monthly_sales_trends.csv"
)

monthly.to_csv(
    output_file,
    index=False
)

print("\nMonthly sales analysis completed!")
print("Report saved to:", output_file)
