import pandas as pd
import requests
import yaml
import glob, os
import sqlite3

CONFIG_PATH = "config.yaml"

def get_csv_data(directory_path):
    csv_files = glob.glob(os.path.join(directory_path, "*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV files found in the input directory.")
    df = pd.read_csv(csv_files[0])
    return df

def validate_customer(company_name, customer_name):
    conn = sqlite3.connect("dummy_oracle.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Customers.customer_name
        FROM Customers
        JOIN Companies ON Customers.company_id = Companies.company_id
        WHERE Companies.company_name = ? AND Customers.customer_name = ?
    """, (company_name, customer_name))

    result = cursor.fetchone()
    conn.close()
    return result is not None

if __name__ == "__main__":
    # Load Config
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)

    MOCK_API_URL = config["mock_api_url"]  # <-- Define explicitly here
    csv_folder = config["csv_folder"]

    # Load CSV data
    request_df = get_csv_data(csv_folder)

    so_number = request_df.loc[0, "SO"]
    company = request_df.loc[0, "Company"]
    customer = request_df.loc[0, "Customer"]

    # Validate customer
    if validate_customer(company, customer):
        print("Customer validation passed.")
    else:
        print("Customer validation failed.")

    # Fetch SO data from Mock API
    response = requests.get(f"{MOCK_API_URL}/{so_number}")
    if response.status_code == 200:
        so_data = response.json()
        print("Fetched Sales Order data:", so_data)
    else:
        print("Failed to fetch Sales Order data.")
