import sys
import os
import json

# Add worker to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "kernel_parts"))

from worker import worker_main

def run_test():
    print("Starting ranking cell self-test...")
    result = worker_main({"message": {"params": {}}})
    
    # Save to outbox
    out_dir = os.path.join(current_dir, "outbox")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "market_ranks__out.json")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    if result.get("ok"):
        print("Test SUCCESS.")
        count = len(result['data']['gainers']) + len(result['data']['losers']) + len(result['data']['most_active'])
        print(f"Total items collected: {count}")
        print(f"Output saved to: {out_path}")
    else:
        print(f"Test FAILED: {result.get('error')}")

if __name__ == "__main__":
    run_test()

