"""
NOTIFICATION PROCESSING ROUTES

Handles:
- Processing pending notifications
- Simulating email/webhook sending
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from ..database import get_db

router = APIRouter()


# ============================================
# PROCESS PENDING NOTIFICATIONS
# ============================================

@router.post("/process")
async def process_notifications(db: Session = Depends(get_db)):
    """
    Process all pending notifications.
    Simulates sending email/webhook and updates status to 'sent'.
    """

    # Fetch pending notifications
    notifications = db.execute(
        text("""
            SELECT notification_id,
                   user_id,
                   evaluation_id,
                   notification_type,
                   recipient,
                   subject,
                   message
            FROM notifications
            WHERE status = 'pending'
            ORDER BY created_at ASC
        """)
    ).fetchall()

    if not notifications:
        return {
            "message": "No pending notifications",
            "processed_count": 0
        }

    processed_count = 0

    for notification in notifications:
        print("=" * 60)
        print("📨 Sending Notification")
        print(f"Type: {notification.notification_type}")
        print(f"To: {notification.recipient}")
        print(f"Subject: {notification.subject}")
        print(f"Message: {notification.message}")
        print("=" * 60)

        # Update status to sent
        db.execute(
            text("""
                UPDATE notifications
                SET status = 'sent',
                    sent_at = NOW()
                WHERE notification_id = :notification_id
            """),
            {"notification_id": notification.notification_id}
        )

        processed_count += 1

    db.commit()

    return {
        "message": "Notifications processed successfully",
        "processed_count": processed_count
    }