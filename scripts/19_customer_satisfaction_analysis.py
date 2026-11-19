
import pandas as pd
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent

raw = project / "data" / "raw"
reports = project / "reports"

reports.mkdir(parents=True, exist_ok=True)

print("RETAIL360 - CUSTOMER SATISFACTION ANALYSIS")
print("=" * 55)

# Load order and review datasets
orders = pd.read_csv(
    raw / "olist_orders_dataset.csv"
)

reviews = pd.read_csv(
    raw / "olist_order_reviews_dataset.csv"
)

# Validate order identifiers
if orders["order_id"].duplicated().any():
    raise ValueError("Duplicate order IDs found!")

# Convert dates
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

# Select delivered orders in reporting period
delivered = orders.loc[
    (orders["order_status"] == "delivered") &
    (orders["order_purchase_timestamp"] >= "2017-02-01") &
    (orders["order_purchase_timestamp"] < "2018-08-01")
].copy()

# Keep valid delivery dates
delivered = delivered.dropna(
    subset=[
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
)

# Exclude logically impossible negative durations
delivered = delivered.loc[
    delivered["order_delivered_customer_date"] >=
    delivered["order_purchase_timestamp"]
].copy()

# Calculate delivery status
actual_date = (
    delivered["order_delivered_customer_date"]
    .dt.normalize()
)

estimated_date = (
    delivered["order_estimated_delivery_date"]
    .dt.normalize()
)

delivered["Delivery_Status"] = "On Time"

delivered.loc[
    actual_date > estimated_date,
    "Delivery_Status"
] = "Late"

# Prepare customer review scores
reviews["review_score"] = pd.to_numeric(
    reviews["review_score"],
    errors="coerce"
)

reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"],
    errors="coerce"
)

reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"],
    errors="coerce"
)

# Keep valid ratings between 1 and 5
reviews = reviews.loc[
    reviews["review_score"].between(1, 5)
].copy()

# Keep the latest review for each order
# This avoids counting the same order multiple times
duplicate_reviews = (
    reviews["order_id"].duplicated().sum()
)

reviews = (
    reviews.sort_values(
        [
            "review_creation_date",
            "review_answer_timestamp"
        ],
        kind="mergesort",
        na_position="first"
    )
    .drop_duplicates(
        subset=["order_id"],
        keep="last"
    )
)

print("\nDuplicate order-review records resolved:",
      duplicate_reviews)

# Join delivered orders with reviews
df = delivered.merge(
    reviews[["order_id", "review_score"]],
    on="order_id",
    how="left",
    validate="one_to_one"
)

# Measure review coverage
total_delivered = len(df)

reviewed = df.dropna(
    subset=["review_score"]
).copy()

rated_orders = len(reviewed)

if rated_orders == 0:
    raise ValueError("No matching customer reviews found!")

review_coverage = (
    rated_orders / total_delivered * 100
)

# Display customer satisfaction KPIs
print("\nCUSTOMER SATISFACTION KPIs")
print("-" * 45)

print("Eligible Delivered Orders:", total_delivered)
print("Orders With Reviews:", rated_orders)

print(
    "Review Coverage:",
    f"{review_coverage:.2f}%"
)

print(
    "Average Review Rating:",
    round(reviewed["review_score"].mean(), 2)
)

# Compare late and on-time deliveries
summary = (
    reviewed.groupby(
        "Delivery_Status",
        as_index=False
    )
    .agg(
        Reviewed_Orders=("order_id", "nunique"),
        Average_Review_Score=("review_score", "mean"),
        Low_Rating_Orders=(
            "review_score",
            lambda values: (values <= 2).sum()
        )
    )
)

# Calculate poor rating percentage
summary["Low_Rating_Percent"] = (
    summary["Low_Rating_Orders"]
    / summary["Reviewed_Orders"] * 100
)

summary[
    ["Average_Review_Score", "Low_Rating_Percent"]
] = summary[
    ["Average_Review_Score", "Low_Rating_Percent"]
].round(2)

print("\nREVIEW PERFORMANCE BY DELIVERY STATUS")
print(summary.to_string(index=False))

# Create rating distribution
reviewed["review_score"] = (
    reviewed["review_score"].astype(int)
)

distribution = pd.crosstab(
    reviewed["Delivery_Status"],
    reviewed["review_score"]
).reindex(
    columns=[1, 2, 3, 4, 5],
    fill_value=0
)

print("\nREVIEW SCORE DISTRIBUTION")
print(distribution.to_string())

# Save our reports
summary.to_csv(
    reports / "customer_satisfaction_by_delivery.csv",
    index=False
)

distribution.to_csv(
    reports / "review_score_distribution.csv"
)

print("\nCustomer satisfaction analysis completed!")
print("Reports saved successfully!")
