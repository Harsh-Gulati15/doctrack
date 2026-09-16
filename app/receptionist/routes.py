import os
import uuid
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user

from app.receptionist import receptionist_bp
from app.auth.routes import role_required
from app.models import db, Document, Department, User, Categorisation, Routing, Notification, TrackingEvent, AuditLog

def generate_tracking_id():
    year = datetime.now().year
    last_doc = Document.query.filter(
        Document.tracking_id.like(f'DOC-{year}-%')
    ).order_by(Document.document_id.desc()).first()
    if last_doc:
        last_seq = int(last_doc.tracking_id.split('-')[2])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    return f'DOC-{year}-{str(new_seq).zfill(5)}'

@receptionist_bp.route('/dashboard')
@login_required
@role_required('receptionist')
def dashboard():
    today = datetime.today().date()
    today_docs = Document.query.filter(Document.date_received == today).count()
    pending_acks = Document.query.filter(Document.status.in_(['routed', 'notified'])).count()
    overdue_count = Routing.query.filter(Routing.sla_deadline < datetime.now()).join(Document).filter(Document.status.in_(['routed', 'notified'])).count()
    
    current_month = today.month
    current_year = today.year
    monthly_total = Document.query.filter(
        db.extract('month', Document.date_received) == current_month,
        db.extract('year', Document.date_received) == current_year
    ).count()

    recent_docs = Document.query.order_by(Document.created_at.desc()).limit(10).all()

    return render_template('receptionist/dashboard.html', 
                           today_docs=today_docs, 
                           pending_acks=pending_acks, 
                           overdue_count=overdue_count, 
                           monthly_total=monthly_total,
                           recent_docs=recent_docs)

@receptionist_bp.route('/register', methods=['GET', 'POST'])
@login_required
@role_required('receptionist')
def register():
    if request.method == 'POST':
        date_received_str = request.form.get('date_received')
        time_received_str = request.form.get('time_received')
        
        try:
            date_received = datetime.strptime(date_received_str, '%Y-%m-%d').date()
            time_received = datetime.strptime(time_received_str, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return redirect(request.url)

        mode_of_receipt = request.form.get('mode_of_receipt')
        sender_name = request.form.get('sender_name')
        sender_organisation = request.form.get('sender_organisation')
        sender_address = request.form.get('sender_address')
        subject_description = request.form.get('subject_description')
        number_of_pages = request.form.get('number_of_pages', type=int)

        file = request.files.get('file_upload')
        
        tracking_id = generate_tracking_id()
        
        doc = Document(
            tracking_id=tracking_id,
            date_received=date_received,
            time_received=time_received,
            mode_of_receipt=mode_of_receipt,
            sender_name=sender_name,
            sender_organisation=sender_organisation,
            sender_address=sender_address,
            subject_description=subject_description,
            number_of_pages=number_of_pages,
            status='received',
            created_by=current_user.user_id
        )

        db.session.add(doc)
        db.session.flush()

        if file and file.filename != '':
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            allowed_exts = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg'})
            if ext not in allowed_exts:
                flash('Invalid file extension.', 'danger')
                db.session.rollback()
                return redirect(request.url)
            
            filename = f"{uuid.uuid4().hex}.{ext}"

            try:
                from app.utils.storage import upload_file as storage_upload
                stored_path = storage_upload(file, filename)
            except Exception as e:
                current_app.logger.error(f'File upload failed: {e}')
                flash('File upload failed.', 'danger')
                db.session.rollback()
                return redirect(request.url)

            doc.file_path = stored_path
            doc.file_type = 'jpeg' if ext in ['jpg', 'jpeg'] else ext
            doc.status = 'scanned'
            
        db.session.commit()
        
        event = TrackingEvent(document_id=doc.document_id, event_type='REGISTERED', 
                              event_description=f'Document registered by {current_user.username}', 
                              performed_by=current_user.user_id)
        log = AuditLog(event_type='REGISTER', document_id=doc.document_id, 
                       user_id=current_user.user_id, ip_address=request.remote_addr, 
                       details=f'Document {tracking_id} registered')
        
        db.session.add(event)
        db.session.add(log)
        db.session.commit()

        if doc.file_path:
            try:
                from app.utils.ocr import extract_text
                from app.utils.storage import download_to_temp
                temp_path = download_to_temp(doc.file_path, doc.file_type)
                ocr_text = extract_text(temp_path, doc.file_type)
                # Clean up temp file if it was downloaded from GCS
                if current_app.config.get('GCS_BUCKET_NAME') and os.path.exists(temp_path):
                    os.unlink(temp_path)
                doc.ocr_text = ocr_text
                doc.ocr_status = 'completed'
                db.session.add(TrackingEvent(document_id=doc.document_id, event_type='OCR_COMPLETED', event_description='OCR processing successful', performed_by=current_user.user_id))
            except Exception as e:
                current_app.logger.error(f'OCR failed: {e}')
                doc.ocr_status = 'failed'
                db.session.add(TrackingEvent(document_id=doc.document_id, event_type='OCR_FAILED', event_description='OCR processing failed', performed_by=current_user.user_id))
                ocr_text = None
            db.session.commit()

            if doc.ocr_status == 'completed' and ocr_text:
                try:
                    from app.utils.ai_categoriser import categorise_document
                    result = categorise_document(ocr_text)
                except Exception as e:
                    current_app.logger.error(f'AI categorisation failed: {e}')
                    result = None
                
                if result:
                    cat = Categorisation(
                        document_id=doc.document_id,
                        suggested_department_id=result.get('suggested_department_id'),
                        suggested_user_id=result.get('suggested_user_id'),
                        document_type=result.get('document_type'),
                        confidence_score=result.get('confidence_score'),
                        method='ai_auto' if result.get('auto_route') else 'manual',
                        categorised_by=current_user.user_id
                    )
                    db.session.add(cat)
                    db.session.add(TrackingEvent(document_id=doc.document_id, event_type='CATEGORISED', event_description='Document categorised by AI', performed_by=current_user.user_id))
                    db.session.commit()
                    
                    if result.get('auto_route'):
                        sla_hours = current_app.config.get('SLA_HOURS', 48)
                        routing = Routing(
                            document_id=doc.document_id,
                            routed_to_department_id=result.get('suggested_department_id'),
                            routed_to_user_id=result.get('suggested_user_id'),
                            routed_by=current_user.user_id,
                            sla_deadline=datetime.now() + timedelta(hours=sla_hours)
                        )
                        db.session.add(routing)
                        doc.status = 'notified'
                        db.session.commit()
                        
                        try:
                            from app.utils.notifications import send_notification
                            send_notification(doc.document_id, result.get('suggested_user_id'), 'new_document', f'New document routed: {doc.tracking_id}')
                        except:
                            pass
                        
                        db.session.add(TrackingEvent(document_id=doc.document_id, event_type='ROUTED', event_description='Auto-routed by AI', performed_by=current_user.user_id))
                        db.session.add(TrackingEvent(document_id=doc.document_id, event_type='NOTIFIED', event_description='Notification sent to recipient', performed_by=current_user.user_id))
                        db.session.commit()
                        flash(f'Document {tracking_id} registered and auto-routed successfully!', 'success')
                        return redirect(url_for('receptionist.document_detail', document_id=doc.document_id))
                    else:
                        doc.status = 'categorised'
                        db.session.commit()
                        flash(f'Document {tracking_id} registered. Please confirm categorisation.', 'info')
                        return redirect(url_for('receptionist.categorise', document_id=doc.document_id))

        flash(f'Document {tracking_id} registered successfully!', 'success')
        return redirect(url_for('receptionist.document_detail', document_id=doc.document_id))
        
    return render_template('receptionist/register.html')

@receptionist_bp.route('/categorise/<int:document_id>', methods=['GET', 'POST'])
@login_required
@role_required('receptionist')
def categorise(document_id):
    doc = Document.query.get_or_404(document_id)
    cat = getattr(doc, 'categorisation', None)
    # the relationship is one-to-one but often lists are returned, handle cautiously
    if isinstance(cat, list) and len(cat) > 0:
        cat = cat[0]
        
    departments = Department.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        dept_id = request.form.get('department_id', type=int)
        user_id = request.form.get('user_id', type=int)
        doc_type = request.form.get('document_type')
        
        is_override = True
        if cat and cat.suggested_department_id == dept_id and cat.document_type == doc_type:
            is_override = False
            
        if not cat:
            cat = Categorisation(document_id=doc.document_id)
            db.session.add(cat)
            
        cat.suggested_department_id = dept_id
        cat.suggested_user_id = user_id
        cat.document_type = doc_type
        cat.method = 'ai_override' if is_override else 'ai_auto'
        cat.categorised_by = current_user.user_id
        cat.categorised_at = datetime.now()
        
        sla_hours = current_app.config.get('SLA_HOURS', 48)
        routing = Routing(
            document_id=doc.document_id,
            routed_to_department_id=dept_id,
            routed_to_user_id=user_id,
            routed_by=current_user.user_id,
            sla_deadline=datetime.now() + timedelta(hours=sla_hours)
        )
        db.session.add(routing)
        
        doc.status = 'notified'
        db.session.commit()
        
        db.session.add(TrackingEvent(document_id=doc.document_id, event_type='CATEGORISED', event_description=f'Categorised manually as {doc_type}', performed_by=current_user.user_id))
        db.session.add(TrackingEvent(document_id=doc.document_id, event_type='ROUTED', event_description=f'Routed to user {user_id}', performed_by=current_user.user_id))
        db.session.add(AuditLog(event_type='ROUTE', document_id=doc.document_id, user_id=current_user.user_id, ip_address=request.remote_addr, details='Document routed'))
        db.session.commit()
        
        try:
            from app.utils.notifications import send_notification
            send_notification(doc.document_id, user_id, 'new_document', f'New document routed: {doc.tracking_id}')
            db.session.add(TrackingEvent(document_id=doc.document_id, event_type='NOTIFIED', event_description='Notification sent to recipient', performed_by=current_user.user_id))
            db.session.commit()
        except:
            pass

        flash('Document routed successfully!', 'success')
        return redirect(url_for('receptionist.document_detail', document_id=doc.document_id))
        
    initial_users = User.query.filter_by(department_id=departments[0].department_id).all() if departments else []
    
    return render_template('receptionist/categorise.html', doc=doc, categorisation=cat, departments=departments, initial_users=initial_users)

@receptionist_bp.route('/api/users/<int:department_id>')
@login_required
def get_users_by_dept(department_id):
    users = User.query.filter_by(department_id=department_id, is_active=True).all()
    return jsonify([{'id': u.user_id, 'name': u.full_name} for u in users])

@receptionist_bp.route('/documents')
@login_required
@role_required('receptionist')
def documents():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    query = Document.query
    if search:
        query = query.filter(
            db.or_(
                Document.tracking_id.ilike(f'%{search}%'),
                Document.sender_name.ilike(f'%{search}%'),
                Document.subject_description.ilike(f'%{search}%')
            )
        )
    if status:
        query = query.filter(Document.status == status)
        
    pagination = query.order_by(Document.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('receptionist/documents.html', pagination=pagination, search=search, status=status)

@receptionist_bp.route('/document/<int:document_id>')
@login_required
@role_required('receptionist')
def document_detail(document_id):
    doc = Document.query.get_or_404(document_id)
    return render_template('receptionist/document_detail.html', doc=doc)

@receptionist_bp.route('/track')
@login_required
@role_required('receptionist')
def track():
    tracking_id = request.args.get('tracking_id', '')
    doc = None
    if tracking_id:
        doc = Document.query.filter_by(tracking_id=tracking_id).first()
        if not doc:
            flash(f'Document with Tracking ID {tracking_id} not found.', 'warning')
    return render_template('receptionist/track.html', doc=doc, tracking_id=tracking_id)

@receptionist_bp.route('/serve-file/<int:document_id>')
@login_required
def serve_file(document_id):
    doc = Document.query.get_or_404(document_id)
    if not doc.file_path:
        flash('No file attached to this document.', 'warning')
        return redirect(url_for('receptionist.document_detail', document_id=doc.document_id))
    
    from app.utils.storage import serve_file as storage_serve
    return storage_serve(doc.file_path)
