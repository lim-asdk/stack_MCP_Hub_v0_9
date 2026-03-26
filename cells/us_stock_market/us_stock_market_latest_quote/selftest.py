import os
import json
from bridge import main

def run_selftest():
    print("--- Starting US Stock_market_latest_quote selftest ---")
    
    # 1. Ensure outbox is clean
    outbox_file = os.path.join("outbox", "req_latest_quote__out.json")
    if os.path.exists(outbox_file):
        os.remove(outbox_file)
        
    # 2. Run bridge Live
    print("Invoking bridge with real US Stock Market Data query...")
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
        
    normalized = message_data.get("normalized", [])
    if not normalized:
        print("FAIL: 'normalized' array is empty, no quote data returned.")
        exit(1)
        
    first_quote = normalized[0]
    required_keys = ["symbol", "ask_price", "bid_price", "timestamp"]
    for k in required_keys:
        if k not in first_quote:
            print(f"FAIL: Missing required normalized key '{k}' in result {first_quote}")
            exit(1)
            
    print(f"PASS: Latest quote for {first_quote.get('symbol')} was successfully fetched (Bid: ${first_quote.get('bid_price')} / Ask: ${first_quote.get('ask_price')}).")

if __name__ == "__main__":
    run_selftest()
