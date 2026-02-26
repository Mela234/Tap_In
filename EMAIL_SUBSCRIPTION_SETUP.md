# Email Subscription Feature Setup Guide

## Overview
Your TAPIN application now includes an automated email subscription feature that sends curated weekly trends digest emails to subscribers every 2 weeks on Saturday/Sunday (configured for Friday 9 AM UTC).

## Features Implemented

### Backend Features
✅ **Email Service** (`backend/app/services/email_service.py`)
- SMTP-based email sending with HTML templates
- Beautiful, mobile-friendly email templates
- Bulk email sending capabilities
- Singleton pattern for efficient service management

✅ **Email Scheduler** (`backend/app/tasks/email_scheduler.py`)
- APScheduler-based background task runner
- Bi-weekly email scheduling (Friday 9 AM UTC)
- Automatic trend data fetching and email generation
- Email sent tracking with `last_email_sent` timestamps
- Test email functionality for development

✅ **API Endpoints** (`backend/app/api/routes/trends.py`)
- `POST /api/email/subscribe` - Subscribe/unsubscribe from email digest
- `GET /api/email/subscription-status/{email}` - Check subscription status
- `POST /api/email/test-send/{email}` - Send test email (development)

✅ **Database Updates** (`backend/app/models/user.py`)
- `is_email_subscriber` - Boolean flag for email subscription status
- `last_email_sent` - DateTime tracking last email sent to user

### Frontend Features
✅ **Email Subscription Modal** (`frontend/src/Subscribe.jsx`)
- Beautiful modal for email subscription signup
- Form validation and error handling
- Success confirmation message
- Integration with backend API

✅ **CTA Buttons**
- "Free Email Digest" button on paywall (non-subscribers)
- "Enable Email Digest" button on subscription page
- Alternative call-to-action for email-only subscribers

✅ **Styling** (`frontend/src/Subscribe.css`)
- Responsive email subscription modal
- Consistent with existing design language
- Smooth animations and transitions
- Mobile-optimized layout

## Setup Instructions

### 1. Backend Environment Variables

Create or update your `.env` file in the `/backend` directory:

```bash
# SMTP Email Configuration (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password  # Use app-specific password for Gmail
SENDER_NAME=TAPIN

# Database and other existing variables...
DATABASE_URL=postgresql://user:password@localhost/tapin
```

#### Gmail Setup (Recommended)
1. Enable 2-Factor Authentication on your Google Account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the generated password as `SENDER_PASSWORD`

#### Alternative Email Providers
- **SendGrid**: Use SMTP gateway sendgrid.net
- **Mailgun**: Use SMTP gateway smtp.mailgun.org
- **AWS SES**: Use email-smtp.{region}.amazonaws.com
- **Brevo (Sendinblue)**: Use smtp-relay.brevo.com

### 2. Database Migration

Run migrations to add the new columns to the users table:

```bash
# In the backend directory
alembic revision --autogenerate -m "Add email subscription fields"
alembic upgrade head
```

Or execute directly with psql:

```sql
ALTER TABLE users ADD COLUMN is_email_subscriber BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN last_email_sent TIMESTAMP NULL;
```

### 3. Install Dependencies

The required dependencies have been added to `requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
```

Key packages:
- `pydantic==2.6.0` - Data validation
- `jinja2==3.1.2` - Email template rendering
- `apscheduler==3.10.4` - Background task scheduling (already installed)

### 4. Run the Application

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The email scheduler will start automatically on application startup. You should see:
```
✅ Email scheduler started successfully
📅 Email scheduler configured to run every Friday at 9:00 AM UTC
```

## API Endpoints

### Subscribe to Email Digest
```bash
POST /api/email/subscribe
Content-Type: application/json

{
  "email": "user@example.com",
  "subscribe": true
}

# Response
{
  "success": true,
  "message": "Successfully subscribed from email digest",
  "email": "user@example.com",
  "is_email_subscriber": true
}
```

### Get Subscription Status
```bash
GET /api/email/subscription-status/user@example.com

# Response
{
  "email": "user@example.com",
  "is_email_subscriber": true,
  "last_email_sent": "2026-02-20T09:00:00"
}
```

### Test Send Email (Development)
```bash
POST /api/email/test-send/user@example.com

# Response
{
  "success": true,
  "message": "Test email sent successfully to user@example.com"
}
```

## Frontend Integration

The email subscription feature is already integrated into the Subscribe component:

1. **Non-Subscribers**: See "Free Email Digest" button on paywall
2. **Subscribers**: See "Enable Email Digest" option in subscription area
3. **Modal**: Beautiful form with email input and benefits list

The modal automatically:
- Validates email format
- Sends subscription request to backend
- Shows success/error messages
- Closes after successful subscription

## Email Template

The email digest includes:

- **Header**: "This Week's Trends" branding
- **Top 10 Trends**: Each with:
  - Title and relevance score (🔥)
  - Category badge
  - Description summary
  - "Why it matters" insight
  - Source attribution
- **CTA Button**: "View All Trends" link
- **Footer**: Unsubscribe link and copyright

## Customization

### Change Email Sending Schedule

Edit `backend/app/tasks/email_scheduler.py`, line 60:

```python
# Change from Friday 9 AM UTC to your preferred schedule
# Current: 0 9 * * fri (Friday 9 AM)
# Examples:
# Saturday 9 AM: 0 9 * * sat
# Every Saturday & Sunday: 0 9 * * 5,6
# Twice a month (1st & 15th): 0 9 1,15 * *

scheduler.add_job(
    send_weekly_digest_emails,
    CronTrigger(hour=9, minute=0, day_of_week='fri'),  # ← Modify this line
    ...
)
```

### Customize Email Template

Edit `backend/app/services/email_service.py`, method `generate_weekly_digest_email`:

```python
def generate_weekly_digest_email(self, trends: List[dict], recipient_email: str) -> str:
    # Modify HTML template here
    # Change colors, fonts, layout, etc.
```

### Change Trends Count in Email

Edit `backend/app/tasks/email_scheduler.py`:

```python
# Line 40: Change from [:10] to desired limit
html_content = email_service.generate_weekly_digest_email(trends[:10], None)
```

## Monitoring & Troubleshooting

### Check Email Scheduler Status
```bash
# View logs in console when server runs
# Should show:
# ✅ Email scheduler started successfully
# 📅 Email scheduler configured to run every Friday at 9:00 AM UTC
```

### Manual Test Email
```bash
# Use the test endpoint
curl -X POST "http://localhost:8000/api/email/test-send/test@example.com"
```

### Database Queries

Check subscription status:
```sql
SELECT email, is_email_subscriber, last_email_sent 
FROM users 
WHERE is_email_subscriber = true;
```

Check subscriber count:
```sql
SELECT COUNT(*) as subscriber_count 
FROM users 
WHERE is_email_subscriber = true AND is_active = true;
```

### Common Issues

**Issue**: Email not sending
- ✅ Check SMTP credentials in `.env`
- ✅ Verify firewall allows port 587 (or your SMTP port)
- ✅ Check email provider's app password settings
- ✅ Look at console logs for detailed error messages

**Issue**: Users can't subscribe
- ✅ Verify backend is running on localhost:8000
- ✅ Check CORS settings in `app/main.py`
- ✅ Check browser console for API errors

**Issue**: Scheduler not running
- ✅ Restart the backend server
- ✅ Check for errors during startup
- ✅ Verify APScheduler is installed: `pip list | grep apscheduler`

## Production Deployment

### Security Considerations

1. **Email Credentials**
   - Use environment variables (never hardcode)
   - Use app-specific passwords when available
   - Rotate credentials regularly

2. **SMTP**
   - Use TLS (port 587) or SSL (port 465)
   - Consider IP whitelisting with email provider
   - Use authenticated SMTP only

3. **Database**
   - Ensure user data is encrypted
   - Implement data retention policies
   - Regular backups

4. **Rate Limiting**
   - Implement rate limits on subscription endpoint
   - Monitor for abuse patterns

### Email Deliverability

1. **SPF/DKIM/DMARC**
   - Configure DNS records with your email provider
   - Improves email deliverability
   - Reduces spam folder placement

2. **Unsubscribe Link**
   - Currently in footer
   - Implement unsubscribe flow
   - Required by CAN-SPAM Act (US) and GDPR (EU)

3. **List Maintenance**
   - Monitor bounce rates
   - Remove hard bounces automatically
   - Re-engagement campaigns for inactive subscribers

## File Structure Reference

```
backend/
├── app/
│   ├── models/
│   │   └── user.py (UPDATED)
│   ├── services/
│   │   └── email_service.py (NEW)
│   ├── tasks/
│   │   └── email_scheduler.py (NEW)
│   ├── api/routes/
│   │   └── trends.py (UPDATED)
│   └── main.py (UPDATED)
└── requirements.txt (UPDATED)

frontend/
├── src/
│   ├── Subscribe.jsx (UPDATED)
│   └── Subscribe.css (UPDATED)
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Email scheduler initializes on startup
- [ ] Test email endpoint sends email successfully
- [ ] Frontend modal opens and displays correctly
- [ ] Email subscription form validates input
- [ ] Successful subscription shows confirmation
- [ ] Subscription status can be queried
- [ ] Database records are updated correctly
- [ ] Scheduler runs at configured time (check logs)
- [ ] Email template renders correctly in email client

## Support & Future Enhancements

### Possible Future Features
- Email preference center (frequency, topics, format)
- Rich text editor for admin email customization
- Email analytics (open rates, click rates)
- Automated double opt-in confirmation
- Segmentation based on interests/categories
- A/B testing for subject lines
- Delay scheduling (send at user's local time)
- Digest template variations

### Documentation
- Email template customization guide
- Deployment guide for specific platforms
- Email provider configuration guides
