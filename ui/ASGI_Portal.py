import os
import sys
import json
import asyncio
import threading
from pathlib import Path
from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp_hub import server
from mcp_hub.server import mcp, register_all_tools

UI_DIR = Path(__file__).resolve().parent
PORT = 6991

# --- API HANDLERS ---
async def get_tools(request):
    return JSONResponse({"tools": server.get_all_tool_names()})

async def get_tool_metadata(request):
    name = request.path_params["name"]
    return JSONResponse(server.get_tool_metadata(name))

async def call_tool(request):
    idx = await request.json()
    tool_name = idx.get("tool_name") or idx.get("tool")
    symbol = idx.get("symbol") or idx.get("input")
    
    try:
        # Starlette is already in an event loop
        result = await server.execute_cell_worker(tool_name, symbol)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"Bridge Error: {str(e)}"}, status_code=500)

async def serve_index(request):
    return FileResponse(UI_DIR / "index.html")

# --- PROXY/MOUNT LOGIC ---
# Register all tools into the global MCP instance
register_all_tools()

# Build the main app
routes = [
    Route("/", serve_index),
    Route("/api/tools", get_tools),
    Route("/api/metadata/{name}", get_tool_metadata),
    Route("/api/call", call_tool, methods=["POST"]),
    Mount("/sse", mcp.sse_app),  # IMPORTANT: Native mount of the MCP SSE app
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
]

app = Starlette(routes=routes, middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    # IMPORTANT: We use 6991 because it's a proven open port for this user.
    # proxy_headers=True is needed for GCP host/ip resolution.
    print(f"=== US Stock MCP Unified ASGI Portal Starting on http://0.0.0.0:{PORT} ===")
    uvicorn.run(app, host="0.0.0.0", port=PORT, proxy_headers=True, forwarded_allow_ips="*")
