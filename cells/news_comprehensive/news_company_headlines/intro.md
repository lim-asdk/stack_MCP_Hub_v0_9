# news_company_headlines

## Description
Queries global news headlines related to a specific company or query string. Useful for tracking massive events around a ticker.

## Inputs
- `query` (string): The search string describing the company (e.g., "Apple Inc" instead of just "AAPL" to get better natural language results).

## Outputs
- `articles`: Returns up to the 20 most relevant articles from the last 7 days.

## Notes
- Relies on news using the `everything` endpoint.
- Free tier only allows articles up to 30 days old; this tool fetches the last 7 days.

