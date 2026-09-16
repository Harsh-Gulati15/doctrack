from datetime import datetime
from flask import current_app
from flask_mail import Message
from app.models import db, Notification, User


def send_notification(document_id, user_id, notification_type, message):
    """Create portal notification and optionally send email."""
    # Portal notification
    notif = Notification(
        document_id=document_id,
        user_id=user_id,
        notification_type=notification_type,
        message=message
    )
    db.session.add(notif)
    db.session.commit()
    
    # Email notification
    try:
        user = db.session.get(User, user_id)
        if user and user.email:
            from app import mail
            email_msg = Message(
                subject=f'[DocTrack] {notification_type.replace("_", " ").title()}',
                recipients=[user.email],
                body=f"Hello {user.full_name},\n\n{message}\n\nPlease log in to DocTrack to take action.\n\n— DocTrack System"
            )
            mail.send(email_msg)
    except Exception as e:
        current_app.logger.warning(f'Email notification failed for user {user_id}: {e}')


def notify_admins(document_id, notification_type, message):
    """Send notification to all active admins and superadmins."""
    admins = User.query.filter(
        User.role.in_(['admin', 'superadmin']),
        User.is_active == True
    ).all()
    for admin in admins:
        send_notification(document_id, admin.user_id, notification_type, message)


def notify_department_head(department_id, document_id, notification_type, message):
    """Send notification to the head of a department."""
    from app.models import Department
    dept = db.session.get(Department, department_id)
    if dept and dept.head_user_id:
        send_notification(document_id, dept.head_user_id, notification_type, message)
