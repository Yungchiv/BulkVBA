import sqlite3
import requests
import pandas as pd
import yaml

# Define constants/config
CONFIG_PATH = "config.yml"
DB_PATH = "dummy_oracle.db"
MOCK_API_URL = "http://localhost:8000/get_so"

# Load configuration
with open(CONFIG_PATH, 'r') as file:
    config = yaml.safe_load(file)

def get_sales_order(so_number):
    """Fetch Sales Order data from mock API"""
    response = requests.get(f"{MOCK_API_URL}/{so_number}")
    return response.json()

def validate_customer(company_name, customer_name):
    """Check if customer exists under the company in dummy Oracle DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Customers.customer_name
        FROM Customers
        JOIN Companies ON Customers.company_id = Companies.company_id
        WHERE Companies.company_name = ? AND Customers.customer_name = ?
    """, (company, customer_name))
    
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Example validation call (test)
if __name__ == "__main__":
    # Example test
    company = "1805"
    customer = "Cingular"
    so_number = "SO12345"

    # Validate customer
    if validate_customer(company, "Cingular"):
        print("Customer validation passed.")
    else:
        print("Customer validation failed.")

    # Get SO data from Mock API
    response = requests.get(f"{MOCK_API_URL}/{so_number}")
    if response.status_code == 200:
        so_data = response.json()
        print("Fetched Sales Order data:", so_data)
    else:
        print("Failed to fetch Sales Order data from Mock API.")