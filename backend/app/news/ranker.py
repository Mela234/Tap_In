import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.news.collector import Article

STOPWORDS = set(
    """
    a an the and or but of to in on at for with from by as is are was were be been
    this that these those it its into over after before about than then will would
    can could should may might has have had not no new says say said how why what
    who when where your you their they them his her our out up off just more most
    video watch live update updates latest week day year amid
    """.split()
)


def _tokens(title: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", title.lower().replace("'s", ""))
    tokens = set()
    for w in words:
        if len(w) < 3 or w in STOPWORDS:
            continue
        # Crude plural folding so "tariffs" matches "tariff".
        tokens.add(w[:-1] if w.endswith("s") and len(w) > 4 else w)
    return tokens


def _same_story(a: set[str], b: set[str]) -> bool:
    shared = len(a & b)
    if shared >= 3:
        return True
    return shared >= 2 and shared / max(1, min(len(a), len(b))) >= 0.5


@dataclass
class StoryCluster:
    topic: str
    articles: list[Article] = field(default_factory=list)
    tokens: set[str] = field(default_factory=set)

    @property
    def sources(self) -> set[str]:
        return {a.source for a in self.articles}

    @property
    def coverage(self) -> int:
        return len(self.sources)

    @property
    def newest(self) -> datetime:
        dates = [a.published for a in self.articles if a.published]
        return max(dates) if dates else datetime.min.replace(tzinfo=timezone.utc)

    @property
    def score(self) -> float:
        fresh = datetime.now(timezone.utc) - self.newest < timedelta(hours=12)
        return self.coverage * 3 + (1 if fresh else 0) + min(len(self.articles), 5) * 0.2


def cluster_articles(articles: list[Article]) -> dict[str, list[StoryCluster]]:
    """Group articles about the same story, per topic, ranked by how widely they're covered."""
    by_topic: dict[str, list[StoryCluster]] = {}

    for article in articles:
        tokens = _tokens(article.title)
        clusters = by_topic.setdefault(article.topic, [])
        match = next((c for c in clusters if _same_story(tokens, c.tokens)), None)
        if match:
            # Keep matching against the first headline only, so clusters don't snowball.
            match.articles.append(article)
        else:
            clusters.append(StoryCluster(topic=article.topic, articles=[article], tokens=tokens))

    for clusters in by_topic.values():
        clusters.sort(key=lambda c: (c.score, c.newest), reverse=True)

    return by_topic
