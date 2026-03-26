import os
import sys
import json
from datetime import datetime, timezone
import yfinance as yf

def worker_main(inbox_payload: dict) -> dict:
    try:
        # 1. Parse Input
        params = inbox_payload.get("message", {}).get("params", {})
        symbols = params.get("symbols")
        
        if not symbols:
            return {"ok": False, "error": "Missing required field: symbols"}
            
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        
        normalized = []
        
        for sym in sym_list:
            try:
                ticker = yf.Ticker(sym)
                
                # Fetch various sentiment data if available
                # Fallback to empty structures if yfinance doesn't return them
                maj_holders = ticker.major_holders
                inst_holders = ticker.institutional_holders
                insider_trans = ticker.insider_transactions
                mutual_fund = ticker.mutualfund_holders
                
                # Convert Pandas DataFrames to dicts/lists safely and handle Timestamps
                def df_to_list(df):
                    if df is None or df.empty:
                        return []
                    # to_json automatically handles NaNs and Timestamps to ISO 8601
                    return json.loads(df.to_json(orient='records', date_format='iso'))
                
                def df_to_dict(df):
                    if df is None or df.empty:
                        return {}
                    if df.shape[1] == 2:
                        mapping = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
                        # Ensure values are JSON serializable
                        for k, v in mapping.items():
                            import pandas as pd
                            if pd.isna(v):
                                mapping[k] = None
                            elif hasattr(v, 'isoformat'):
                                mapping[k] = v.isoformat()
                        return mapping
                    return json.loads(df.to_json(orient='records', date_format='iso'))

                mapped = {
                    "symbol": sym,
                    "major_holders": df_to_dict(maj_holders),
                    "institutional_holders": df_to_list(inst_holders),
                    "mutualfund_holders": df_to_list(mutual_fund),
                    "insider_transactions": df_to_list(insider_trans)
                }
                normalized.append(mapped)
                
            except Exception as e:
                normalized.append({"symbol": sym, "error": str(e)})
            
        # 5. Build Outbox Result
        outbox_data = {
            "normalized": normalized,
            "request_meta": {
                "symbols": symbols,
                "queried_at": datetime.now(timezone.utc).isoformat()
            }
        }
            
        return {
            "ok": True,
            "data": outbox_data
        }

    except Exception as e:
        return {"ok": False, "error": f"Exception in worker: {str(e)}"}

