import yfinance as yf
import pandas as pd

def worker_main(inbox_payload: dict) -> dict:
    try:
        params = inbox_payload.get("message", {}).get("params", {})
        symbol = params.get("symbol")
        
        if not symbol:
            return {"ok": False, "error": "Missing required field: symbol"}
            
        ticker = yf.Ticker(symbol)
        
        # Insider transactions
        insider_df = ticker.insider_transactions
        insider_list = []
        if insider_df is not None and not insider_df.empty:
            # We want to reset index as sometimes the position/date is in the index
            # and format dates
            insider_df = insider_df.reset_index()
            # Try to convert datetime types to string if they exist
            if "Start Date" in insider_df.columns:
                insider_df["Start Date"] = insider_df["Start Date"].astype(str)
            if "Position" not in insider_df.columns:
                insider_df["Position"] = "Unknown"
                
            # Limit to recent 20
            insider_list = insider_df.head(20).to_dict("records")
            
        insider_data = {
            "symbol": symbol,
            "insider_transactions": insider_list
        }
        
        return {
            "ok": True,
            "data": insider_data
        }

    except Exception as e:
        return {"ok": False, "error": f"Exception in worker: {str(e)}"}

