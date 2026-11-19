
import pandas as pd
from pathlib import Path

# Find our project folder
project_folder = Path(__file__).resolve().parent.parent

# Define our data and reports folders
data_folder = project_folder / "data" / "raw"
reports_folder = project_folder / "reports"

# Find all CSV files
csv_files = sorted(data_folder.glob("*.csv"))

print("RETAIL360 - DATA QUALITY AUDIT")
print("=" * 50)

# Create an empty list for our results
results = []

# Examine every dataset
for file in csv_files:

    df = pd.read_csv(file, low_memory=False)

    results.append({
        "Dataset": file.name,
        "Rows": len(df),
        "Columns": len(df.columns),
        "Missing_Values": df.isnull().sum().sum(),
        "Duplicate_Rows": df.duplicated().sum()
    })

    print(f"Completed: {file.name}")

# Create a summary DataFrame
summary = pd.DataFrame(results)

print("\nDATA QUALITY SUMMARY:")
print(summary.to_string(index=False))

# Save the report as a CSV file
output_file = reports_folder / "dataset_audit_summary.csv"

summary.to_csv(output_file, index=False)

print("\nReport saved successfully!")
print(output_file)
