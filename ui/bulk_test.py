import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

# Fix for Windows encoding in terminal
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from universal_cell_server import execute_cell_worker, get_all_tool_names
except ImportError:
    print("Error: Could not find universal_cell_server.py")
    sys.exit(1)

async def run_diagnostic():
    tools = get_all_tool_names()
    print(f"=== Starting Bulk Diagnostic for {len(tools)} Cells ===")
    
    symbol = "NVDA"
    # Dates for historical bars
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    results = []
    
    for tool in tools:
        print(f"Testing [{tool}]...", end=" ", flush=True)
        try:
            # Default params
            params = {"symbols": symbol, "ticker": symbol, "symbol": symbol, "query": symbol}
            
            # Specific overrides for complex tools
            if "historical_bars" in tool:
                params.update({
                    "timeframe": "1Day",
                    "start": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                    "end": end_date.strftime("%Y-%m-%dT00:00:00Z")
                })
            
            res = await execute_cell_worker(tool, params)
            
            if res.get("ok"):
                print("OK")
                results.append((tool, True, "Success"))
            else:
                err = res.get("error", "Unknown error")
                print(f"FAIL: {err}")
                results.append((tool, False, err))
        except Exception as e:
            print(f"CRITICAL: {e}")
            results.append((tool, False, str(e)))
            
    print("\n=== DIAGNOSTIC SUMMARY ===")
    success_count = 0
    for tool, ok, detail in results:
        status = "[V]" if ok else "[X]"
        print(f"{status} {tool}: {detail}")
        if ok: success_count += 1
        
    print(f"\nFinal Score: {success_count}/{len(tools)}")
    
    if success_count < len(tools):
        print("\nSome cells require attention (Check API Key tiers or Parameters).")

if __name__ == "__main__":
    asyncio.run(run_diagnostic())
