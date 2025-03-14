from fastapi import FastAPI
from typing import Dict, List

app = FastAPI()

# Dummy database of Sales Orders (SO) with line-level details
dummy_so_data = {
    "SO12345": {
        "so_number": "SO12345",
        "total_amount": 5000,
        "customer": "Cingular",
        "lines": [
            {"line_number": 1, "description": "Line Item 1", "amount": 3000},
            {"line_number": 2, "description": "Line Item 2", "amount": 2000}
        ]
    },
    "SO67890": {
        "so_number": "SO67890",
        "total_amount": 7500,
        "customer": "Cingular",
        "lines": [
            {"line_number": 1, "description": "Line Item A", "amount": 5000},
            {"line_number": 2, "description": "Line Item B", "amount": 2500}
        ]
    },
    "SO54321": {
        "so_number": "SO54321",
        "total_amount": 10000,
        "customer": "T-Mobile",
        "lines": [
            {"line_number": 1, "description": "Line Item X", "amount": 6000},
            {"line_number": 2, "description": "Line Item Y", "amount": 4000}
        ]
    },
    "SO98765": {
        "so_number": "SO98765",
        "total_amount": 8500,
        "customer": "Verizon",
        "lines": [
            {"line_number": 1, "description": "Line Item M", "amount": 5000},
            {"line_number": 2, "description": "Line Item N", "amount": 3500}
        ]
    }
}

@app.get("/get_so/{so_number}")
def get_sales_order(so_number: str) -> Dict:
    """
    Mock API endpoint to retrieve Sales Order details with line-level data.
    Usage: /get_so/{so_number}
    """
    if so_number in dummy_so_data:
        return {"status": "success", "data": dummy_so_data[so_number]}
    else:
        return {"status": "error", "message": "Sales Order not found"}

# Run the server with: uvicorn mock_api:app --reload