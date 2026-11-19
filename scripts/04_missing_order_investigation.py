
import pandas as pd
from pathlib import Path

# Locate the project folder
project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "data" / "raw"
reports_folder = project_folder / "reports"

# Load the two datasets
orders = pd.read_csv(
    data_folder / "olist_orders_dataset.csv"
)

items = pd.read_csv(
    data_folder / "olist_order_items_dataset.csv"
)

print("RETAIL360 - MISSING ORDER INVESTIGATION")
print("=" * 50)

# Check which orders have item records
has_items = orders["order_id"].isin(
    items["order_id"]
)

# Separate orders without item records
missing_orders = orders.loc[~has_items].copy()

print("\nTOTAL ORDERS:", len(orders))
print("ORDERS WITH ITEMS:", has_items.sum())
print("ORDERS WITHOUT ITEMS:", len(missing_orders))

# Investigate order statuses
print("\nSTATUS OF ORDERS WITHOUT ITEMS:")
print(
    missing_orders["order_status"].value_counts()
)

# Create a summary report
status_summary = (
    missing_orders["order_status"]
    .value_counts()
    .rename_axis("order_status")
    .reset_index(name="order_count")
)

# Save the report
output_file = (
    reports_folder /
    "orders_without_items_by_status.csv"
)

status_summary.to_csv(
    output_file,
    index=False
)

print("\nReport saved successfully!")
print(output_file)
