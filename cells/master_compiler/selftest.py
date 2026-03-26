import os
import json
import time
from orchestrator import orchestrate_tiger

def run_selftest():
    print("--- Starting master_compiler selftest ---")
    
    outbox_file = os.path.join("outbox", "master_bundle__out.json")
    if os.path.exists(outbox_file):
        os.remove(outbox_file)
        
    start_time = time.time()
    
    # Run the orchestrator on AAPL
    orchestrate_tiger("AAPL")
    
    elapsed = time.time() - start_time
    print(f"[Selftest] Orchestration completed in {elapsed:.2f} seconds.")
    
    if not os.path.exists(outbox_file):
        print("FAIL: Master bundle was not created.")
        exit(1)
        
    with open(outbox_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
        
    ui_zones = master_data.get("ui_zones", {})
    price_action = ui_zones.get("price_action", {}).get("chart_data", [])
    news = ui_zones.get("news_sentiment", {}).get("latest_news", [])
    
    if not price_action:
         print("WARNING/FAIL: Price Action chart data is empty.")
    else:
         print(f"PASS: Found {len(price_action)} bars for Price Action.")
         
    if not news:
         print("WARNING: News sentiment data is empty.")
    else:
         print(f"PASS: Found {len(news)} news articles.")
         
    print(f"PASS: Master payload check complete for {master_data.get('symbol')}.")

if __name__ == "__main__":
    run_selftest()
