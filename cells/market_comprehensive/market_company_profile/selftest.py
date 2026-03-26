import os
import json
from bridge import main

def run_selftest():
    print("--- Starting market_company_profile selftest ---")
    
    # 1. Ensure outbox is clean
    outbox_file = os.path.join("outbox", "req_company_profile__out.json")
    if os.path.exists(outbox_file):
        os.remove(outbox_file)
        
    # 2. Run bridge script
    print("Invoking bridge for company profile query...")
    main()
    
    # 3. Verify outbox
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
        
    if not message_data:
        print("FAIL: 'data' is empty, no profile data returned.")
        exit(1)
        
    required_keys = ["symbol", "company_name", "sector", "summary", "market_cap"]
    for k in required_keys:
        if k not in message_data:
            print(f"FAIL: Missing required key '{k}' in result.")
            exit(1)
            
    print(f"PASS: Fetched company profile for {message_data.get('symbol')}.")
    print(f"      Name: {message_data.get('company_name')}")
    print(f"      Sector: {message_data.get('sector')}")
    print(f"      Summary: {message_data.get('summary')[:50]}...")

if __name__ == "__main__":
    run_selftest()

