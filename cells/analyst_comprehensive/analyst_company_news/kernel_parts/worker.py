import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone

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

        # Get news for the last 30 days
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        url = f"https://analyst.io/api/v1/company-news?symbol={symbol}&from={from_date.strftime('%Y-%m-%d')}&to={to_date.strftime('%Y-%m-%d')}&token={analyst_key}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        return {
            "ok": True,
            "data": {
                "symbol": symbol,
                "news": data[:20] if isinstance(data, list) else data
            }
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

