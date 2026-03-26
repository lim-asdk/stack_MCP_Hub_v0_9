import os
import sys
import json
import asyncio
import threading
import webbrowser
import requests
from pathlib import Path
from bottle import Bottle, request, response, static_file, HTTPResponse

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp_hub import server

app = Bottle()
UI_DIR = Path(__file__).resolve().parent
PORT = 6991

# Internal Hub URL
LOCAL_HUB_URL = "http://127.0.0.1:19021/sse"

@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'

@app.get("/")
def serve_index():
    return static_file("index.html", root=UI_DIR)

# --- SSE PROXY ENDPOINT ---
# Merged into 6991 because this port is already proven to be open and working.
@app.route('/sse', method=['GET', 'POST', 'OPTIONS'])
def proxy_sse():
    if request.method == 'OPTIONS':
        return ""
        
    print(f"[GATEWAY] Proxying {request.method} to {LOCAL_HUB_URL}")
    
    try:
        # Use streaming forward for SSE
        if request.method == 'POST':
            res = requests.post(LOCAL_HUB_URL, json=request.json or {}, stream=True, timeout=600)
        else:
            res = requests.get(LOCAL_HUB_URL, params=request.query, stream=True, timeout=600)
            
        response.status = res.status_code
        for k, v in res.headers.items():
            if k.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                response.set_header(k, v)
        
        response.set_header('Content-Type', 'text/event-stream')
        response.set_header('Cache-Control', 'no-cache')
        response.set_header('X-Accel-Buffering', 'no')
        response.set_header('Connection', 'keep-alive')
        
        return res.iter_content(chunk_size=1)
        
    except Exception as e:
        print(f"[GATEWAY ERROR] {e}")
        return HTTPResponse(status=502, body=str(e))

@app.get("/api/tools")
def get_tools():
    return {"tools": server.get_all_tool_names()}

@app.get("/api/metadata/<name>")
def get_tool_metadata(name):
    return server.get_tool_metadata(name)

@app.route('/api/call', method='POST')
def call_tool():
    idx = request.json or {}
    tool_name = idx.get("tool_name") or idx.get("tool")
    symbol = idx.get("symbol") or idx.get("input")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(server.execute_cell_worker(tool_name, symbol))
            return result
        finally:
            loop.close()
    except Exception as e:
        return {"ok": False, "error": f"Bridge Error: {str(e)}"}

if __name__ == "__main__":
    url = f"http://127.0.0.1:{PORT}/?v=1"
    print(f"=== US Stock MCP Unified Portal Starting on {url} ===")
    
    # Pre-build tool index
    threading.Thread(target=server.get_all_tool_names, daemon=True).start()
    
    # Non-blocking browser launch
    threading.Timer(2.0, lambda: webbrowser.open_new(url)).start()
    
    # Robust server selection (local fallback for waitress)
    try:
        import waitress
        server_choice = 'waitress'
        print("[SYSTEM] Using Waitress server (Production-grade)")
    except ImportError:
        server_choice = 'wsgiref'
        print("[SYSTEM] Using default wsgiref server (Waitress not found)")
        
    app.run(host='0.0.0.0', port=PORT, server=server_choice, debug=True, reloader=False)
