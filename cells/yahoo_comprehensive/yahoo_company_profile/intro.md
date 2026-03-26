# yahoo_company_profile

## Description
Fetches comprehensive company profile data, basic valuation metrics, and dividends using the `yfinance` library. This serves as the foundation for the PPT-style Ticker Report.

## Inputs
- `symbol` (string): The ticker symbol (e.g. AAPL, TSLA)

## Outputs
- `company_name`: Short or Long Name of the company
- `sector`: Sector classification
- `industry`: Industry classification
- `ceo`: Name of the CEO
- `dividend_yield`: Current dividend yield % (if available)
- `market_cap`: Market capitalization
- `summary`: Long business summary
- `forward_pe`, `price_to_book`, `roe`, `peg_ratio`: Basic valuation metrics

## Notes
- Relies on `yfinance.Ticker(symbol).info`
- No API keys required.
