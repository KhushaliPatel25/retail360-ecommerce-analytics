
import sqlite3
import pandas as pd
from pathlib import Path

# Locate project folder
project = Path(__file__).resolve().parent.parent

# Locate database and SQL file
database = (
    project / "data" / "processed" / "retail360.db"
)

sql_file = (
    project / "sql" / "06_reporting_views.sql"
)

print("RETAIL360 - SQL REPORTING VIEWS")
print("=" * 55)

# Check that files exist
if not database.exists():
    raise FileNotFoundError(
        "Database not found. Check retail360.db"
    )

if not sql_file.exists():
    raise FileNotFoundError(
        "SQL reporting views file not found."
    )

# Read the SQL script
sql_script = sql_file.read_text(
    encoding="utf-8"
)

# Connect to SQLite
with sqlite3.connect(database) as connection:

    # Create all three reporting views
    connection.executescript(sql_script)

    print("\nREPORTING VIEWS CREATED")

    # Display available views
    views = pd.read_sql_query(
        """
        SELECT name AS view_name
        FROM sqlite_master
        WHERE type = 'view'
        ORDER BY name
        """,
        connection
    )

    print(views.to_string(index=False))

    # Check row counts
    print("\nVIEW RECORD COUNTS")
    print("-" * 45)

    for view in [
        "vw_order_summary",
        "vw_item_sales",
        "vw_monthly_delivered_sales"
    ]:

        count = connection.execute(
            f"SELECT COUNT(*) FROM {view}"
        ).fetchone()[0]

        print(f"{view}: {count:,} rows")

    # Check key relationships
    order_count = connection.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    summary_count = connection.execute(
        "SELECT COUNT(*) FROM vw_order_summary"
    ).fetchone()[0]

    item_count = connection.execute(
        "SELECT COUNT(*) FROM order_items"
    ).fetchone()[0]

    item_view_count = connection.execute(
        "SELECT COUNT(*) FROM vw_item_sales"
    ).fetchone()[0]

    if summary_count != order_count:
        raise ValueError(
            "Order summary row count does not match!"
        )

    if item_view_count != item_count:
        raise ValueError(
            "Item sales row count does not match!"
        )

    print("\nROW COUNT VALIDATION PASSED")

    # View monthly business metrics
    monthly = pd.read_sql_query(
        """
        SELECT
            purchase_month,
            delivered_orders,
            merchandise_value_brl
        FROM vw_monthly_delivered_sales
        ORDER BY purchase_month
        """,
        connection
    )

    print("\nMONTHLY DELIVERED SALES")
    print(monthly.to_string(index=False))

    # Check overall merchandise value
    total = connection.execute(
        """
        SELECT ROUND(
            SUM(merchandise_value_brl), 2
        )
        FROM vw_monthly_delivered_sales
        """
    ).fetchone()[0]

    print("\nTOTAL DELIVERED MERCHANDISE VALUE")
    print(f"R$ {total:,.2f}")

print("\nREPORTING VIEWS CREATED SUCCESSFULLY!")
