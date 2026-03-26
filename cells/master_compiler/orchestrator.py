import os
import sys
import json
import concurrent.futures
import subprocess
from datetime import datetime, timezone

from compiler import collect_and_compile

def run_worker_in_subprocess(cell_dir, payload):
    runner_code = """
import sys
import json
from kernel_parts.worker import worker_main

try:
    payload = json.loads(sys.argv[1])
    res = worker_main(payload)
    print(json.dumps(res))
except Exception as e:
    print(json.dumps({"ok": False, "error": str(e)}))
"""
    try:
        cmd = [sys.executable, "-c", runner_code, json.dumps(payload)]
        proc = subprocess.run(cmd, cwd=cell_dir, capture_output=True, text=True, timeout=45)
        if proc.returncode != 0:
            return {"ok": False, "error": f"Process failed: {proc.stderr}"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Worker process timed out (20s limit)"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    try:
        # Some workers might print extra logs, so we try to find the final line that is JSON
        lines = proc.stdout.strip().split('\n')
        for line in reversed(lines):
            try:
                return json.loads(line)
            except:
                pass
        return {"ok": False, "error": f"Failed to parse JSON from stdout: {proc.stdout[:200]}"}
    except Exception as e:
        return {"ok": False, "error": f"Exception parsing: {e}"}

def _run_worker_and_save(cell_rel_path, symbol, payload_override=None):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cells_dir = os.path.dirname(current_dir)
        
        cell_dir = os.path.join(cells_dir, *cell_rel_path.split("/"))
        cell_name = cell_rel_path.split("/")[-1]
        outbox_path = os.path.join(cell_dir, "outbox", f"req_{cell_name.split('_', 1)[-1]}__out.json")
        if "historical_bars" in cell_name:
             outbox_path = os.path.join(cell_dir, "outbox", f"req_historical_bars__out.json")
        
        payload = {"message": {"params": {"symbol": symbol}}}
        if payload_override:
             payload["message"]["params"].update(payload_override)
             
        res = run_worker_in_subprocess(cell_dir, payload)
        
        outbox_payload = {
            "message": {
                "source": "orchestrator_trigger",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": res.get("data", {}),
                "error": res.get("error")
            },
            "status": "OK" if res.get("ok") else "FAIL"
        }
        os.makedirs(os.path.dirname(outbox_path), exist_ok=True)
        with open(outbox_path, 'w', encoding='utf-8') as f:
            json.dump(outbox_payload, f, indent=2, ensure_ascii=False)
            
        return outbox_path
    except Exception as e:
        print(f"[Orchestrator] Error generating outbox for {cell_rel_path}: {e}")
        return None

def orchestrate_tiger(symbol: str):
    print(f"--- [Master Orchestrator] Triggering Subprocess Execution for {symbol} ---")
    
    tasks = [
         ("market_comprehensive/market_company_profile", symbol, None),
         ("market_comprehensive/market_analyst_ratings", symbol, None),
         ("market_comprehensive/market_insider_trades", symbol, None),
         ("market_comprehensive/market_fin_statements", symbol, None),
         ("financial_comprehensive/financial_financial_metrics", symbol, None),
         ("analyst_comprehensive/analyst_company_news", symbol, None),
         ("analyst_comprehensive/analyst_peers", symbol, None),
         ("US Stock_market/US Stock_market_historical_bars", symbol, {"symbols": symbol, "timeframe": "1Day"}),
         ("market_comprehensive/market_market_ranks", symbol, None)
    ]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for cell_rel, sym, payload in tasks:
             futures.append(executor.submit(_run_worker_and_save, cell_rel, sym, payload))
             
        # Wait for critical tasks first if possible, or just wait with a total cap
        concurrent.futures.wait(futures, timeout=50)
        
    print(f"[Master Orchestrator] All subprocess tasks finished. Initiating compilation...")
    final_outbox = collect_and_compile(symbol)
    print(f"[Master Orchestrator] Done! Master payload ready at: {final_outbox}")
    return final_outbox

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_symbol = sys.argv[1]
    else:
        target_symbol = "NVDA"
    orchestrate_tiger(target_symbol)

