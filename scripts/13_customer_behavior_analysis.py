
import pandas as pd
from pathlib import Path

# Locate the project folders
project = Path(__file__).resolve().parent.parent

raw = project / "data" / "raw"
reports = project / "reports"

# Load Orders and Customers datasets
orders = pd.read_csv(
    raw / "olist_orders_dataset.csv"
)

customers = pd.read_csv(
    raw / "olist_customers_dataset.csv"
)

print("RETAIL360 - CUSTOMER BEHAVIOUR ANALYSIS")
print("=" * 55)

# Validate customer IDs
if customers["customer_id"].duplicated().any():
    raise ValueError("Duplicate customer_id values found!")

# Combine orders with customer information
combined = orders.merge(
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
    indicator=True
)

# Check missing relationships
missing = (
    combined["_merge"] == "left_only"
).sum()

print("\nOrders without customer match:", missing)

if missing > 0:
    raise ValueError("Unmatched customer records found!")

combined = combined.drop(columns=["_merge"])

# Keep delivered orders
delivered = combined[
    combined["order_status"] == "delivered"
].copy()

# Remove records without a customer identifier
delivered = delivered.dropna(
    subset=["customer_unique_id"]
)

# Count delivered orders per customer
customer_frequency = (
    delivered.groupby(
        "customer_unique_id",
        as_index=False
    )
    .agg(
        Total_Orders=("order_id", "nunique")
    )
)

# Calculate customer KPIs
total_customers = len(customer_frequency)

one_time_customers = (
    customer_frequency["Total_Orders"] == 1
).sum()

repeat_customers = (
    customer_frequency["Total_Orders"] >= 2
).sum()

repeat_rate = (
    repeat_customers / total_customers * 100
    if total_customers > 0 else 0
)

average_orders = (
    customer_frequency["Total_Orders"].mean()
    if total_customers > 0 else 0
)

# Display business metrics
print("\nCUSTOMER KPI SUMMARY")
print("-" * 40)

print("Unique Customers:", total_customers)

print("One-Time Customers:", one_time_customers)

print("Repeat Customers:", repeat_customers)

print(
    "Repeat Customer Rate:",
    round(repeat_rate, 2),
    "%"
)

print(
    "Average Orders Per Customer:",
    round(average_orders, 2)
)

# Analyze purchase frequency
frequency_distribution = (
    customer_frequency["Total_Orders"]
    .value_counts()
    .sort_index()
)

print("\nPURCHASE FREQUENCY DISTRIBUTION")
print(frequency_distribution)

# Save the detailed customer report
customer_frequency.to_csv(
    reports / "customer_purchase_frequency.csv",
    index=False
)

# Create a customer KPI summary
summary = pd.DataFrame([
    {
        "Unique_Customers": total_customers,
        "One_Time_Customers": one_time_customers,
        "Repeat_Customers": repeat_customers,
        "Repeat_Rate_Percent": round(repeat_rate, 2),
        "Average_Orders_Per_Customer": round(
            average_orders, 2
        )
    }
])

summary.to_csv(
    reports / "customer_repeat_summary.csv",
    index=False
)

print("\nCustomer analysis completed successfully!")
print("Reports saved successfully!")
