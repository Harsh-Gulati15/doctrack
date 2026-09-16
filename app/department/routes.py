from flask import render_template, request, redirect, url_for, flash, send_from_directory, current_app, abort
from flask_login import login_required, current_user
from app.department import department_bp
from app.auth.routes import role_required
from app.models import db, Document, Routing, Acknowledgement, Notification, TrackingEvent, AuditLog, User
from datetime import datetime
import os

try:
    from app.utils.notifications import send_notification
except ImportError:
    # Fallback in case utils is not fully set up
    def send_notification(document_id, user_id, notification_type, message):
        pass

@department_bp.route('/dashboard')
@login_required
@role_required('dept_user')
def dashboard():
    base_query = db.session.query(Document).join(Routing).filter(Routing.routed_to_user_id == current_user.user_id)
    
    assigned_count = base_query.count()
    pending_count = base_query.filter(~Document.status.in_(['acknowledged', 'archived'])).count()
    overdue_count = base_query.filter(Document.status == 'escalated').count()
    acknowledged_count = base_query.filter(Document.status == 'acknowledged').count()
    
    recent_documents = base_query.order_by(Routing.routed_at.desc()).limit(10).all()
    
    return render_template('department/dashboard.html',
                           assigned_count=assigned_count,
                           pending_count=pending_count,
                           overdue_count=overdue_count,
                           acknowledged_count=acknowledged_count,
                           recent_documents=recent_documents)

@department_bp.route('/my-documents')
@login_required
@role_required('dept_user')
def my_documents():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    
    query = db.session.query(Document).join(Routing).filter(Routing.routed_to_user_id == current_user.user_id)
    
    if status_filter:
        query = query.filter(Document.status == status_filter)
        
    pagination = query.order_by(Routing.routed_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('department/my_documents.html', pagination=pagination, status_filter=status_filter)


@department_bp.route('/document/<int:document_id>')
@login_required
@role_required('dept_user')
def document_detail(document_id):
    document = Document.query.get_or_404(document_id)
    
    # Check if routed to current user
    routing = Routing.query.filter_by(document_id=document.document_id, routed_to_user_id=current_user.user_id).order_by(Routing.routed_at.desc()).first()
    if not routing:
        abort(403)
        
    return render_template('department/document_detail.html', document=document, routing=routing)

@department_bp.route('/acknowledge/<int:document_id>', methods=['POST'])
@login_required
@role_required('dept_user')
def acknowledge(document_id):
    document = Document.query.get_or_404(document_id)
    
    # Check routing
    routing = Routing.query.filter_by(document_id=document.document_id, routed_to_user_id=current_user.user_id).first()
    if not routing:
        abort(403)
        
    remarks = request.form.get('remarks', '')
    
    was_escalated = (document.status == 'escalated')
    
    ack = Acknowledgement(
        document_id=document.document_id,
        acknowledged_by=current_user.user_id,
        was_escalated=was_escalated,
        remarks=remarks
    )
    db.session.add(ack)
    
    document.status = 'acknowledged'
    
    event = TrackingEvent(
        document_id=document.document_id,
        event_type='ACKNOWLEDGED',
        event_description=f"Document acknowledged by {current_user.full_name or current_user.username}",
        performed_by=current_user.user_id
    )
    db.session.add(event)
    
    # Notifications
    receptionist_id = document.created_by
    if receptionist_id:
        send_notification(document.document_id, receptionist_id, 'acknowledgement_done', f"Document {document.tracking_id} acknowledged by {current_user.username}")
    
    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        send_notification(document.document_id, admin.user_id, 'acknowledgement_done', f"Document {document.tracking_id} acknowledged by {current_user.username}")
        
    # Email try/except
    try:
        # Emailing logic placeholder
        pass
    except Exception as e:
        current_app.logger.error(f"Error sending acknowledgement email: {str(e)}")
        
    log = AuditLog(
        event_type='ACKNOWLEDGE_DOCUMENT',
        document_id=document.document_id,
        user_id=current_user.user_id,
        ip_address=request.remote_addr,
        details=f"Document {document.tracking_id} acknowledged"
    )
    db.session.add(log)
    
    db.session.commit()
    
    flash('Document acknowledged successfully.', 'success')
    return redirect(url_for('department.document_detail', document_id=document.document_id))

@department_bp.route('/track', methods=['GET'])
@login_required
@role_required('dept_user')
def track():
    tracking_id = request.args.get('tracking_id')
    document = None
    if tracking_id:
        document = Document.query.filter_by(tracking_id=tracking_id).first()
        if document:
            routing = Routing.query.filter_by(document_id=document.document_id, routed_to_user_id=current_user.user_id).first()
            if not routing:
                document = None
                flash('Document not found or you do not have permission to track it.', 'danger')
        else:
            flash('Document not found.', 'danger')
            
    return render_template('department/track.html', document=document, tracking_id=tracking_id)

@department_bp.route('/serve-file/<int:document_id>')
@login_required
@role_required('dept_user')
def serve_file(document_id):
    document = Document.query.get_or_404(document_id)
    routing = Routing.query.filter_by(document_id=document.document_id, routed_to_user_id=current_user.user_id).first()
    if not routing:
        abort(403)
        
    if not document.file_path:
        abort(404)
        
    from app.utils.storage import serve_file as storage_serve
    return storage_serve(document.file_path)
