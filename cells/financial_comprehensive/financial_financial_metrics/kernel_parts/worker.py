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
            financial_key = apis.get("financial", {}).get("api_key")
        except Exception:
            financial_key = None

        if not financial_key:
            return {"ok": False, "error": "financial API key not found in config"}

        params = inbox_payload.get("message", {}).get("params", {})
        symbol = params.get("symbol")
        
        if not symbol:
            return {"ok": False, "error": "Missing symbol parameter"}
        # Call financial Quote
        url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={financial_key}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        return {
            "ok": True,
            "data": {
                "symbol": symbol,
                "metrics": data
            }
        }
    except Exception as e:
        if "403" in str(e):
            return {"ok": True, "data": {"symbol": symbol, "metrics": []}, "error": "403 Forbidden - financial Free Tier"}
        return {"ok": False, "error": str(e)}


