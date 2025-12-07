import feedparser

class NewsFetcher:
    """
    A class to fetch news using Google News RSS.
    """

    def __init__(self, query: str, max_headlines: int = 5):
        """
        Initialize news fetcher with search query.
        """
        self.query = query
        self.max_headlines = max_headlines
        self.base_url = "https://news.google.com/rss/search?q={query}+stock"

    def _build_url(self) -> str:
        """Construct the RSS feed URL."""
        return self.base_url.format(query=self.query)

    def fetch(self) -> list:
        """
        Fetch latest headlines and return them as a list of dictionaries.
        """
        try:
            url = self._build_url()
            feed = feedparser.parse(url)

            headlines = []
            for entry in feed.entries[:self.max_headlines]:
                headlines.append({
                    "title": entry.title,
                    "link": entry.link
                })

            return headlines

        except Exception:
            return []
