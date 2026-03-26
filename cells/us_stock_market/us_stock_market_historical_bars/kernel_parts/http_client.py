import urllib.request
import urllib.error
import json
import traceback

def perform_get(url: str, headers: dict = None, timeout: int = 15) -> dict:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {"raw_body": body}
                
            return {
                "ok": True,
                "status_code": status_code,
                "json": data
            }
            
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            err_json = json.loads(err_body)
        except Exception:
            err_json = {"raw_error": err_body if 'err_body' in locals() else str(e)}
            
        return {
            "ok": False,
            "status_code": e.code,
            "error": f"HTTPError {e.code}: {e.reason}",
            "json": err_json
        }
        
    except urllib.error.URLError as e:
        return {
            "ok": False,
            "error": f"URLError: {e.reason}"
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": f"Exception: {str(e)}\n{traceback.format_exc()}"
        }

