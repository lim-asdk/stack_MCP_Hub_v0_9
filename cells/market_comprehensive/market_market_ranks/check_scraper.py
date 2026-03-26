import pandas as pd
import json

def check_env():
    print("--- Environment Check ---")
    try:
        import lxml
        print("lxml: Installed")
    except ImportError:
        print("lxml: NOT Installed")
        
    try:
        # Try fetching gainers
        url = "https://finance.market.com/markets/stocks/gainers/"
        print(f"Testing fetch: {url}")
        tables = pd.read_html(url)
        if tables:
            print(f"Success! Found {len(tables)} tables.")
            print("First few rows of table 0:")
            print(tables[0].head())
        else:
            print("No tables found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_env()

