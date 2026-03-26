# yahoo_fin_statements

## Description
Fetches core financial statements (recent 4 years/quarters of revenue, operating income, net income) and major institutional holders (Vanguard, BlackRock, etc.) using `yfinance`. 

## Inputs
- `symbol` (string): The ticker symbol (e.g. AAPL)

## Outputs
- `financials`: Array containing recent financial key figures like Total Revenue, Basic EPS, Net Income, etc.
- `institutional_holders`: Array of top institutional holding entities.

## Notes
- Extracts data from `yfinance.Ticker.financials` and `yfinance.Ticker.institutional_holders`.
