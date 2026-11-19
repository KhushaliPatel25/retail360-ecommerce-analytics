
import pandas as pd
from pathlib import Path

# Locate the dataset folder
project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "data" / "raw"

# Load three related datasets
orders = pd.read_csv(
    data_folder / "olist_orders_dataset.csv"
)

customers = pd.read_csv(
    data_folder / "olist_customers_dataset.csv"
)

items = pd.read_csv(
    data_folder / "olist_order_items_dataset.csv"
)

print("RETAIL360 - TABLE RELATIONSHIP CHECK")
print("=" * 50)

# Count records
print("\nRECORD COUNTS")
print("Orders:", len(orders))
print("Customers:", len(customers))
print("Order Items:", len(items))

# Check unique business identifiers
print("\nUNIQUE IDENTIFIERS")
print("Unique Order IDs:", orders["order_id"].nunique())
print("Unique Customer IDs:", customers["customer_id"].nunique())
print(
    "Unique Real Customers:",
    customers["customer_unique_id"].nunique()
)

# Check uniqueness of important keys
print("\nPRIMARY KEY CHECKS")
print(
    "Duplicate Order IDs:",
    orders["order_id"].duplicated().sum()
)

print(
    "Duplicate Customer IDs:",
    customers["customer_id"].duplicated().sum()
)

# Check relationships between tables
print("\nRELATIONSHIP VALIDATION")

missing_customers = ~orders["customer_id"].isin(
    customers["customer_id"]
)

missing_orders = ~items["order_id"].isin(
    orders["order_id"]
)

print(
    "Orders without matching customer records:",
    missing_customers.sum()
)

print(
    "Order items without matching orders:",
    missing_orders.sum()
)

# Check orders with multiple items
item_counts = items.groupby("order_id").size()

print("\nORDER ITEMS ANALYSIS")
print(
    "Orders represented in Order Items:",
    len(item_counts)
)

print(
    "Orders with multiple items:",
    (item_counts > 1).sum()
)

print(
    "Maximum items in a single order:",
    item_counts.max()
)

print("\nRelationship check completed successfully!")
