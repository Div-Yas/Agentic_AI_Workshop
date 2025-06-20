import pandas as pd
from datetime import datetime
import os

# Define the data for the sample file
data = {
    'employee_id': ['EMP001', 'EMP002', 'EMP003'],
    'name': ['John Doe', 'Jane Smith', 'Peter Jones'],
    'email': ['john.doe@example.com', 'jane.smith@example.com', 'peter.jones@example.com'],
    'phone': ['123-456-7890', '234-567-8901', '345-678-9012'],
    'designation': ['Software Engineer', 'Product Manager', 'Data Scientist'],
    'department': ['Engineering', 'Product', 'Analytics'],
    'join_date': [datetime(2023, 1, 15), datetime(2022, 5, 20), datetime(2023, 8, 10)],
    'basic_salary': [60000, 75000, 80000],
    'hra': [24000, 30000, 32000],
    'lta': [5000, 6000, 6500],
    'variable_pay': [10000, 12000, 15000],
    'bonuses': [5000, 7500, 8000],
    'other_allowances': [2000, 2500, 3000]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Go up one level from `backend` and then into `frontend/public`
output_dir = '../frontend/public/'
output_path = os.path.join(output_dir, 'sample_employees.xlsx')

# Create the directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Write the DataFrame to an Excel file
df.to_excel(output_path, index=False)

print(f"Successfully created sample employee Excel file at: {output_path}") 