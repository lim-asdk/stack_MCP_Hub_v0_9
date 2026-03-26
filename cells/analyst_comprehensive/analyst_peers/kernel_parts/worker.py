import os
import json
import urllib.request

def worker_main(inbox_payload: dict) -> dict:
    try:
        # Load Config
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "..", "..", "..", "..", "config", "config_grace_apis.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                apis = json.load(f)
            analyst_key = apis.get("analyst", {}).get("api_key")
        except Exception:
            analyst_key = None

        if not analyst_key:
            return {"ok": False, "error": "analyst API key not found in config"}

        params = inbox_payload.get("message", {}).get("params", {})
        symbol = params.get("symbol")
        
        if not symbol:
            return {"ok": False, "error": "Missing symbol parameter"}
        
        url = f"https://analyst.io/api/v1/stock/peers?symbol={symbol}&token={analyst_key}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        return {
            "ok": True,
            "data": {
                "symbol": symbol,
                "peers": data
            }
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

