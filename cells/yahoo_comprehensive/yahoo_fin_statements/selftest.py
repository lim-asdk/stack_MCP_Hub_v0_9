import os
import json
from bridge import main

def run_selftest():
    print("--- Starting yahoo_fin_statements selftest ---")
    
    outbox_file = os.path.join("outbox", "req_fin_statements__out.json")
    if os.path.exists(outbox_file):
        os.remove(outbox_file)
        
    main()
    
    if not os.path.exists(outbox_file):
        print("FAIL: Outbox file was not created.")
        exit(1)
        
    with open(outbox_file, 'r', encoding='utf-8') as f:
        outbox_data = json.load(f)
        
    status = outbox_data.get("status")
    message_data = outbox_data.get("message", {}).get("data", {})
    error = outbox_data.get("message", {}).get("error")
    
    if status != "OK":
        print(f"FAIL: Expected status OK, got {status}. Error: {error}")
        exit(1)
            
    print(f"PASS: Fetched financial statements for {message_data.get('symbol')}.")
    fins = message_data.get("financials", [])
    holders = message_data.get("institutional_holders", [])
    
    print(f"      Financials fetched: {len(fins)} periods")
    if fins:
         print(f"      Sample Data ({fins[0].get('Date')}): Revenue={fins[0].get('Total Revenue')}, Net Income={fins[0].get('Net Income')}")
    print(f"      Institutional Holders fetched: {len(holders)}")
    if holders:
         print(f"      Top Holder: {holders[0].get('Holder')}")

if __name__ == "__main__":
    run_selftest()
