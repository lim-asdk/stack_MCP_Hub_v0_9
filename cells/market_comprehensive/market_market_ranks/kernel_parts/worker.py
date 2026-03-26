import os
import sys
import json
import requests
import io
from datetime import datetime, timezone
import pandas as pd

def fetch_market_table(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Use io.StringIO to avoid ambiguities in pd.read_html
        tables = pd.read_html(io.StringIO(response.text))
        if not tables:
            return []
            
        df = tables[0]
        results = []
        
        # market's table structure might change, so we use iloc for robustness if name-based fails
        for _, row in df.head(10).iterrows():
            try:
                symbol = str(row.get("Symbol", row.iloc[0]))
                name = str(row.get("Name", row.iloc[1]))
                price = str(row.get("Price (Intraday)", row.get("Price", row.iloc[2])))
                change = str(row.get("Change", row.iloc[3]))
                pct_change = str(row.get("% Change", row.iloc[4]))
                
                # Cleanup: remove '+' and '%' for consistency if needed, but keeping for now
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "price": price,
                    "change": change,
                    "percent_change": pct_change
                })
            except:
                continue
        return results
    except Exception:
        return []

def worker_main(inbox_payload: dict) -> dict:
    try:
        # We fetch Gainers, Losers, and Most Active
        data = {
            "gainers": fetch_market_table("https://finance.market.com/markets/stocks/gainers/"),
            "losers": fetch_market_table("https://finance.market.com/markets/stocks/losers/"),
            "most_active": fetch_market_table("https://finance.market.com/markets/stocks/most-active/"),
            "queried_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "ok": True,
            "data": data
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    # Internal test mode
    res = worker_main({"message": {"params": {}}})
    # Ensure stdout handles potential characters
    try:
        sys.stdout.buffer.write(json.dumps(res, indent=2).encode('utf-8'))
    except:
        pass

