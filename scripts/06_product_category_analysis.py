
import pandas as pd
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent

raw = project / "data" / "raw"
processed = project / "data" / "processed"
reports = project / "reports"

# Load our datasets
sales = pd.read_csv(
    processed / "order_item_analysis_base.csv"
)

products = pd.read_csv(
    raw / "olist_products_dataset.csv"
)

translations = pd.read_csv(
    raw / "product_category_name_translation.csv"
)

print("RETAIL360 - PRODUCT CATEGORY ANALYSIS")
print("=" * 50)

# Verify lookup table keys
if products["product_id"].duplicated().any():
    raise ValueError("Duplicate product IDs found!")

if translations["product_category_name"].duplicated().any():
    raise ValueError("Duplicate category names found!")

# Join sales with product information
sales = sales.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left",
    validate="many_to_one",
    indicator="_product_match"
)

print(
    "\nItems without matching products:",
    (sales["_product_match"] == "left_only").sum()
)

sales = sales.drop(columns=["_product_match"])

# Add English category names
sales = sales.merge(
    translations,
    on="product_category_name",
    how="left",
    validate="many_to_one"
)

# Use the original category name when
# an English translation is unavailable.
sales["category"] = (
    sales["product_category_name_english"]
    .fillna(sales["product_category_name"])
    .fillna("Unknown")
)

# Check record counts
print("Total item records:", len(sales))

if len(sales) != 112650:
    raise ValueError("Unexpected item record count!")

# Filter to delivered orders
delivered = sales[
    sales["order_status"] == "delivered"
].copy()

# Calculate category performance
category_summary = (
    delivered.groupby("category", as_index=False)
    .agg(
        Items_Sold=("order_item_id", "size"),
        Unique_Orders=("order_id", "nunique"),
        Merchandise_Value_BRL=("price", "sum"),
        Freight_Value_BRL=("freight_value", "sum")
    )
)

# Calculate share of merchandise value
total_value = delivered["price"].sum()

category_summary["Value_Share_Percent"] = (
    category_summary["Merchandise_Value_BRL"]
    / total_value * 100
).round(2)

# Sort categories by merchandise value
category_summary = category_summary.sort_values(
    "Merchandise_Value_BRL",
    ascending=False
)

category_summary[
    ["Merchandise_Value_BRL", "Freight_Value_BRL"]
] = category_summary[
    ["Merchandise_Value_BRL", "Freight_Value_BRL"]
].round(2)

# Select the top 10 categories
top_10 = category_summary.head(10)

print("\nTOP 10 PRODUCT CATEGORIES:")
print(top_10.to_string(index=False))

# Save our reports
category_summary.to_csv(
    reports / "all_category_performance.csv",
    index=False
)

top_10.to_csv(
    reports / "top_10_product_categories.csv",
    index=False
)

print("\nProduct category analysis completed!")
print("Reports saved successfully!")
