"""Daily news pipeline: collect feeds -> rank stories -> summarize with Claude -> store the edition.

Run by hand with:  python -m app.tasks.news_pipeline
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from app.agents.summarizer import Summarizer
from app.core.database import Base, SessionLocal, engine
from app.models.highlight import Highlight
from app.news.collector import collect_articles
from app.news.feeds import TOPICS
from app.news.ranker import cluster_articles


def run_news_pipeline() -> dict:
    """Build today's edition, replacing any earlier run from the same day."""
    print("\n🗞️  Building today's Tap In edition...")
    Base.metadata.create_all(bind=engine, tables=[Highlight.__table__])

    articles = collect_articles()
    clusters = cluster_articles(articles)
    print(f"🧮 {len(articles)} articles grouped into {sum(len(c) for c in clusters.values())} stories")

    summarizer = Summarizer()
    with ThreadPoolExecutor(max_workers=len(TOPICS)) as pool:
        written = dict(
            zip(TOPICS, pool.map(lambda t: summarizer.write_topic(t, clusters.get(t, [])), TOPICS))
        )

    edition = date.today()
    db = SessionLocal()
    try:
        db.query(Highlight).filter(Highlight.edition == edition).delete()
        for topic, highlights in written.items():
            for rank, h in enumerate(highlights, 1):
                db.add(
                    Highlight(
                        edition=edition,
                        topic=topic,
                        rank=rank,
                        title=h.title,
                        gist=h.gist,
                        why_it_matters=h.why_it_matters,
                        sources=h.sources,
                        coverage=h.coverage,
                    )
                )
        db.commit()
    finally:
        db.close()

    counts = {topic: len(h) for topic, h in written.items()}
    print(f"✅ Edition {edition} saved: {counts}")
    return {"edition": edition.isoformat(), "highlights": counts}


if __name__ == "__main__":
    run_news_pipeline()
