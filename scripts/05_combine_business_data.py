
import pandas as pd
from pathlib import Path

# Locate our folders
project_folder = Path(__file__).resolve().parent.parent
raw_folder = project_folder / "data" / "raw"
processed_folder = project_folder / "data" / "processed"

processed_folder.mkdir(parents=True, exist_ok=True)

# Load our three datasets
orders = pd.read_csv(
    raw_folder / "olist_orders_dataset.csv"
)

items = pd.read_csv(
    raw_folder / "olist_order_items_dataset.csv"
)

customers = pd.read_csv(
    raw_folder / "olist_customers_dataset.csv"
)

print("RETAIL360 - BUSINESS DATA INTEGRATION")
print("=" * 50)

# Check that parent-table keys are unique
if orders["order_id"].duplicated().any():
    raise ValueError("Duplicate order_id in Orders")

if customers["customer_id"].duplicated().any():
    raise ValueError("Duplicate customer_id in Customers")

# Join Order Items with Orders
combined = items.merge(
    orders[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp"
        ]
    ],
    on="order_id",
    how="left",
    validate="many_to_one",
    indicator="_order_match"
)

print("\nAFTER FIRST JOIN:")
print("Rows:", len(combined))

print(
    "Items without matching orders:",
    (combined["_order_match"] == "left_only").sum()
)

# Join with Customers
combined = combined.merge(
    customers[
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state"
        ]
    ],
    on="customer_id",
    how="left",
    validate="many_to_one",
    indicator="_customer_match"
)

print("\nAFTER SECOND JOIN:")
print("Rows:", len(combined))
print("Columns:", len(combined.columns))

print(
    "Items without matching customers:",
    (combined["_customer_match"] == "left_only").sum()
)

# Verify that no item records were multiplied
if len(combined) != len(items):
    raise ValueError("Unexpected change in item row count")

# Calculate business metrics
print("\nBUSINESS METRICS")

print(
    "Total item records:",
    len(combined)
)

print(
    "Unique orders represented:",
    combined["order_id"].nunique()
)

# Focus on delivered orders for this example
delivered = combined[
    combined["order_status"] == "delivered"
]

print(
    "Delivered orders with items:",
    delivered["order_id"].nunique()
)

print(
    "Delivered item value (BRL):",
    round(delivered["price"].sum(), 2)
)

print(
    "Delivered freight value (BRL):",
    round(delivered["freight_value"].sum(), 2)
)

# Remove temporary merge-check columns
combined = combined.drop(
    columns=["_order_match", "_customer_match"]
)

# Save our combined dataset
output_file = (
    processed_folder /
    "order_item_analysis_base.csv"
)

combined.to_csv(output_file, index=False)

print("\nCombined dataset saved successfully!")
print(output_file)
