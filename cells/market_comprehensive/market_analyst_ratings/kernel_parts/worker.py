import yfinance as yf
import pandas as pd
from datetime import datetime

def worker_main(inbox_payload: dict) -> dict:
    try:
        params = inbox_payload.get("message", {}).get("params", {})
        symbol = params.get("symbol")
        
        if not symbol:
            return {"ok": False, "error": "Missing required field: symbol"}
            
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # 1. Target Prices & Recommendation Consensus
        consensus = {
            "recommendationMean": info.get("recommendationMean", None),
            "recommendationKey": info.get("recommendationKey", "N/A"),
            "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions", 0),
            "targetHighPrice": info.get("targetHighPrice", None),
            "targetLowPrice": info.get("targetLowPrice", None),
            "targetMeanPrice": info.get("targetMeanPrice", None),
            "targetMedianPrice": info.get("targetMedianPrice", None)
        }

        # 2. Recommendations over time (yfinance recommendations)
        recs_df = ticker.recommendations
        recs_list = []
        if recs_df is not None and not recs_df.empty:
            if "period" in recs_df.columns:
                recs_list = recs_df.tail(4).to_dict("records")
            else:
                recs_list = recs_df.reset_index().tail(4).to_dict("records")

        # 3. Upgrades/Downgrades
        up_down_df = ticker.upgrades_downgrades
        up_down_list = []
        if up_down_df is not None and not up_down_df.empty:
            recent_up_down = up_down_df.reset_index().sort_values(by="GradeDate", ascending=False).head(10)
            # GradeDate is likely a timestamp, convert to string
            recent_up_down["GradeDate"] = recent_up_down["GradeDate"].dt.strftime('%Y-%m-%d')
            up_down_list = recent_up_down.to_dict("records")

        analyst_data = {
            "symbol": symbol,
            "consensus": consensus,
            "recent_recommendations": recs_list,
            "recent_upgrades_downgrades": up_down_list
        }
        
        return {
            "ok": True,
            "data": analyst_data
        }

    except Exception as e:
        return {"ok": False, "error": f"Exception in worker: {str(e)}"}

