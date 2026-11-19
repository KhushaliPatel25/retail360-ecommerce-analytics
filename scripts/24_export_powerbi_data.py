
import sqlite3
import pandas as pd
from pathlib import Path

# Locate our Retail360 project
project = Path(__file__).resolve().parent.parent

# Locate our SQL database
database = (
    project / "data" / "processed" / "retail360.db"
)

# Create a folder for Power BI data
powerbi_folder = project / "data" / "powerbi"

powerbi_folder.mkdir(
    parents=True,
    exist_ok=True
)

print("RETAIL360 - POWER BI DATA EXPORT")
print("=" * 55)

# Check the database exists
if not database.exists():
    raise FileNotFoundError(
        "retail360.db was not found!"
    )

# Connect to our SQL database
with sqlite3.connect(database) as connection:

    # Load our order summary view
    orders = pd.read_sql_query(
        "SELECT * FROM vw_order_summary",
        connection
    )

    # Load our item sales view
    items = pd.read_sql_query(
        "SELECT * FROM vw_item_sales",
        connection
    )

# Validate the datasets
if orders["order_id"].duplicated().any():
    raise ValueError(
        "Duplicate Order IDs in order summary!"
    )

unmatched = ~items["order_id"].isin(
    orders["order_id"]
)

if unmatched.any():
    raise ValueError(
        "Some order items have no matching orders!"
    )

# Export CSV files
orders_file = powerbi_folder / "OrderSummary.csv"

items_file = powerbi_folder / "OrderItems.csv"

orders.to_csv(
    orders_file,
    index=False,
    encoding="utf-8-sig"
)

items.to_csv(
    items_file,
    index=False,
    encoding="utf-8-sig"
)

# Display export results
print("\nORDER SUMMARY")
print("Rows:", len(orders))
print("Columns:", len(orders.columns))

print("\nORDER ITEMS")
print("Rows:", len(items))
print("Columns:", len(items.columns))

print("\nFiles exported successfully!")
print("Order Summary:", orders_file)
print("Order Items:", items_file)

print("\nPOWER BI DATA PREPARATION COMPLETED!")
