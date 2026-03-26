import requests
from bottle import Bottle, request, response, HTTPResponse
import time

app = Bottle()

# The local Hub moved to 19021
LOCAL_HUB_URL = "http://127.0.0.1:19021/sse"

@app.route('/sse', method=['GET', 'POST', 'OPTIONS'])
def proxy_sse():
    if request.method == 'OPTIONS':
        return ""
        
    print(f"[GATEWAY] Proxying {request.method} to {LOCAL_HUB_URL}")
    
    try:
        # We use a streaming request to forward the SSE events
        if request.method == 'POST':
            res = requests.post(LOCAL_HUB_URL, json=request.json or {}, stream=True, timeout=600)
        else:
            res = requests.get(LOCAL_HUB_URL, params=request.query, stream=True, timeout=600)
            
        # Manually construct the response to ensure streaming
        response.status = res.status_code
        for k, v in res.headers.items():
            if k.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                response.set_header(k, v)
        
        # Explicitly set headers for SSE proxying
        response.set_header('Content-Type', 'text/event-stream')
        response.set_header('Cache-Control', 'no-cache')
        response.set_header('X-Accel-Buffering', 'no')
        response.set_header('Connection', 'keep-alive')
        
        # Increase timeout for the stream
        return res.iter_content(chunk_size=1)
        
    except Exception as e:
        print(f"[GATEWAY ERROR] {e}")
        return HTTPResponse(status=502, body=str(e))

@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'

if __name__ == "__main__":
    PORT = 6992
    print(f"=== US Stock MCP Bottle Gateway Starting on http://0.0.0.0:{PORT}/sse ===")
    app.run(host='0.0.0.0', port=PORT, server='waitress')

