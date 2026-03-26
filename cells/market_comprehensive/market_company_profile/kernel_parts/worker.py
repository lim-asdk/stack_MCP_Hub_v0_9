import yfinance as yf

def worker_main(inbox_payload: dict) -> dict:
    try:
        # 1. Parse Input
        params = inbox_payload.get("message", {}).get("params", {})
        symbol = params.get("symbol")
        
        if not symbol:
            return {"ok": False, "error": "Missing required field: symbol"}
            
        # 2. Fetch data via yfinance
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info or len(info) == 0:
            return {"ok": False, "error": f"No info found for symbol {symbol}"}

        # 3. Build Outbox Data
        company_profile = {
            "symbol": symbol,
            "company_name": info.get("shortName", info.get("longName", "N/A")),
            "price": info.get("currentPrice", info.get("regularMarketPrice")),
            "prev_close": info.get("regularMarketPreviousClose"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "ceo": info.get("companyOfficers", [{"name": "N/A"}])[0].get("name", "N/A") if info.get("companyOfficers") else "N/A",
            "website": info.get("website", "N/A"),
            "dividend_yield": info.get("dividendYield", 0),
            "market_cap": info.get("marketCap", 0),
            "summary": info.get("longBusinessSummary", "N/A"),
            "forward_pe": info.get("forwardPE", None),
            "price_to_book": info.get("priceToBook", None),
            "roe": info.get("returnOnEquity", None),
            "peg_ratio": info.get("pegRatio", None),
        }
        
        return {
            "ok": True,
            "data": company_profile
        }

    except Exception as e:
        return {"ok": False, "error": f"Exception in worker: {str(e)}"}

