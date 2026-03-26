import os
import json
from bridge import main

def run_selftest():
    print("--- Starting market_insider_trades selftest ---")
    
    outbox_file = os.path.join("outbox", "req_insider_trades__out.json")
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
            
    print(f"PASS: Fetched insider trades for {message_data.get('symbol')}.")
    transactions = message_data.get("insider_transactions", [])
    print(f"      Total transactions fetched: {len(transactions)}")
    if transactions:
        print(f"      Sample: {transactions[0].get('Insider', 'Unknown')} | Shares: {transactions[0].get('Shares', 0)}")

if __name__ == "__main__":
    run_selftest()

