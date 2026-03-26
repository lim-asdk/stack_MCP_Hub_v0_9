import sys
import os
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp_hub.server import register_all_tools, mcp

# Starlette/FastMCP sometimes needs ALLOWED_HOSTS if accessed via IP in some cloud setups
os.environ["ALLOWED_HOSTS"] = "*"

if __name__ == "__main__":
    # Sticking with 19020 (known clean port in allow-v6-web range)
    PORT = 19021
    print(f"=== US Stock MCP Hub (SSE/HTTP) Starting with Hypercorn on http://0.0.0.0:{PORT} ===", file=sys.stderr)
    
    register_all_tools()
    
    import uvicorn
    # Use Uvicorn for native ASGI support to avoid Hypercorn's 500 error
    # proxy_headers and forwarded_allow_ips are still key for GCP
    uvicorn.run(
        mcp.sse_app, 
        host="0.0.0.0", 
        port=PORT, 
        proxy_headers=True, 
        forwarded_allow_ips="*"
    )

