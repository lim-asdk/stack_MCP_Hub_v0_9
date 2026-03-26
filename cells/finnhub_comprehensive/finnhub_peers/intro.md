# finnhub_peers

## Description
Fetches a list of peer companies in the same industry/sector using the Finnhub API. 

## Inputs
- `symbol` (string): The ticker symbol to base the peer grouping off of.

## Outputs
- `peers`: Array of ticker strings representing competitors (e.g. ["MSFT", "GOOGL"]).

## Notes
- Needs Finnhub API Key configured in `config_grace_apis.json`.
