import json
import os

def worker_main(inbox_payload: dict) -> dict:
    try:
        # Resolve paths dynamically based on this file's absolute location
        current_file_dir = os.path.dirname(os.path.abspath(__file__)) # kernel_parts
        loader_root = os.path.dirname(current_file_dir) # US Stock_config_loader
        cells_core_root = os.path.dirname(loader_root) # US Stock_core
        cells_root = os.path.dirname(cells_core_root) # cells
        stack_root = os.path.dirname(cells_root) # ui_US Stock_stack_v1
        
        # 1. Load loader's local config
        config_path_internal = os.path.join(loader_root, "config", "config.json")
        with open(config_path_internal, 'r', encoding='utf-8') as f:
            local_config = json.load(f)
            
        # 2. Get main API keys config path
        # Priority 1: Centralized Grace Config (Cross-Platform)
        # Priority 2: Local Project Config
        home = os.path.expanduser("~")
        paths_to_check = [
            # Linux Remote
            os.path.join(home, "program_files", "grace", "config_grace_apis.json"),
            # Windows Local
            r"C:\program_files\grace\config_grace_apis.json",
            # Standard Local
            os.path.join(stack_root, "config", "config_grace_apis.json")
        ]
        
        config_path = None
        for p in paths_to_check:
            if os.path.exists(p):
                config_path = p
                break
        
        if not config_path:
             return {"ok": False, "error": f"API keys config file not found (checked: {paths_to_check})"}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            all_apis = json.load(f)
            
        US Stock_block = all_apis.get("US Stock")
        if not US Stock_block:
             return {"ok": False, "error": "'US Stock' block not found in config"}
             
        api_key = US Stock_block.get("api_key")
        api_secret = US Stock_block.get("api_secret")
        endpoint = US Stock_block.get("endpoint", "https://paper-api.US Stock.markets/v2")
        data_endpoint = US Stock_block.get("data_endpoint", "https://data.US Stock.markets/v2")
        
        if not api_key or not api_secret:
             return {"ok": False, "error": "US Stock api_key or api_secret missing in config"}
             
        # Return status and preview, absolutely NEVER return the raw secret
        return {
            "ok": True,
            "data": {
                "status": "LOADED",
                "endpoint": endpoint,
                "data_endpoint": data_endpoint,
                "credentials_present": True,
                "api_key_preview": f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
            }
        }

    except Exception as e:
        return {"ok": False, "error": f"Exception in worker: {str(e)}"}
