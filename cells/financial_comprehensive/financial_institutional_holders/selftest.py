import os
import json
from bridge import main

def run_selftest():
    print("--- Starting financial_institutional_holders selftest ---")
    
    outbox_file = os.path.join("outbox", "req_institutions__out.json")
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
            
    print(f"PASS: Fetched institutional holders for {message_data.get('symbol')}.")
    holders = message_data.get("institutionalHolders", [])
    print(f"      Top holders count: {len(holders)}")
    if holders:
        print(f"      Top: {holders[0].get('holder')} ({holders[0].get('shares')} shares)")

if __name__ == "__main__":
    run_selftest()

