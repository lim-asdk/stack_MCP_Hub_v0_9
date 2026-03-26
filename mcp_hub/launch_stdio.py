import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp_hub.server import register_all_tools, mcp

if __name__ == "__main__":
    print("=== US Stock MCP Hub (STDIO Port) Starting... ===", file=sys.stderr)
    register_all_tools()
    mcp.run()

