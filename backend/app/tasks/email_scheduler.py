"""
Email scheduler for sending weekly digest emails to subscribers
Sends emails every week on Friday
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.raw_data import RawData
from app.services.email_service import get_email_service
from firebase_admin import firestore\

scheduler = BackgroundScheduler()


def get_weekly_trends_data(db: Session):
    """Get this week's trending data from the database"""
    from app.api.routes.trends import format_raw_data_as_trend
    
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


def get_email_subscribers():
    """Get all users who are subscribed to emails from Firestore"""
    try:
        db = firestore.client()
        
        # Query Firestore for subscribed users
        users_ref = db.collection('users')
        
        # Get users where isSubscribed = true
        subscribers = users_ref.where('isSubscribed', '==', True).stream()
        
        # Filter for users who want email notifications (default True if not set)
        email_list = []
        for user_doc in subscribers:
            user_data = user_doc.to_dict()
            # Check if email_notifications is enabled (default to True if not set)
            if user_data.get('email_notifications', True):
                email_list.append(user_data.get('email'))
        
        return email_list
    except Exception as e:
        print(f"❌ Error fetching email subscribers from Firestore: {e}")
        return []


def send_weekly_digest_emails():
    """Send weekly digest emails to all subscribed users"""
    sql_db = SessionLocal()
    try:
        print(f"\n📧 Starting weekly digest email send at {datetime.utcnow().isoformat()}")
        
        # Get email subscribers from Firestore
        recipient_emails = get_email_subscribers()
        
        if not recipient_emails:
            print("ℹ️  No email subscribers found")
            return
        
        print(f"📨 Found {len(recipient_emails)} email subscribers")
        
        # Get this week's trends from SQL database
        trends_data = get_weekly_trends_data(sql_db)
        trends = trends_data.get("trends", [])
        
        if not trends:
            print("⚠️  No trends data available for this week")
            return
        
        # Send emails
        email_service = get_email_service()
        
        # Generate email content
        html_content = email_service.generate_weekly_digest_email(trends, None)
        
        # Send bulk emails
        results = email_service.send_bulk_email(
            recipient_emails,
            "📊 Your TAPIN Weekly Trends Digest",
            html_content
        )
        
        # Update last_email_sent in Firestore for successful sends
        if results["sent"]:
            firestore_db = firestore.client()
            for email in results["sent"]:
                # Find user by email and update last_email_sent
                users_ref = firestore_db.collection('users').where('email', '==', email).stream()
                for user_doc in users_ref:
                    firestore_db.collection('users').document(user_doc.id).update({
                        'last_email_sent': datetime.utcnow()
                    })
            
            print(f"✅ Successfully sent emails to {len(results['sent'])} subscribers")
        
        if results["failed"]:
            print(f"❌ Failed to send emails to {len(results['failed'])} subscribers: {results['failed']}")
        
    except Exception as e:
        print(f"❌ Error in send_weekly_digest_emails: {str(e)}")
    finally:
        sql_db.close()


def start_email_scheduler():
    """Start the background scheduler for email tasks"""
    try:
        # Schedule to run every Friday at 9 AM UTC
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
    sql_db = SessionLocal()
    try:
        print(f"🧪 Testing email send to {recipient_email}")
        
        # Get trends
        trends_data = get_weekly_trends_data(sql_db)
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
        sql_db.close()