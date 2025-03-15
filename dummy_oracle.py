import sqlite3

DB_PATH = "dummy_oracle.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE Companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE OracleTemplates (
        template_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        template_name TEXT NOT NULL,
        FOREIGN KEY(company_id) REFERENCES Companies(company_id)
    );

        CREATE TABLE Customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        customer_name TEXT NOT NULL,
        customer_code TEXT NOT NULL,
        customer_bill_address TEXT NOT NULL,
        FOREIGN KEY(company_id) REFERENCES Companies(company_id)
    );


    CREATE TABLE LOBs (id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER, lob TEXT NOT NULL);
    CREATE TABLE Regions (id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER, region TEXT NOT NULL);
    CREATE TABLE Markets (id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER, market TEXT NOT NULL);
    CREATE TABLE Submarkets (id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER, submarket TEXT NOT NULL);
    CREATE TABLE PhysicalStates (id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER, physical_state TEXT NOT NULL);
    CREATE TABLE RegionalManagers (id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER, regional_manager TEXT NOT NULL);
    CREATE TABLE ProjectManagers (id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER, project_manager TEXT NOT NULL);
    CREATE TABLE ProjectTypes (id INTEGER PRIMARY KEY AUTOINCREMENT, template_id INTEGER, project_type TEXT NOT NULL);
    """)

    conn.commit()
    conn.close()

def insert_sample_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Companies (company_name) VALUES ('1805'), ('1802')")

    cursor.execute("SELECT company_id FROM Companies WHERE company_name = '1805'")
    id_1805 = cursor.fetchone()[0]
    cursor.execute("SELECT company_id FROM Companies WHERE company_name = '1802'")
    id_1802 = cursor.fetchone()[0]

    templates = [(id_1805, 'T-MOD'), (id_1805, 'Revbill'), (id_1802, 'Revbill'), (id_1802, 'POC')]
    cursor.executemany("INSERT INTO OracleTemplates (company_id, template_name) VALUES (?, ?)", templates)

    cursor.execute("SELECT template_id FROM OracleTemplates WHERE template_name='T-MOD' AND company_id=?", (id_1805,))
    tmod_id = cursor.fetchone()[0]
    cursor.execute("SELECT template_id FROM OracleTemplates WHERE template_name='Revbill' AND company_id=?", (id_1805,))
    revbill_id_1805 = cursor.fetchone()[0]
    cursor.execute("SELECT template_id FROM OracleTemplates WHERE template_name='Revbill' AND company_id=?", (id_1802,))
    revbill_id_1802 = cursor.fetchone()[0]
    cursor.execute("SELECT template_id FROM OracleTemplates WHERE template_name='POC' AND company_id=?", (id_1802,))
    poc_id = cursor.fetchone()[0]

    valid_customers_1805 = [
        (id_1805, "Cingular", "1100", "123 Billing St"),
        (id_1805, "Verizon", "1200", "234 Verizon Way")
    ]

    valid_customers_1802 = [
        (id_1802, "Cingular", "1100", "123 Billing St"),
        (id_1802, "T-Mobile", "1030", "456 Billing Blvd")
    ]

    cursor.executemany("INSERT INTO Customers (company_id, customer_name, customer_code, customer_bill_address) VALUES (?, ?, ?, ?)", valid_customers_1805)
    cursor.executemany("INSERT INTO Customers (company_id, customer_name, customer_code, customer_bill_address) VALUES (?, ?, ?, ?)", valid_customers_1802)

    # Move the valid_data dictionary INSIDE here (after IDs defined)
    valid_data = {
        tmod_id: {
            "LOBs": ["LOB1", "LOB2", "LOB4", "LOB5"],
            "Regions": ["Region1", "Region2", "Region4", "Region5"],
            "Markets": ["MarketA", "MarketB", "MarketD", "MarketE"],
            "Submarkets": ["SubmarketX", "SubmarketY", "SubmarketW", "SubmarketV"],
            "PhysicalStates": ["NY", "CA", "FL", "WA"],
            "RegionalManagers": ["John Doe", "Alice Brown", "Eve Grey", "Frank Blue"],
            "ProjectManagers": ["Jane Smith", "Bob White", "Sam Green", "Sara Red"],
            "ProjectTypes": ["Initiative Alpha", "Initiative Beta", "Initiative Delta", "Initiative Epsilon"]
        },
        revbill_id_1802: {
            "LOBs": ["LOB1", "LOB3", "LOB4", "LOB6"],
            "Regions": ["Region1", "Region3", "Region4", "Region6"],
            "Markets": ["MarketA", "MarketC", "MarketD", "MarketF"],
            "Submarkets": ["SubmarketX", "SubmarketZ", "SubmarketW", "SubmarketU"],
            "PhysicalStates": ["NY", "TX", "FL", "OR"],
            "RegionalManagers": ["John Doe", "Charlie Green", "Eve Grey", "Hannah White"],
            "ProjectManagers": ["Jane Smith", "David Black", "Sam Green", "Peter Gold"],
            "ProjectTypes": ["Initiative Alpha", "Initiative Gamma", "Initiative Delta", "Initiative Zeta"]
        },
        poc_id: {
            "LOBs": ["LOB1", "LOB4", "LOB8", "LOB9"],
            "Regions": ["Region3", "Region5", "Region9", "Region10"],
            "Markets": ["MarketA", "MarketF", "MarketG", "MarketH"],
            "Submarkets": ["SubmarketU", "SubmarketV", "SubmarketS", "SubmarketT"],
            "PhysicalStates": ["FL", "OR", "GA", "NV"],
            "RegionalManagers": ["Eve Grey", "Frank Blue", "Laura Silver", "Tom Bronze"],
            "ProjectManagers": ["Sam Green", "Sara Red", "Olivia Pink", "George Orange"],
            "ProjectTypes": ["Initiative Delta", "Initiative Epsilon", "Initiative Theta", "Initiative Lambda"]
        }
    }

    column_mapping = {
        "LOBs": "lob",
        "Regions": "region",
        "Markets": "market",
        "Submarkets": "submarket",
        "PhysicalStates": "physical_state",
        "RegionalManagers": "regional_manager",
        "ProjectManagers": "project_manager",
        "ProjectTypes": "project_type"
    }

    for template_id, categories in valid_data.items():
        for table, values in categories.items():
            col = column_mapping[table]
            for val in values:
                cursor.execute(f"INSERT INTO {table} (template_id, {col}) VALUES (?, ?)", (template_id, val))

    conn.commit()
    conn.close()
    print("Database setup and populated successfully.")

if __name__ == "__main__":
    create_database()
    insert_sample_data()
