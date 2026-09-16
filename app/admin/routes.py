import bcrypt
from datetime import datetime, date
import io
import csv
from flask import render_template, request, flash, redirect, url_for, jsonify, current_app, send_file, session, make_response
from flask_login import login_required, current_user
from sqlalchemy import func, or_
import os

from app.admin import admin_bp
from app.models import db, Document, Department, User, Categorisation, Routing, Notification, Acknowledgement, TrackingEvent, AuditLog
from app.auth.routes import role_required

try:
    from app.utils.reports import (
        daily_inward_register, pending_acknowledgements,
        overdue_documents, department_volume, document_type_distribution
    )
except ImportError:
    daily_inward_register = lambda d: []
    pending_acknowledgements = lambda: []
    overdue_documents = lambda: []
    department_volume = lambda s, e: []
    document_type_distribution = lambda s, e: []

try:
    from weasyprint import HTML
except ImportError:
    HTML = None

@admin_bp.before_request
@login_required
@role_required('admin', 'superadmin')
def restrict_admin():
    pass

@admin_bp.route('/dashboard')
def dashboard():
    today = date.today()
    docs_today = Document.query.filter(func.date(Document.date_received) == today).count()
    pending_acks = Document.query.filter_by(status='notified').count()
    overdue = Document.query.filter_by(status='escalated').count()
    
    current_month = today.month
    current_year = today.year
    monthly_total = Document.query.filter(
        func.extract('month', Document.date_received) == current_month,
        func.extract('year', Document.date_received) == current_year
    ).count()

    dept_counts_query = db.session.query(
        Department.department_name,
        func.count(Routing.document_id)
    ).join(Routing, Department.department_id == Routing.routed_to_department_id)\
     .filter(
        func.extract('month', Routing.routed_at) == current_month,
        func.extract('year', Routing.routed_at) == current_year
     ).group_by(Department.department_name).all()

    dept_labels = [row[0] for row in dept_counts_query]
    dept_counts = [row[1] for row in dept_counts_query]

    recent_docs = Document.query.order_by(Document.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                           docs_today=docs_today,
                           pending_acks=pending_acks,
                           overdue=overdue,
                           monthly_total=monthly_total,
                           dept_labels=dept_labels,
                           dept_counts=dept_counts,
                           recent_docs=recent_docs)

@admin_bp.route('/users')
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', pagination=pagination)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
def create_user():
    departments = Department.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        department_id = request.form.get('department_id')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.create_user'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.create_user'))

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            department_id=department_id if department_id else None,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        AuditLog.query.session.add(AuditLog(
            event_type='user_created',
            user_id=current_user.user_id,
            ip_address=request.remote_addr,
            details=f'Created user {username}'
        ))
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', departments=departments, user=None)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    departments = Department.query.all()
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.role = request.form.get('role')
        department_id = request.form.get('department_id')
        user.department_id = department_id if department_id else None

        password = request.form.get('password')
        if password:
            user.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

        db.session.commit()
        AuditLog.query.session.add(AuditLog(
            event_type='user_edited',
            user_id=current_user.user_id,
            ip_address=request.remote_addr,
            details=f'Edited user {user.username}'
        ))
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', departments=departments, user=user)

@admin_bp.route('/users/toggle/<int:user_id>', methods=['POST'])
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    AuditLog.query.session.add(AuditLog(
        event_type='user_toggled',
        user_id=current_user.user_id,
        ip_address=request.remote_addr,
        details=f'Toggled user {user.username} active status to {user.is_active}'
    ))
    db.session.commit()
    flash(f'User {user.username} status toggled.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/departments')
def departments():
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)

@admin_bp.route('/departments/create', methods=['GET', 'POST'])
def create_department():
    users = User.query.all()
    if request.method == 'POST':
        name = request.form.get('department_name')
        code = request.form.get('department_code')
        head_id = request.form.get('head_user_id')

        if Department.query.filter_by(department_name=name).first():
            flash('Department name exists.', 'danger')
            return redirect(url_for('admin.create_department'))
        if Department.query.filter_by(department_code=code).first():
            flash('Department code exists.', 'danger')
            return redirect(url_for('admin.create_department'))

        dept = Department(
            department_name=name,
            department_code=code,
            head_user_id=head_id if head_id else None,
            is_active=True
        )
        db.session.add(dept)
        db.session.commit()
        AuditLog.query.session.add(AuditLog(
            event_type='department_created',
            user_id=current_user.user_id,
            ip_address=request.remote_addr,
            details=f'Created department {name}'
        ))
        db.session.commit()
        flash('Department created.', 'success')
        return redirect(url_for('admin.departments'))
    return render_template('admin/department_form.html', users=users, department=None)

@admin_bp.route('/departments/edit/<int:department_id>', methods=['GET', 'POST'])
def edit_department(department_id):
    dept = Department.query.get_or_404(department_id)
    users = User.query.all()
    if request.method == 'POST':
        dept.department_name = request.form.get('department_name')
        dept.department_code = request.form.get('department_code')
        head_id = request.form.get('head_user_id')
        dept.head_user_id = head_id if head_id else None

        db.session.commit()
        AuditLog.query.session.add(AuditLog(
            event_type='department_edited',
            user_id=current_user.user_id,
            ip_address=request.remote_addr,
            details=f'Edited department {dept.department_name}'
        ))
        db.session.commit()
        flash('Department updated.', 'success')
        return redirect(url_for('admin.departments'))
    return render_template('admin/department_form.html', users=users, department=dept)

@admin_bp.route('/documents')
def documents():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    dept_filter = request.args.get('department_id', '')

    query = Document.query

    if search_query:
        query = query.filter(or_(
            Document.tracking_id.ilike(f'%{search_query}%'),
            Document.sender_name.ilike(f'%{search_query}%'),
            Document.subject_description.ilike(f'%{search_query}%')
        ))

    if status_filter:
        query = query.filter_by(status=status_filter)

    if dept_filter:
        query = query.join(Routing).filter(Routing.routed_to_department_id == dept_filter)

    query = query.order_by(Document.created_at.desc())
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    departments = Department.query.all()

    return render_template('admin/documents.html', pagination=pagination, departments=departments)

@admin_bp.route('/document/<int:document_id>')
def document_detail(document_id):
    document = Document.query.get_or_404(document_id)
    return render_template('admin/document_detail.html', document=document)

@admin_bp.route('/reports')
def reports():
    return render_template('admin/reports.html')

@admin_bp.route('/reports/generate', methods=['POST'])
def generate_report():
    report_type = request.form.get('report_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    session['report_type'] = report_type
    session['start_date'] = start_date
    session['end_date'] = end_date

    data = []
    if report_type == 'daily_inward':
        data = daily_inward_register(start_date)
    elif report_type == 'pending_ack':
        data = pending_acknowledgements()
    elif report_type == 'overdue':
        data = overdue_documents()
    elif report_type == 'dept_volume':
        data = department_volume(start_date, end_date)
    elif report_type == 'type_dist':
        data = document_type_distribution(start_date, end_date)

    return render_template('admin/report_result.html', data=data, report_type=report_type)

@admin_bp.route('/reports/download-csv/<report_type>')
def download_csv(report_type):
    start_date = session.get('start_date')
    end_date = session.get('end_date')
    data = []
    if report_type == 'daily_inward':
        data = daily_inward_register(start_date)
    elif report_type == 'pending_ack':
        data = pending_acknowledgements()
    elif report_type == 'overdue':
        data = overdue_documents()
    elif report_type == 'dept_volume':
        data = department_volume(start_date, end_date)
    elif report_type == 'type_dist':
        data = document_type_distribution(start_date, end_date)

    si = io.StringIO()
    cw = csv.writer(si)
    if data and len(data) > 0:
        cw.writerow(data[0].keys())
        for row in data:
            cw.writerow(row.values())

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={report_type}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@admin_bp.route('/reports/download-pdf/<report_type>')
def download_pdf(report_type):
    if HTML is None:
        flash('WeasyPrint is not installed or failed to load.', 'danger')
        return redirect(url_for('admin.reports'))

    start_date = session.get('start_date')
    end_date = session.get('end_date')
    data = []
    if report_type == 'daily_inward':
        data = daily_inward_register(start_date)
    elif report_type == 'pending_ack':
        data = pending_acknowledgements()
    elif report_type == 'overdue':
        data = overdue_documents()
    elif report_type == 'dept_volume':
        data = department_volume(start_date, end_date)
    elif report_type == 'type_dist':
        data = document_type_distribution(start_date, end_date)

    html_content = render_template('admin/report_result.html', data=data, report_type=report_type, pdf_mode=True)
    pdf = HTML(string=html_content).write_pdf()

    output = make_response(pdf)
    output.headers['Content-Disposition'] = f'attachment; filename={report_type}.pdf'
    output.headers['Content-type'] = 'application/pdf'
    return output

@admin_bp.route('/track')
def track():
    tracking_id = request.args.get('tracking_id')
    document = None
    if tracking_id:
        document = Document.query.filter_by(tracking_id=tracking_id).first()
        if not document:
            flash('Document not found.', 'warning')
    return render_template('admin/track.html', document=document)

@admin_bp.route('/serve-file/<int:document_id>')
def serve_file(document_id):
    doc = Document.query.get_or_404(document_id)
    if not doc.file_path:
        flash('File not found.', 'danger')
        return redirect(url_for('admin.document_detail', document_id=doc.document_id))

    from app.utils.storage import serve_file as storage_serve
    return storage_serve(doc.file_path)
