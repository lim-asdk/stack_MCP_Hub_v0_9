# yahoo_insider_trades

## Description
Fetches recent insider transactions (officers, directors) using `yfinance`. 

## Inputs
- `symbol` (string): The ticker symbol (e.g. AAPL)

## Outputs
- `insider_transactions`: Array of the latest insider transactions including the Insider name, Position, Date, Shares, and Value.

## Notes
- Relies on `yfinance.Ticker.insider_transactions`
- Converts the DataFrame to a JSON array for outbox.
