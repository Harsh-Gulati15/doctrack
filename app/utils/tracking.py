from app.models import TrackingEvent


def get_tracking_timeline(document_id):
    """Get ordered list of tracking events for a document.
    
    Returns list of dicts with: event_type, description, performer, timestamp
    """
    events = TrackingEvent.query.filter_by(
        document_id=document_id
    ).order_by(TrackingEvent.performed_at.asc()).all()
    
    timeline = []
    for event in events:
        timeline.append({
            'event_type': event.event_type,
            'description': event.event_description,
            'performer': event.performer.full_name if event.performer else 'System',
            'timestamp': event.performed_at,
            'icon': _get_event_icon(event.event_type)
        })
    
    return timeline


def _get_event_icon(event_type):
    """Return Bootstrap icon class for event type."""
    icons = {
        'REGISTERED': 'bi-file-earmark-plus',
        'OCR_COMPLETED': 'bi-eye',
        'OCR_FAILED': 'bi-eye-slash',
        'CATEGORISED': 'bi-tags',
        'ROUTED': 'bi-arrow-right-circle',
        'NOTIFIED': 'bi-bell',
        'ACKNOWLEDGED': 'bi-check-circle',
        'ESCALATED': 'bi-exclamation-triangle',
        'ARCHIVED': 'bi-archive',
    }
    return icons.get(event_type, 'bi-circle')
