
import sqlite3
import pandas as pd
from pathlib import Path

# Locate project folders
project = Path(__file__).resolve().parent.parent

raw = project / "data" / "raw"
processed = project / "data" / "processed"

processed.mkdir(parents=True, exist_ok=True)

# Define our database location
database_path = processed / "retail360.db"

print("RETAIL360 - SQL DATABASE CREATION")
print("=" * 55)

# Define datasets and SQL table names
datasets = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

# Preserve ZIP code prefixes as text
zip_dtypes = {
    "customers": {
        "customer_zip_code_prefix": "string"
    },
    "sellers": {
        "seller_zip_code_prefix": "string"
    },
    "geolocation": {
        "geolocation_zip_code_prefix": "string"
    }
}

# Check that all CSV files exist
for table_name, filename in datasets.items():
    file_path = raw / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing source file: {filename}"
        )

# Connect to SQLite
connection = sqlite3.connect(database_path)

try:
    # Import CSV files as SQL tables
    for table_name, filename in datasets.items():

        file_path = raw / filename

        total_rows = 0
        first_chunk = True

        # Read large files in smaller batches
        chunks = pd.read_csv(
            file_path,
            chunksize=50000,
            dtype=zip_dtypes.get(table_name),
            low_memory=False
        )

        for chunk in chunks:

            chunk.to_sql(
                name=table_name,
                con=connection,
                if_exists=(
                    "replace" if first_chunk
                    else "append"
                ),
                index=False
            )

            total_rows += len(chunk)
            first_chunk = False

        print(
            f"Imported {table_name}: "
            f"{total_rows:,} rows"
        )

    # Create useful database indexes
    # These help the database find matching records
    indexes = [
        """CREATE UNIQUE INDEX IF NOT EXISTS
           idx_orders_id ON orders(order_id)""",

        """CREATE UNIQUE INDEX IF NOT EXISTS
           idx_customers_id ON customers(customer_id)""",

        """CREATE UNIQUE INDEX IF NOT EXISTS
           idx_products_id ON products(product_id)""",

        """CREATE INDEX IF NOT EXISTS
           idx_items_order ON order_items(order_id)""",

        """CREATE INDEX IF NOT EXISTS
           idx_items_product ON order_items(product_id)""",

        """CREATE INDEX IF NOT EXISTS
           idx_orders_customer ON orders(customer_id)""",

        """CREATE INDEX IF NOT EXISTS
           idx_payments_order ON payments(order_id)""",

        """CREATE INDEX IF NOT EXISTS
           idx_reviews_order ON reviews(order_id)"""
    ]

    for statement in indexes:
        connection.execute(statement)

    connection.commit()

    # Verify the database tables
    print("\nDATABASE VALIDATION")
    print("-" * 45)

    for table_name in datasets:

        count = connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        print(
            f"{table_name}: {count:,} records"
        )

    # Count available tables
    table_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        """
    ).fetchone()[0]

    print("\nTotal database tables:", table_count)

finally:
    # Close the database safely
    connection.close()

print("\nSQL DATABASE CREATED SUCCESSFULLY!")
print("Database saved at:", database_path)
