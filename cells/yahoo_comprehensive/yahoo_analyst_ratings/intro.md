# yahoo_analyst_ratings

## Description
Fetches Wall Street analyst ratings, consensus recommendation, target prices, and recent upgrade/downgrade history using `yfinance`. 

## Inputs
- `symbol` (string): The ticker symbol (e.g. AAPL)

## Outputs
- `consensus`: Object containing the mean recommendation string, target mean price, low/high target, and number of analyst opinions.
- `recent_recommendations`: Recent analyst recommendation counts over time.
- `recent_upgrades_downgrades`: Array of the latest 10 upgrade or downgrade actions by analyst firms with the Action, Firm, ToGrade, and FromGrade.

## Notes
- Relies on `yfinance` to fetch recommendations and history.
