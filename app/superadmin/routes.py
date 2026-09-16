import csv
import io
from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from datetime import datetime
from app.superadmin import superadmin_bp
from app.models import db, AuditLog, Document, User
from app.auth.routes import role_required

@superadmin_bp.route('/superadmin/audit-log', methods=['GET'])
@login_required
@role_required('superadmin')
def audit_log():
    page = request.args.get('page', 1, type=int)
    event_type = request.args.get('event_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search')
    
    query = AuditLog.query

    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if date_from:
        try:
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.logged_at >= date_from_dt)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(AuditLog.logged_at < date_to_dt.replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    if search:
        query = query.filter(AuditLog.details.ilike(f'%{search}%'))

    query = query.order_by(AuditLog.logged_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    logs = pagination.items

    distinct_event_types = [r[0] for r in db.session.query(AuditLog.event_type).distinct().all()]
    
    # Attach user and doc for templates if relations aren't present
    for log in logs:
        if not hasattr(log, 'doc'):
            log.doc = Document.query.get(log.document_id) if log.document_id else None
        if not hasattr(log, 'user'):
            log.user = User.query.get(log.user_id) if log.user_id else None

    return render_template('superadmin/audit_log.html',
                           logs=logs,
                           pagination=pagination,
                           distinct_event_types=distinct_event_types,
                           event_type=event_type,
                           date_from=date_from,
                           date_to=date_to,
                           search=search)


@superadmin_bp.route('/superadmin/audit-log/export-csv', methods=['GET'])
@login_required
@role_required('superadmin')
def export_csv():
    event_type = request.args.get('event_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search')
    
    query = AuditLog.query

    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if date_from:
        try:
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.logged_at >= date_from_dt)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(AuditLog.logged_at < date_to_dt.replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    if search:
        query = query.filter(AuditLog.details.ilike(f'%{search}%'))

    query = query.order_by(AuditLog.logged_at.desc())
    logs = query.all()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['Log ID', 'Event Type', 'Document Tracking ID', 'Username', 'IP Address', 'Details', 'Timestamp'])
    for log in logs:
        if not hasattr(log, 'doc'):
            log.doc = Document.query.get(log.document_id) if log.document_id else None
        if not hasattr(log, 'user'):
            log.user = User.query.get(log.user_id) if log.user_id else None
            
        writer.writerow([
            log.log_id,
            log.event_type,
            log.doc.tracking_id if log.doc else '',
            log.user.username if log.user else '',
            log.ip_address or '',
            log.details or '',
            log.logged_at.strftime('%Y-%m-%d %H:%M:%S') if log.logged_at else ''
        ])

    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=audit_log_{datetime.now().strftime("%Y-%m-%d")}.csv'}
    )


@superadmin_bp.route('/superadmin/purge-archived', methods=['POST'])
@login_required
@role_required('superadmin')
def purge_archived():
    archived_docs = Document.query.filter_by(status='archived').all()
    count = len(archived_docs)
    
    if count > 0:
        for doc in archived_docs:
            db.session.delete(doc)
            
        audit = AuditLog(
            event_type='PURGE_ARCHIVED',
            user_id=current_user.user_id,
            ip_address=request.remote_addr,
            details=f'Purged {count} archived documents.',
            logged_at=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'Successfully purged {count} archived document(s).', 'success')
    else:
        flash('No archived documents found to purge.', 'info')
        
    return redirect(url_for('superadmin.audit_log'))
