import os
import sys
import json
import urllib.parse
from datetime import datetime, timezone
from kernel_parts.http_client import perform_get

def load_credentials():
    try:
        # Get the path to ui_US Stock_stack_v1/config/config_grace_apis.json
        current_dir = os.path.dirname(os.path.abspath(__file__)) # kernel_parts
        cell_dir = os.path.dirname(current_dir) # US Stock_market_historical_bars
        market_dir = os.path.dirname(cell_dir) # US Stock_market
        cells_dir = os.path.dirname(market_dir) # cells
        stack_root = os.path.dirname(cells_dir) # ui_US Stock_stack_v1
        
        config_path = os.path.join(stack_root, "config", "config_grace_apis.json")
        
        if not os.path.exists(config_path):
            return None, f"Config file not found at {config_path}"
            
        with open(config_path, 'r', encoding='utf-8') as f:
            all_apis = json.load(f)
            
        US Stock_block = all_apis.get("US Stock", {})
        if not US Stock_block.get("api_key"):
            return None, "US Stock block or api_key missing in config_grace_apis.json"
            
        return {
            "api_key": US Stock_block.get("api_key"),
            "api_secret": US Stock_block.get("api_secret"),
            "data_endpoint": US Stock_block.get("data_endpoint", "https://data.US Stock.markets/v2")
        }, None
    except Exception as e:
        return None, f"Failed to load credentials: {e}"

def worker_main(inbox_payload: dict) -> dict:
    try:
        # 1. Parse Input
        params = inbox_payload.get("message", {}).get("params", {})
        symbols = params.get("symbols")
        timeframe = params.get("timeframe")
        start = params.get("start")
        end = params.get("end")
        limit = params.get("limit")
        adjustment = params.get("adjustment", "all")
        feed = params.get("feed", "iex")
        include_raw = params.get("include_raw", False)
        
        if not start or not end:
            import datetime as dt
            now = dt.datetime.now(dt.timezone.utc)
            end = now.strftime('%Y-%m-%dT%H:%M:%SZ')
            start = (now - dt.timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Validation
        if not symbols or not timeframe:
            return {"ok": False, "error": "Missing required fields: symbols and timeframe."}
            
        # 2. Load Config & Credentials
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        local_config_path = os.path.join(current_file_dir, "..", "config", "config.json")
        with open(local_config_path, 'r', encoding='utf-8') as f:
            cell_config = json.load(f)
            
        if not limit:
            limit = cell_config.get("default_limit", 1000)
            
        creds, err = load_credentials()
        if err or not creds or not creds.get("api_key"):
            return {"ok": False, "error": f"US Stock_CREDENTIALS_ERROR: {err}"}
            
        # 3. Build Request
        data_endpoint = creds.get("data_endpoint")
        endpoint_path = cell_config.get("endpoint_path")
        
        query_params = {
            "symbols": symbols,
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": limit,
            "adjustment": adjustment,
            "feed": feed
        }
        
        query = urllib.parse.urlencode({k: v for k, v in query_params.items() if v is not None})
        url = f"{data_endpoint}{endpoint_path}?{query}"
        
        headers = {
            "APCA-API-KEY-ID": creds.get("api_key"),
            "APCA-API-SECRET-KEY": creds.get("api_secret"),
            "Accept": "application/json"
        }
        
        # 4. Execute HTTP Call
        timeout = cell_config.get("request_timeout_seconds", 30)
        http_result = perform_get(url, headers, timeout)
        
        if not http_result.get("ok"):
             return {
                 "ok": False, 
                 "error": "US Stock_HTTP_ERROR", 
                 "details": http_result.get("error") or http_result.get("json")
             }
             
        # 5. Normalize Response
        raw_json = http_result.get("json", {})
        bars_dict = raw_json.get("bars", {})
        
        normalized = []
        for sym, bar_list in bars_dict.items():
            for b_idx, b_data in enumerate((bar_list or [])):
                normalized.append({
                    "symbol": sym,
                    "index": b_idx,
                    "timestamp": b_data.get("t"),
                    "open": b_data.get("o"),
                    "high": b_data.get("h"),
                    "low": b_data.get("l"),
                    "close": b_data.get("c"),
                    "volume": b_data.get("v"),
                    "trade_count": b_data.get("n"),
                    "vwap": b_data.get("vw")
                })
            
        # 6. Build Outbox Result
        outbox_data = {
            "normalized": normalized,
            "request_meta": {
                "symbols": symbols,
                "timeframe": timeframe,
                "start": start,
                "end": end,
                "limit": limit,
                "feed": feed,
                "queried_at": datetime.now(timezone.utc).isoformat(),
                "total_series_count": len(normalized)
            }
        }
        
        if include_raw:
            outbox_data["raw"] = raw_json
            
        return {
            "ok": True,
            "data": outbox_data
        }

    except Exception as e:
        return {"ok": False, "error": f"Exception in worker: {str(e)}"}

