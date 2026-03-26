import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

def worker_main(inbox_payload: dict) -> dict:
    try:
        # Load Config
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "..", "..", "..", "..", "config", "config_grace_apis.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                apis = json.load(f)
            news_key = apis.get("news", {}).get("api_key")
        except Exception:
            news_key = None

        if not news_key:
            return {"ok": False, "error": "news key not found in config"}

        params = inbox_payload.get("message", {}).get("params", {})
        query = params.get("query")
        
        if not query:
            return {"ok": False, "error": "Missing query parameter"}

        # Get news for the last 7 days (news free tier limitation)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=7)
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.org/v2/everything?q={encoded_query}&from={from_date.strftime('%Y-%m-%d')}&to={to_date.strftime('%Y-%m-%d')}&sortBy=relevancy&apiKey={news_key}&language=en"
        
        # Adding User-Agent as news requires it
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        articles = data.get("articles", [])
        
        return {
            "ok": True,
            "data": {
                "query": query,
                "articles": articles[:20] # Return top 20
            }
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

