import yfinance as yf
import pandas as pd
import numpy as np

def clean_nan(val):
    if pd.isna(val) or val is None or val == "NaN":
        return None
    return val

def worker_main(inbox_payload: dict) -> dict:
    try:
        params = inbox_payload.get("message", {}).get("params", {})
        symbol = params.get("symbol")
        
        if not symbol:
            return {"ok": False, "error": "Missing required field: symbol"}
            
        ticker = yf.Ticker(symbol)
        
        # 1. Financials (Income Statement)
        try:
            fin_df = ticker.financials
        except Exception:
            fin_df = pd.DataFrame()
            
        financials_list = []
        if fin_df is not None and not fin_df.empty:
            # We want headers (Total Revenue, Operating Income, Net Income)
            # and col names are dates.
            # Transpose to make dates the rows, and metrics the columns.
            fin_df_t = fin_df.T
            
            # Select key metrics if available
            key_metrics = ["Total Revenue", "Operating Income", "Net Income", "Gross Profit", "EBITDA"]
            available_metrics = [m for m in key_metrics if m in fin_df_t.columns]
            
            recent_fins = fin_df_t[available_metrics].head(4).reset_index()
            # Rename index to Date
            if "index" in recent_fins.columns:
                recent_fins.rename(columns={"index": "Date"}, inplace=True)
                # Apply string formatting if it is datetime
                recent_fins["Date"] = recent_fins["Date"].astype(str)
                
            # Convert to dict and clean NaNs
            raw_list = recent_fins.to_dict("records")
            financials_list = [{k: clean_nan(v) for k, v in row.items()} for row in raw_list]

        # 2. Institutional Holders
        try:
            holders_df = ticker.institutional_holders
        except Exception:
            holders_df = pd.DataFrame()
            
        holders_list = []
        if holders_df is not None and not holders_df.empty:
            holders_df = holders_df.head(10) # Top 10
            # Clean dataframe types
            if "Date Reported" in holders_df.columns:
                holders_df["Date Reported"] = holders_df["Date Reported"].astype(str)
                
            holders_list = [{k: clean_nan(v) for k, v in row.items()} for row in holders_df.to_dict("records")]
            
        data = {
            "symbol": symbol,
            "financials": financials_list,
            "institutional_holders": holders_list
        }
        
        return {
            "ok": True,
            "data": data
        }

    except Exception as e:
        import traceback
        return {"ok": False, "error": f"Exception in worker: {str(e)}\n{traceback.format_exc()}"}
