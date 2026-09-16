import os
from datetime import datetime
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

from app.config import Config
from app.models import db

login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Initialise extensions ──
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # ── User loader ──
    from app.models import User, Notification

    @login_manager.user_loader
    def load_user(user_id):
        user = db.session.get(User, int(user_id))
        if user and not user.is_active:
            return None
        return user

    # ── Context processor: inject unread notification count + year ──
    @app.context_processor
    def inject_globals():
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                user_id=current_user.user_id, is_read=False
            ).count()
        return dict(unread_count=unread_count, now=datetime.utcnow())

    # ── Ensure upload folder exists (local dev only) ──
    if not app.config.get('GCS_BUCKET_NAME'):
        upload_path = os.path.join(os.path.dirname(app.root_path), app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_path, exist_ok=True)
        app.config['UPLOAD_FOLDER_ABS'] = os.path.abspath(upload_path)
    else:
        app.config['UPLOAD_FOLDER_ABS'] = '/tmp/uploads'
        os.makedirs('/tmp/uploads', exist_ok=True)

    # ── Register blueprints ──
    from app.auth import auth_bp
    from app.receptionist import receptionist_bp
    from app.department import department_bp
    from app.admin import admin_bp
    from app.superadmin import superadmin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(receptionist_bp, url_prefix='/receptionist')
    app.register_blueprint(department_bp, url_prefix='/department')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(superadmin_bp, url_prefix='/superadmin')

    # ── Root redirect ──
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            role_map = {
                'receptionist': 'receptionist.dashboard',
                'dept_user': 'department.dashboard',
                'admin': 'admin.dashboard',
                'superadmin': 'admin.dashboard',
            }
            return redirect(url_for(role_map.get(current_user.role, 'auth.login')))
        return redirect(url_for('auth.login'))

    # ── Create tables ──
    with app.app_context():
        db.create_all()

    # ── Start SLA scheduler ──
    try:
        from app.utils.scheduler import start_scheduler
        start_scheduler(app)
    except Exception as e:
        app.logger.warning(f'Scheduler failed to start: {e}')

    return app
