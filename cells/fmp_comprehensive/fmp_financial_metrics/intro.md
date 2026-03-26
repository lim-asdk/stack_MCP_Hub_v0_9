# fmp_financial_metrics

## Description
Fetches profile and basic financial metrics from Financial Modeling Prep (FMP) to provide cross-checking capabilities against Yahoo Finance.

## Inputs
- `symbol` (string): The ticker symbol (e.g. AAPL)

## Outputs
- `metrics`: Array including detailed API response with marketCap, EPS, PE, etc.

## Notes
- Requires FMP API Key configured in `config_grace_apis.json`. This queries `/api/v3/profile/` to avoid free-tier limitations.
