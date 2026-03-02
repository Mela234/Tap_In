"""
Email scheduler for sending bi-weekly digest emails to subscribers
Sends emails every 2 weeks on Saturday/Sunday
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.raw_data import RawData
from app.services.email_service import get_email_service


scheduler = BackgroundScheduler()


def get_weekly_trends_data(db: Session):
    """Get this week's trending data from the database"""
    from app.api.routes.trends import format_raw_data_as_trend
    from datetime import timedelta
    
    # Get data from the last 7 days
    raw_data = db.query(RawData).order_by(
        RawData.collected_at.desc()
    ).limit(50).all()
    
    if not raw_data:
        return {
            "week_start": datetime.utcnow().strftime("%Y-%m-%d"),
            "week_end": datetime.utcnow().strftime("%Y-%m-%d"),
            "trends": []
        }
    
    # Convert raw data to trend format
    trends = []
    trend_id = 1
    
    for item in raw_data[:20]:  # Return top 20
        trend = format_raw_data_as_trend(item, trend_id)
        if trend:
            trends.append(trend)
            trend_id += 1
    
    return {
        "week_start": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "week_end": datetime.utcnow().strftime("%Y-%m-%d"),
        "trends": trends
    }


scheduler = BackgroundScheduler()


def send_weekly_digest_emails():
    """Send bi-weekly digest emails to all subscribed users"""
    db = SessionLocal()
    try:
        print(f"\n📧 Starting weekly digest email send at {datetime.utcnow().isoformat()}")
        
        # Get all users subscribed to email digest
        email_subscribers = db.query(User).filter(
            User.is_email_subscriber == True,
            User.is_active == True
        ).all()
        
        if not email_subscribers:
            print("ℹ️  No email subscribers found")
            return
        
        print(f"📨 Found {len(email_subscribers)} email subscribers")
        
        # Get this week's trends
        trends_data = get_weekly_trends_data(db)
        trends = trends_data.get("trends", [])
        
        if not trends:
            print("⚠️  No trends data available for this week")
            return
        
        # Send emails
        email_service = get_email_service()
        recipient_emails = [user.email for user in email_subscribers]
        
        # Generate email content
        html_content = email_service.generate_weekly_digest_email(trends, None)
        
        # Send bulk emails
        results = email_service.send_bulk_email(
            recipient_emails,
            "📊 Your TAPIN Weekly Trends Digest",
            html_content
        )
        
        # Update last_email_sent for successful sends
        sent_emails = results["sent"]
        if sent_emails:
            db.query(User).filter(User.email.in_(sent_emails)).update(
                {User.last_email_sent: datetime.utcnow()},
                synchronize_session=False
            )
            db.commit()
            print(f"✅ Successfully sent emails to {len(sent_emails)} subscribers")
        
        if results["failed"]:
            print(f"❌ Failed to send emails to {len(results['failed'])} subscribers: {results['failed']}")
        
    except Exception as e:
        print(f"❌ Error in send_weekly_digest_emails: {str(e)}")
        db.rollback()
    finally:
        db.close()


def start_email_scheduler():
    """Start the background scheduler for email tasks"""
    try:
        # Schedule to run every 2 weeks on Saturday at 9 AM UTC
        # Using cron expression: 0 9 * * 5 (Friday at 9 AM to account for timezones, sends Saturday morning)
        scheduler.add_job(
            send_weekly_digest_emails,
            CronTrigger(hour=9, minute=0, day_of_week='fri'),
            id='weekly_digest_email',
            name='Send weekly digest emails',
            replace_existing=True,
            misfire_grace_time=60
        )
        
        print("✅ Email scheduler started successfully")
        print("📅 Email scheduler configured to run every Friday at 9:00 AM UTC")
        
        if not scheduler.running:
            scheduler.start()
    except Exception as e:
        print(f"❌ Error starting email scheduler: {str(e)}")


def stop_email_scheduler():
    """Stop the background scheduler"""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            print("✅ Email scheduler stopped")
    except Exception as e:
        print(f"⚠️  Error stopping scheduler: {str(e)}")


# For testing purposes
def test_send_digest_email(recipient_email: str):
    """Test function to send a digest email immediately"""
    db = SessionLocal()
    try:
        print(f"🧪 Testing email send to {recipient_email}")
        
        # Get trends
        trends_data = get_weekly_trends_data(db)
        trends = trends_data.get("trends", [])
        
        # Send email
        email_service = get_email_service()
        html_content = email_service.generate_weekly_digest_email(trends, recipient_email)
        success = email_service.send_email(
            recipient_email,
            "🧪 Test: TAPIN Weekly Trends Digest",
            html_content
        )
        
        if success:
            print(f"✅ Test email sent successfully to {recipient_email}")
        else:
            print(f"❌ Test email failed for {recipient_email}")
        
        return success
    finally:
        db.close()
