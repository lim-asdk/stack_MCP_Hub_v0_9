import os
import sys
import json
from datetime import datetime, timezone
import yfinance as yf

def get_mock_data(sym):
    """API ?¤íŒ¨ ??UI ê¹¨ì§ ë°©ì?ë¥??„í•œ ?”ë? ?°ì´??""
    return {
        "symbol": sym,
        "shortName": f"{sym} (Fallback Data)",
        "regularMarketPrice": 150.0 + (hash(sym) % 100),
        "regularMarketChangePercent": 1.25,
        "marketCap": 2500000000000,
        "trailingPE": 25.4,
        "forwardPE": 22.1,
        "fiftyTwoWeekHigh": 200.0,
        "fiftyTwoWeekLow": 120.0,
        "averageVolume": 50000000,
        "sector": "Information Technology",
        "industry": "Consumer Electronics",
        "regularMarketTime": int(datetime.now().timestamp())
    }

def worker_main(inbox_payload: dict) -> dict:
    try:
        # 1. Parse Input
        params = inbox_payload.get("message", {}).get("params", {})
        symbols = params.get("symbols")
        include_raw = params.get("include_raw", False)
        
        if not symbols:
            return {"ok": False, "error": "Missing required field: symbols"}
            
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        
        normalized = []
        raw_data = {}
        
        for sym in sym_list:
            try:
                # Reverting to default ticker call (without session) to avoid 429
                ticker = yf.Ticker(sym)
                info = ticker.info
                
                # Check for 429 or empty data
                if not info or len(info) < 10:
                    print(f"Yahoo API blocked or empty for {sym}. Using mock fallback.")
                    info = get_mock_data(sym)

                raw_data[sym] = info
                
                # yfinance returns timestamp for regularMarketTime as an int (Unix timestamp) or None
                reg_time = info.get("regularMarketTime")
                iso_time = None
                if reg_time:
                    try:
                        iso_time = datetime.fromtimestamp(reg_time, tz=timezone.utc).isoformat()
                    except:
                        iso_time = datetime.now(timezone.utc).isoformat()
                
                mapped = {
                    "symbol": sym,
                    "shortName": info.get("shortName") or info.get("longName") or sym,
                    "regularMarketPrice": info.get("currentPrice") or info.get("regularMarketPrice") or 0.0,
                    "timestamp_iso": iso_time,
                    "regularMarketChangePercent": info.get("regularMarketChangePercent") or 0.0,
                    "marketCap": info.get("marketCap") or 0,
                    "trailingPE": info.get("trailingPE") or 0.0,
                    "forwardPE": info.get("forwardPE") or 0.0,
                    "dividendYield": info.get("dividendYield") or 0.0,
                    "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh") or 0.0,
                    "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow") or 0.0,
                    "averageVolume": info.get("averageVolume") or 0,
                    "currency": info.get("currency") or "USD",
                    "exchange": info.get("exchange") or "UNKNOWN",
                    "sector": info.get("sector") or "N/A",
                    "industry": info.get("industry") or "N/A"
                }
                
                # ?ë³¸ info ?„ì²´ë¥?ë³‘í•©?˜ì—¬ ëª¨ë“  ?„ë“œê°€ ?¸ì¶œ?˜ë„ë¡?ë³€ê²?(?? ??–´?°ì? ?ŠìŒ)
                full_data = info.copy()
                full_data.update(mapped)
                
                normalized.append(full_data)
            except Exception as e:
                print(f"Worker deep error for {sym}: {e}")
                normalized.append(get_mock_data(sym))
            
        # 5. Build Outbox Result
        outbox_data = {
            "normalized": normalized,
            "request_meta": {
                "symbols": symbols,
                "queried_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        if include_raw:
            outbox_data["raw"] = raw_data
            
        return {
            "ok": True,
            "data": outbox_data
        }

    except Exception as e:
        return {"ok": False, "error": f"Exception in worker: {str(e)}"}

