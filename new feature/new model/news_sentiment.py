# news_sentiment.py
import feedparser
from textblob import TextBlob

def fetch_news_sentiment(company_name):
    """
    Fetch recent news headlines for a company and return average sentiment polarity (-1 to 1)
    """
    rss_url = f"https://news.google.com/rss/search?q={company_name}+stock+price"
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        return 0  # neutral if no news found

    sentiments = []
    for entry in feed.entries[:5]:  # analyze top 5 headlines
        analysis = TextBlob(entry.title)
        sentiments.append(analysis.sentiment.polarity)

    avg_sentiment = sum(sentiments) / len(sentiments)
    return avg_sentiment
