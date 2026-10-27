import threading
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import SessionLocal
from app.models.highlight import Highlight
from app.tasks.news_pipeline import run_news_pipeline

news_scheduler = BackgroundScheduler()


def _has_todays_edition() -> bool:
    db = SessionLocal()
    try:
        return db.query(Highlight.id).filter(Highlight.edition == date.today()).first() is not None
    except Exception:
        return False  # table doesn't exist yet
    finally:
        db.close()


def start_news_scheduler():
    """Build a fresh edition every morning, and right away if today's is missing."""
    news_scheduler.add_job(
        run_news_pipeline,
        CronTrigger(hour=6, minute=0, timezone="UTC"),
        id="daily_news_edition",
        name="Build the daily news edition",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    if not news_scheduler.running:
        news_scheduler.start()
    print("📅 News pipeline scheduled daily at 6:00 AM UTC")

    if not _has_todays_edition():
        threading.Thread(target=run_news_pipeline, daemon=True).start()
