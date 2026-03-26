import os
import sys
import json
import asyncio
import threading
import webview
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp_hub import server as universal_cell_server

class Bridge:
    def __init__(self, loop):
        self._loop = loop
        self._tool_list_cache = None
        self._metadata_cache = {}

    def get_tool_list(self):
        if self._tool_list_cache is None:
            self._tool_list_cache = universal_cell_server.get_all_tool_names()
        return json.dumps(self._tool_list_cache)

    def get_tool_metadata(self, tool_name):
        if tool_name not in self._metadata_cache:
            self._metadata_cache[tool_name] = universal_cell_server.get_tool_metadata(tool_name)
        return json.dumps(self._metadata_cache[tool_name])

    def call_tool_poc(self, tool_name, raw_input):
        # Use localized loop for thread safety
        future = asyncio.run_coroutine_threadsafe(
            universal_cell_server.execute_cell_worker(tool_name, raw_input),
            self._loop,
        )
        try:
            return json.dumps(future.result(timeout=40))
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def main():
    print("=== Starting US Stock MCP Desktop Launcher (Native) ===")
    
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=run_asyncio_loop, args=(loop,), daemon=True)
    t.start()
    
    # Pre-build tool index in background for instant UI response
    print("[SYSTEM] Initializing Desktop tool index in background...")
    threading.Thread(target=universal_cell_server.get_all_tool_names, daemon=True).start()

    bridge = Bridge(loop)
    html_path = Path(__file__).resolve().parent / "index.html"
    
    window = webview.create_window(
        "US Stock MCP Universal Cell Tester (Desktop)",
        str(html_path),
        js_api=bridge,
        width=1400,
        height=900
    )
    
    # Start the desktop window (Native Edge/Chrome WebView)
    print("=== GUI Window Initialized. Please check your desktop/taskbar. ===")
    webview.start(debug=False, http_server=True, gui="edgechromium")

if __name__ == "__main__":
    main()
