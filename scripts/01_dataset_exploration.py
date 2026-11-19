
import pandas as pd
from pathlib import Path

# Locate our Retail360 project
project_folder = Path(__file__).resolve().parent.parent

# Locate the Orders CSV file
file_path = project_folder / "data" / "raw" / "olist_orders_dataset.csv"

# Read the dataset using Pandas
df = pd.read_csv(file_path)

# Display the first five records
print("\nFIRST 5 ROWS:")
print(df.head())

# Count rows and columns
print("\nDATASET SHAPE:")
print(df.shape)

# Display column names
print("\nCOLUMN NAMES:")
print(df.columns.tolist())

# Find missing values
print("\nMISSING VALUES:")
print(df.isnull().sum())

print("\nDataset exploration completed successfully!")
