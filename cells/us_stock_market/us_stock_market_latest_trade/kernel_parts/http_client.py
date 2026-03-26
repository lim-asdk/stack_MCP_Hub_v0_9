import urllib.request
import urllib.error
import urllib.parse
import json

def perform_get(url: str, headers: dict, timeout_seconds: int = 15) -> dict:
    req = urllib.request.Request(url, headers=headers, method='GET')
    
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            status_code = response.getcode()
            response_body = response.read()
            
            try:
                json_data = json.loads(response_body)
            except json.JSONDecodeError:
                json_data = None
                
            return {
                "http_status": status_code,
                "ok": 200 <= status_code < 300,
                "json": json_data,
                "text_preview": response_body.decode('utf-8')[:500] if not json_data else "",
                "error": None
            }
            
    except urllib.error.HTTPError as e:
        response_body = e.read()
        try:
            error_json = json.loads(response_body)
        except json.JSONDecodeError:
            error_json = None
            
        return {
            "http_status": e.code,
            "ok": False,
            "json": error_json,
            "text_preview": response_body.decode('utf-8')[:500] if not error_json else "",
            "error": f"HTTPError: {e.reason}"
        }
        
    except urllib.error.URLError as e:
        return {
            "http_status": 0,
            "ok": False,
            "json": None,
            "text_preview": "",
            "error": f"URLError: {e.reason}"
        }
    except Exception as e:
        return {
            "http_status": 0,
            "ok": False,
            "json": None,
            "text_preview": "",
            "error": f"Exception: {str(e)}"
        }

