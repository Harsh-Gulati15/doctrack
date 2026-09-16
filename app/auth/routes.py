import bcrypt
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app.auth import auth_bp
from app.models import db, User, Notification, AuditLog

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            if not user.is_active:
                flash('Your account is deactivated. Please contact an administrator.', 'danger')
                return redirect(url_for('auth.login'))
                
            login_user(user, remember=remember)
            session.permanent = True
            
            user.last_login = datetime.utcnow()
            
            audit = AuditLog(
                event_type='LOGIN',
                user_id=user.user_id,
                ip_address=request.remote_addr,
                details='User logged in successfully'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('Logged in successfully.', 'success')
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
                
            return redirect(next_page)
            
        flash('Invalid username or password.', 'danger')
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    audit = AuditLog(
        event_type='LOGOUT',
        user_id=current_user.user_id,
        ip_address=request.remote_addr,
        details='User logged out'
    )
    db.session.add(audit)
    db.session.commit()
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    pagination = Notification.query.filter_by(user_id=current_user.user_id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
        
    return render_template('auth/notifications.html', pagination=pagination)

@auth_bp.route('/notifications/read/<int:id>', methods=['POST'])
@login_required
def read_notification(id):
    notification = Notification.query.get_or_404(id)
    
    if notification.user_id != current_user.user_id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('auth.notifications'))
        
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(request.referrer or url_for('auth.notifications'))

@auth_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def read_all_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.user_id, is_read=False).all()
    
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
    db.session.commit()
    flash('All notifications marked as read.', 'success')
    
    return redirect(url_for('auth.notifications'))
