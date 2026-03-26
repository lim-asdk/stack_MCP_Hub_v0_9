import os
import json
from bridge import main

def run_selftest():
    print("--- Starting US Stock_config_loader selftest ---")
    
    # 1. Ensure outbox is clean
    outbox_file = os.path.join("outbox", "req_config_load__out.json")
    if os.path.exists(outbox_file):
        os.remove(outbox_file)
        
    # 2. Run bridge
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
        
    if not message_data.get("credentials_present"):
        print("FAIL: credentials_present is not True.")
        exit(1)
        
    # Security check: Ensure secret is NOT in the outbox
    outbox_str = json.dumps(outbox_data)
    if "api_secret" in outbox_str and not "api_secret missing" in outbox_str: # checking for variable name leak
        print("FAIL: SECURITY RISK - Suspicious key 'api_secret' found in outbox dump.")
        exit(1)
        
    print("PASS: US Stock_config_loader successfully loaded keys and protected secrets.")

if __name__ == "__main__":
    run_selftest()
