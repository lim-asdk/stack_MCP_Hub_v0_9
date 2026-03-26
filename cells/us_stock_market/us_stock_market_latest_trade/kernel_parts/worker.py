import os
import sys
import json
import urllib.parse
from datetime import datetime, timezone
from kernel_parts.http_client import perform_get

# Add core path to sys.path to load US Stock_config_loader
current_dir = os.path.dirname(os.path.abspath(__file__))
cell_root = os.path.dirname(current_dir)
stack_root = os.path.dirname(os.path.dirname(cell_root))
sys.path.insert(0, os.path.join(stack_root, "cells", "US Stock_core", "US Stock_config_loader"))

def load_credentials():
    try:
        # Get the path to ui_US Stock_stack_v1/config/config_grace_apis.json
        current_dir = os.path.dirname(os.path.abspath(__file__)) # kernel_parts
        cell_dir = os.path.dirname(current_dir) # US Stock_market_latest_trade
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
        feed = params.get("feed", "iex")
        include_raw = params.get("include_raw", False)
        
        if not symbols:
            return {"ok": False, "error": "Missing required field: symbols"}
            
        # 2. Load Config & Credentials
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        local_config_path = os.path.join(current_file_dir, "..", "config", "config.json")
        with open(local_config_path, 'r', encoding='utf-8') as f:
            cell_config = json.load(f)
            
        creds, err = load_credentials()
        if err or not creds or not creds.get("api_key"):
            return {"ok": False, "error": f"US Stock_CREDENTIALS_ERROR: {err}"}
            
        # 3. Build Request
        data_endpoint = creds.get("data_endpoint")
        endpoint_path = cell_config.get("endpoint_path")
        
        query = urllib.parse.urlencode({
            "symbols": symbols,
            "feed": feed
        })
        url = f"{data_endpoint}{endpoint_path}?{query}"
        
        headers = {
            "APCA-API-KEY-ID": creds.get("api_key"),
            "APCA-API-SECRET-KEY": creds.get("api_secret"),
            "Accept": "application/json"
        }
        
        # 4. Execute HTTP Call
        timeout = cell_config.get("request_timeout_seconds", 15)
        http_result = perform_get(url, headers, timeout)
        
        if not http_result.get("ok"):
             return {
                 "ok": False, 
                 "error": "US Stock_HTTP_ERROR", 
                 "details": http_result.get("error") or http_result.get("json")
             }
             
        # 5. Normalize Response
        raw_json = http_result.get("json", {})
        trades = raw_json.get("trades", {})
        
        normalized = []
        for sym, trade_data in trades.items():
            normalized.append({
                "symbol": sym,
                "price": trade_data.get("p"),
                "size": trade_data.get("s"),
                "timestamp": trade_data.get("t"),
                "exchange_code": trade_data.get("x")
            })
            
        # 6. Build Outbox Result
        outbox_data = {
            "normalized": normalized,
            "request_meta": {
                "symbols": symbols,
                "feed": feed,
                "queried_at": datetime.now(timezone.utc).isoformat()
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

