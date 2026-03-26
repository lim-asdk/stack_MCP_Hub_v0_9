# analyst_company_news

## Description
Fetches company news from recent periods (up to 30 days) using the `analyst` API. Good for sentiment analysis and understanding short term momentum.

## Inputs
- `symbol` (string): The ticker symbol (e.g. TSLA, AAPL)

## Outputs
- `news`: Array of news objects containing the headline, summary, related image, source, and url.

## Notes
- Requires a free or paid analyst API Key loaded via `config_grace_apis.json`.

