
import pandas as pd
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent
reports = project / "reports"

# Load monthly sales report
df = pd.read_csv(
    reports / "monthly_sales_trends.csv"
)

print("RETAIL360 - MONTHLY GROWTH ANALYSIS")
print("=" * 55)

# Convert months into dates
df["Month_Date"] = pd.to_datetime(
    df["purchase_month"],
    format="%Y-%m"
)

# Sort months chronologically
df = df.sort_values(
    "Month_Date"
).reset_index(drop=True)

# Get previous month's value
df["Previous_Month_Value_BRL"] = (
    df["Merchandise_Value_BRL"].shift(1)
)

# Calculate percentage growth
previous = df["Previous_Month_Value_BRL"]

df["MoM_Growth_Percent"] = (
    (
        df["Merchandise_Value_BRL"] - previous
    )
    / previous.where(previous > 0)
    * 100
).round(2)

# Check months are consecutive
month_number = (
    df["Month_Date"].dt.year * 12
    + df["Month_Date"].dt.month
)

consecutive = month_number.diff().eq(1)

# Avoid comparisons across missing months
df.loc[
    ~consecutive,
    "MoM_Growth_Percent"
] = float("nan")

# Display growth report
print("\nMONTHLY GROWTH REPORT:")

print(
    df[
        [
            "purchase_month",
            "Merchandise_Value_BRL",
            "Previous_Month_Value_BRL",
            "MoM_Growth_Percent"
        ]
    ].to_string(index=False)
)

# Identify notable changes
# Exclude earliest comparisons and final month
# because boundary coverage may be incomplete.
review = df.iloc[2:-1].dropna(
    subset=["MoM_Growth_Percent"]
)

if not review.empty:

    highest = review.loc[
        review["MoM_Growth_Percent"].idxmax()
    ]

    lowest = review.loc[
        review["MoM_Growth_Percent"].idxmin()
    ]

    print("\nHIGHEST MONTHLY GROWTH:")
    print(
        highest["purchase_month"],
        f'{highest["MoM_Growth_Percent"]:.2f}%'
    )

    print("\nLOWEST MONTHLY GROWTH:")
    print(
        lowest["purchase_month"],
        f'{lowest["MoM_Growth_Percent"]:.2f}%'
    )

# Save growth analysis
output_file = reports / "monthly_growth_analysis.csv"

df.drop(
    columns=["Month_Date"]
).to_csv(output_file, index=False)

print("\nMonthly growth analysis completed!")
print("Report saved to:", output_file)
