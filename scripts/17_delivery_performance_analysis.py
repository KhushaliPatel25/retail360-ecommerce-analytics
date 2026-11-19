
import pandas as pd
from pathlib import Path

# Locate our project folders
project = Path(__file__).resolve().parent.parent

raw = project / "data" / "raw"
reports = project / "reports"

reports.mkdir(parents=True, exist_ok=True)

print("RETAIL360 - DELIVERY PERFORMANCE ANALYSIS")
print("=" * 55)

# Load orders and customers
orders = pd.read_csv(
    raw / "olist_orders_dataset.csv"
)

customers = pd.read_csv(
    raw / "olist_customers_dataset.csv"
)

# Validate unique IDs
if orders["order_id"].duplicated().any():
    raise ValueError("Duplicate order IDs found!")

if customers["customer_id"].duplicated().any():
    raise ValueError("Duplicate customer IDs found!")

# Convert timestamp columns
date_columns = [
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(
        orders[column],
        errors="coerce"
    )

# Join orders with customer locations
df = orders.merge(
    customers[["customer_id", "customer_state"]],
    on="customer_id",
    how="left",
    validate="many_to_one"
)

# Select a comparable purchase period
df = df.loc[
    (df["order_purchase_timestamp"] >= "2017-02-01") &
    (df["order_purchase_timestamp"] < "2018-08-01")
].copy()

# Keep delivered orders
delivered = df.loc[
    df["order_status"] == "delivered"
].copy()

print("\nDELIVERY DATA QUALITY")
print("-" * 40)

print(
    "Delivered orders in reporting period:",
    len(delivered)
)

# Check missing dates
missing_dates = delivered[
    [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
].isna().any(axis=1)

print(
    "Delivered orders with missing dates:",
    missing_dates.sum()
)

# Keep records with valid dates
valid = delivered.loc[
    ~missing_dates
].copy()

# Calculate delivery duration
valid["Delivery_Days"] = (
    (
        valid["order_delivered_customer_date"] -
        valid["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
)

# Find logically invalid negative durations
invalid_duration = (
    valid["Delivery_Days"] < 0
)

print(
    "Orders with negative delivery duration:",
    invalid_duration.sum()
)

valid = valid.loc[
    ~invalid_duration
].copy()

# Compare calendar delivery dates
# Estimated delivery dates represent calendar dates
actual_date = (
    valid["order_delivered_customer_date"]
    .dt.normalize()
)

estimated_date = (
    valid["order_estimated_delivery_date"]
    .dt.normalize()
)

valid["On_Time"] = (
    actual_date <= estimated_date
)

valid["Late"] = ~valid["On_Time"]

# Calculate days late
valid["Days_Late"] = (
    (actual_date - estimated_date)
    .dt.days
    .clip(lower=0)
)

# Calculate KPI metrics
total_orders = len(valid)

if total_orders == 0:
    raise ValueError(
        "No valid delivery records available."
    )

average_days = valid["Delivery_Days"].mean()
median_days = valid["Delivery_Days"].median()

on_time_orders = int(valid["On_Time"].sum())
late_orders = int(valid["Late"].sum())

on_time_rate = on_time_orders / total_orders * 100
late_rate = late_orders / total_orders * 100

# Display delivery KPIs
print("\nDELIVERY PERFORMANCE KPI SUMMARY")
print("-" * 40)

print("Analyzed Delivered Orders:", total_orders)

print(
    "Average Delivery Days:",
    round(average_days, 2)
)

print(
    "Median Delivery Days:",
    round(median_days, 2)
)

print("On-Time Orders:", on_time_orders)
print("Late Orders:", late_orders)

print(
    "On-Time Delivery Rate:",
    f"{on_time_rate:.2f}%"
)

print(
    "Late Delivery Rate:",
    f"{late_rate:.2f}%"
)

# Calculate state-level performance
state_summary = (
    valid.groupby(
        "customer_state",
        as_index=False
    )
    .agg(
        Delivered_Orders=("order_id", "nunique"),
        Average_Delivery_Days=("Delivery_Days", "mean"),
        On_Time_Orders=("On_Time", "sum"),
        Late_Orders=("Late", "sum")
    )
)

state_summary["On_Time_Rate_Percent"] = (
    state_summary["On_Time_Orders"]
    / state_summary["Delivered_Orders"] * 100
)

state_summary = state_summary.round(2)

# Rank by delivery volume
state_summary = state_summary.sort_values(
    "Delivered_Orders",
    ascending=False
)

print("\nTOP 10 STATES BY DELIVERY VOLUME")

print(
    state_summary.head(10).to_string(index=False)
)

# Save KPI summary
kpi_summary = pd.DataFrame([
    {
        "Reporting_Period": "2017-02 to 2018-07",
        "Analyzed_Orders": total_orders,
        "Average_Delivery_Days": round(average_days, 2),
        "Median_Delivery_Days": round(median_days, 2),
        "On_Time_Orders": on_time_orders,
        "Late_Orders": late_orders,
        "On_Time_Rate_Percent": round(on_time_rate, 2),
        "Late_Rate_Percent": round(late_rate, 2)
    }
])

kpi_summary.to_csv(
    reports / "delivery_performance_summary.csv",
    index=False
)

# Save regional analysis
state_summary.to_csv(
    reports / "delivery_performance_by_state.csv",
    index=False
)

print("\nDelivery performance analysis completed!")
print("Both reports saved successfully!")
