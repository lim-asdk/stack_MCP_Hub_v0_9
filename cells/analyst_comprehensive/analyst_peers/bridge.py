import os
import json
from datetime import datetime, timezone
from kernel_parts.worker import worker_main

def main():
    try:
        with open('inbox/sample_input.json', 'r', encoding='utf-8') as f:
            inbox_data = json.load(f)
    except Exception as e:
        print(f"[bridge] failed to read sample_input: {e}")
        return

    result = worker_main(inbox_data)
    
    outbox_payload = {
        "message": {
            "source": "analyst_peers",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": result.get("data", {}),
            "error": result.get("error"),
            "details": result.get("details")
        },
        "status": "OK" if result.get("ok") else "FAIL",
        "lim_aplc": inbox_data.get("lim_aplc", {})
    }
    
    os.makedirs("outbox", exist_ok=True)
    outbox_path = os.path.join("outbox", "req_peers__out.json")
    with open(outbox_path, 'w', encoding='utf-8') as f:
        json.dump(outbox_payload, f, indent=2, ensure_ascii=False)
        
    print(f"[bridge] Done. Outbox written to {outbox_path}")

if __name__ == "__main__":
    main()

