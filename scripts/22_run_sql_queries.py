
import sqlite3
import pandas as pd
from pathlib import Path

# Locate our Retail360 project
project = Path(__file__).resolve().parent.parent

# Find the SQLite database
database = project / "data" / "processed" / "retail360.db"

# Find our SQL queries

sql_file = project / "sql" / "05_data_quality.sql"


print("RETAIL360 - SQL QUERY EXECUTION")
print("=" * 50)

# Check the database and SQL file
if not database.exists():
    raise FileNotFoundError("Database file not found!")

if not sql_file.exists():
    raise FileNotFoundError("SQL file not found!")

# Read SQL queries
sql_text = sql_file.read_text(encoding="utf-8")

queries = [
    query.strip()
    for query in sql_text.split(";")
    if query.strip()
]

# Connect to the database
with sqlite3.connect(database) as connection:

    # Execute every SQL query
    for number, query in enumerate(queries, start=1):

        print(f"\nQUERY {number}")
        print("-" * 40)

        result = pd.read_sql_query(
            query,
            connection
        )

        print(result.to_string(index=False))

print("\nALL SQL QUERIES EXECUTED SUCCESSFULLY!")
