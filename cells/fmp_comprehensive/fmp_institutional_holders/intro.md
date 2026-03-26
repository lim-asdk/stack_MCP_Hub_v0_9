# fmp_institutional_holders

## Description
Fetches top institutional holders (e.g. Vanguard, Berkshire, Blackrock) for a given symbol using Financial Modeling Prep. Shows 'Smart Money' flow.

## Inputs
- `symbol` (string): The ticker symbol.

## Outputs
- `institutionalHolders`: Array containing the holder name, shares owned, and date reported.

## Notes
- Needs FMP API Key configured in `config_grace_apis.json`. Hits the `/api/v3/institutional-holder/` endpoint.
