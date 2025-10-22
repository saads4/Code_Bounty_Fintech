# news_sentiment.py
import feedparser
import requests
from textblob import TextBlob

def fetch_news_sentiment(company_name):
    """
    Fetch recent news headlines for a company and return average sentiment polarity (-1 to 1)
    """
    rss_url = f"https://news.google.com/rss/search?q={company_name}+stock+price"
    headers = {"User-Agent": "Mozilla/5.0"}  # prevent blocking
    try:
        resp = requests.get(rss_url, headers=headers, timeout=5)
        feed = feedparser.parse(resp.text)
    except Exception as e:
        print(f"[Error fetching news for {company_name}]: {e}")
        return 0

    if not feed.entries:
        print(f"[No news found for {company_name}]")
        return 0  # neutral if no news found

    sentiments = []
    for entry in feed.entries[:5]:  # analyze top 5 headlines
        analysis = TextBlob(entry.title)
        sentiments.append(analysis.sentiment.polarity)

    avg_sentiment = sum(sentiments) / len(sentiments)
    print(f"[Sentiment] {company_name}: {round(avg_sentiment, 3)}")  # log result
    return avg_sentiment
