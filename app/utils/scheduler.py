from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

scheduler = BackgroundScheduler()
_scheduler_started = False


def check_sla_breaches(app: Flask):
    """Check for SLA breaches and escalate overdue documents."""
    with app.app_context():
        from app.models import db, Document, Routing, TrackingEvent, Notification
        from app.utils.notifications import send_notification, notify_admins, notify_department_head
        
        now = datetime.utcnow()
        
        # Find documents that are notified but past SLA deadline
        overdue_routings = db.session.query(Routing).join(Document).filter(
            Document.status == 'notified',
            Routing.sla_deadline < now
        ).all()
        
        for routing in overdue_routings:
            doc = routing.document
            
            # Update status to escalated
            doc.status = 'escalated'
            
            # Create tracking event
            event = TrackingEvent(
                document_id=doc.document_id,
                event_type='ESCALATED',
                event_description=f'Document escalated: SLA deadline ({routing.sla_deadline.strftime("%Y-%m-%d %H:%M")}) breached.',
                performed_by=None
            )
            db.session.add(event)
            
            # Notify department head
            notify_department_head(
                routing.routed_to_department_id,
                doc.document_id,
                'escalation',
                f'ESCALATION: Document {doc.tracking_id} "{doc.subject_description}" has breached SLA deadline.'
            )
            
            # Notify admins
            notify_admins(
                doc.document_id,
                'escalation',
                f'ESCALATION: Document {doc.tracking_id} "{doc.subject_description}" has breached SLA deadline.'
            )
        
        # Also re-escalate already escalated documents every 24 hours
        escalated_routings = db.session.query(Routing).join(Document).filter(
            Document.status == 'escalated'
        ).all()
        
        for routing in escalated_routings:
            doc = routing.document
            # Check if last escalation event was more than 24 hours ago
            last_escalation = TrackingEvent.query.filter_by(
                document_id=doc.document_id,
                event_type='ESCALATED'
            ).order_by(TrackingEvent.performed_at.desc()).first()
            
            if last_escalation:
                hours_since = (now - last_escalation.performed_at).total_seconds() / 3600
                if hours_since >= 24:
                    # Re-escalate
                    event = TrackingEvent(
                        document_id=doc.document_id,
                        event_type='ESCALATED',
                        event_description=f'Document re-escalated: still unacknowledged after {int(hours_since)} hours.',
                        performed_by=None
                    )
                    db.session.add(event)
                    
                    # Send reminder notification
                    send_notification(
                        doc.document_id,
                        routing.routed_to_user_id,
                        'reminder',
                        f'REMINDER: Document {doc.tracking_id} is still awaiting your acknowledgement.'
                    )
                    notify_admins(
                        doc.document_id,
                        'reminder',
                        f'REMINDER: Document {doc.tracking_id} still unacknowledged by {routing.routed_user.full_name}.'
                    )
        
        db.session.commit()


def start_scheduler(app: Flask):
    """Start the background scheduler for SLA checks."""
    global _scheduler_started
    if _scheduler_started:
        return
    
    scheduler.add_job(
        func=check_sla_breaches,
        trigger='interval',
        hours=1,
        args=[app],
        id='sla_breach_check',
        name='Check SLA Breaches',
        replace_existing=True
    )
    
    try:
        scheduler.start()
        _scheduler_started = True
        app.logger.info('SLA breach scheduler started (runs every hour)')
    except Exception as e:
        app.logger.error(f'Failed to start scheduler: {e}')
