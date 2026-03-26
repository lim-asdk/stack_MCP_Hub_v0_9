import json
import os
import sys
from datetime import datetime
from kernel_parts.worker import worker_main

def run_bridge():
    print(f"--- Starting yahoo_market_quote bridge ---")
    
    inbox_path = os.path.join(os.path.dirname(__file__), "inbox", "sample_input.json")
    if not os.path.exists(inbox_path):
        inbox_path = os.path.join(os.path.dirname(__file__), "sample_input.json")
        
    try:
        with open(inbox_path, 'r', encoding='utf-8') as f:
            inbox_payload = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to read inbox: {e}")
        return

    print("Invoking worker with Yahoo Market Data query...")
    result = worker_main(inbox_payload)
    
    outbox_dir = os.path.join(os.path.dirname(__file__), "outbox")
    os.makedirs(outbox_dir, exist_ok=True)
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = f"req_yahoo_quote__out.json"
    out_path = os.path.join(outbox_dir, out_file)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"[bridge] Done. Outbox written to outbox\\{out_file}")

if __name__ == "__main__":
    run_bridge()
