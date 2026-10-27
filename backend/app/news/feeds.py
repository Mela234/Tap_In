"""RSS feeds for each side of the hexagon.

Each feed is (outlet name, url). Several outlets per topic lets the ranker see
which stories everyone is covering. Add or remove feeds here; nothing else needs
to change.
"""

TOPICS = ["tech", "entertainment", "culture", "world", "sports", "money"]

TOPIC_LABELS = {
    "tech": "Tech",
    "entertainment": "Entertainment",
    "culture": "Culture",
    "world": "World",
    "sports": "Sports",
    "money": "Money",
}

FEEDS = {
    "tech": [
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("BBC", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ],
    "entertainment": [
        ("Variety", "https://variety.com/feed/"),
        ("The Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
        ("Rolling Stone", "https://www.rollingstone.com/feed/"),
        ("BBC", "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"),
    ],
    "culture": [
        # Reddit rate-limits aggressively; the pipeline simply skips it when it does.
        ("r/OutOfTheLoop", "https://www.reddit.com/r/OutOfTheLoop/top/.rss?t=day"),
        ("Know Your Meme", "https://knowyourmeme.com/newsfeed.rss"),
        ("BuzzFeed", "https://www.buzzfeed.com/index.xml"),
        ("The Guardian", "https://www.theguardian.com/culture/rss"),
    ],
    "world": [
        ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ("NPR", "https://feeds.npr.org/1004/rss.xml"),
        ("The Guardian", "https://www.theguardian.com/world/rss"),
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ],
    "sports": [
        ("ESPN", "https://www.espn.com/espn/rss/news"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
        ("The Guardian", "https://www.theguardian.com/sport/rss"),
    ],
    "money": [
        ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
        ("BBC", "https://feeds.bbci.co.uk/news/business/rss.xml"),
        ("The Guardian", "https://www.theguardian.com/business/rss"),
        ("NPR", "https://feeds.npr.org/1006/rss.xml"),
    ],
}
