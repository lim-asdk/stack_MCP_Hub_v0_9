import os
import json
import urllib.request
from datetime import datetime, timezone

def worker_main(inbox_payload: dict) -> dict:
    try:
        # Load Config
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "..", "..", "..", "..", "config", "config_grace_apis.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                apis = json.load(f)
            fmp_key = apis.get("fmp", {}).get("api_key")
        except Exception:
            fmp_key = None

        if not fmp_key:
            return {"ok": False, "error": "FMP API key not found in config"}

        params = inbox_payload.get("message", {}).get("params", {})
        symbol = params.get("symbol")
        
        if not symbol:
            return {"ok": False, "error": "Missing symbol parameter"}
        
        url = f"https://financialmodelingprep.com/api/v3/institutional-holder/{symbol}?apikey={fmp_key}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        return {
            "ok": True,
            "data": {
                "symbol": symbol,
                "institutionalHolders": data[:10] if isinstance(data, list) else data
            }
        }
    except Exception as e:
        if "403" in str(e):
            return {"ok": True, "data": {"symbol": symbol, "institutionalHolders": []}, "error": "403 Forbidden - FMP Free Tier"}
        return {"ok": False, "error": str(e)}
