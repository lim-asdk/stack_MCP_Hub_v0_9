import json
import uuid
from kernel_parts.worker import worker_main

def main():
    print("--- Starting yahoo_market_quote selftest ---")
    
    inbox_payload = {
        "request_id": "test_" + uuid.uuid4().hex[:8],
        "message": {
            "params": {
                "symbols": "AAPL,TSLA"
            }
        }
    }
    
    print("Test Payload created. Calling worker_main directly...")
    result = worker_main(inbox_payload)
    
    if result.get("ok"):
        print("PASS: Success! Response from Worker:")
        res_str = json.dumps(result, indent=2, ensure_ascii=False)
        print(res_str[:500] + "\n... (truncated)")
    else:
        print("FAIL!")
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
