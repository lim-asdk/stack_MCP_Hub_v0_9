import os
import json
from bridge import main

def run_selftest():
    print("--- Starting yahoo_analyst_ratings selftest ---")
    
    outbox_file = os.path.join("outbox", "req_analyst_ratings__out.json")
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
        
    if not message_data:
        print("FAIL: 'data' is empty, no ratings returned.")
        exit(1)
            
    print(f"PASS: Fetched ratings for {message_data.get('symbol')}.")
    consensus = message_data.get('consensus', {})
    print(f"      Recommendation: {consensus.get('recommendationKey')} (Mean: {consensus.get('recommendationMean')})")
    print(f"      Target Price Mean: {consensus.get('targetMeanPrice')}")

if __name__ == "__main__":
    run_selftest()
