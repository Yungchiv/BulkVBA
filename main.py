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
    return pd.read_csv(csv_files[0])

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

def validate_project_fields(template_name, field_name, field_value):
    conn = sqlite3.connect("dummy_oracle.db")
    cursor = conn.cursor()
    field_to_db = {
        "LOB": ("LOBs", "lob"),
        "Region": ("Regions", "region"),
        "Market": ("Markets", "market"),
        "Submarket": ("Submarkets", "submarket"),
        "Physical State": ("PhysicalStates", "physical_state"),
        "Regional Manager": ("RegionalManagers", "regional_manager"),
        "Project Manager": ("ProjectManagers", "project_manager"),
        "Project Type/Initiative": ("ProjectTypes", "project_type")
    }
    table_name, column_name = field_to_db[field_name]
    query = f"""
        SELECT {column_name}
        FROM {table_name}
        JOIN OracleTemplates ON OracleTemplates.template_id = {table_name}.template_id
        WHERE OracleTemplates.template_name = ? AND {column_name} = ?
    """
    cursor.execute(query, (template_name, field_value))
    result = cursor.fetchone()
    conn.close()
    return result is not None

if __name__ == "__main__":
    # Load configuration clearly first
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)

    MOCK_API_URL = config["mock_api_url"]
    csv_folder = config["csv_folder"]
    bel_csv_folder = config["bel_csv_folder"]

    # Load Request CSV data
    request_df = get_csv_data(csv_folder)

    # Extract and clean Company data from CSV
    so_number = request_df.loc[0, "SO"]
    company = str(request_df.loc[0, "Company"]).split('.')[0]  # Converts '1805.0' to '1805'
    customer = request_df.loc[0, "Customer"]

    print("Company:", company, "| Customer:", customer)

    # Validate customer
    if validate_customer(company, customer):
        print("✅ Customer validation passed.")
    else:
        print("❌ Customer validation failed.")

    # Extract Oracle template name from CSV
    template_name = request_df.loc[0, "Oracle Template"]

    required_fields = [
        "LOB", "Region", "Market", "Submarket", "Physical State",
        "Regional Manager", "Project Manager", "Project Type/Initiative"
    ]

    validation_results = {}

    # Run validations against Dummy Oracle database
    for field in required_fields:
        value = request_df.loc[0, field]
        is_valid = validate_project_fields(template_name, field, value)
        validation_results[field] = is_valid
        print(f"{field} ('{value}') validation result: {'✅ Passed' if is_valid else '❌ Failed'}")

    # Overall validation check
    if all(validation_results.values()):
        print("✅ All project fields are valid for this Oracle Template.")
    else:
        print("❌ Some project fields failed validation. Review required.")

    # Fetch SO details from Mock API (once only)
    response = requests.get(f"{MOCK_API_URL}/{so_number}")
    if response.status_code == 200:
        so_data = response.json()["data"]
        print("Fetched SO details:", so_data)

        # Load BEL CSV data and verify columns
        bel_df = get_csv_data(bel_csv_folder)
        print("BEL CSV Column Names:", bel_df.columns.tolist())

        # ⚠️ Replace 'Sales Order #' below with the actual printed BEL CSV column name
        bel_so_column = "Sales Order #"  # <-- Update this if needed
        bel_lines_for_so = bel_df[bel_df[bel_so_column] == so_number]

        # Sum BEL Amounts
        bel_total_amount = bel_lines_for_so["Total"].sum()

        print(f"Total BEL amount from BEL CSV for SO {so_number}: {bel_total_amount}")
        print(f"Total SO amount from Mock API: {so_data['total_amount']}")

        # Validate BEL amounts match SO amounts
        if bel_total_amount == so_data["total_amount"]:
            print("✅ BEL validation PASSED: Amounts match.")
        else:
            print("❌ BEL validation FAILED: Amount mismatch.")
    else:
        print(f"❌ Failed to fetch Sales Order data for SO {so_number}.")

    # Extract budget from Request CSV
    revenue_budget_csv = request_df.loc[0, "Revenue Budget"]
    print(f"Revenue Budget from Request CSV: {revenue_budget_csv}")

    # Now you have these values already:
    # - bel_total_amount
    # - so_data["total_amount"]

    # Clearly validate Revenue Budget against SO and BEL totals:
    budget_matches_so = revenue_budget_csv == so_data["total_amount"]
    budget_matches_bel = revenue_budget_csv == bel_total_amount

    # Print the results clearly
    if budget_matches_so and budget_matches_bel:
        print("✅ Budget validation PASSED: Revenue Budget matches SO and BEL amounts.")
    elif not budget_matches_so and not budget_matches_bel:
        print("❌ Budget validation FAILED: Revenue Budget mismatch with both SO and BEL.")
    elif not budget_matches_so:
        print("❌ Budget validation FAILED: Revenue Budget mismatch with SO amount.")
    elif not budget_matches_bel:
        print("❌ Budget validation FAILED: Revenue Budget mismatch with BEL amount.")
