from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Department(db.Model):
    __tablename__ = 'departments'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(100), nullable=False, unique=True)
    department_code = db.Column(db.String(20), nullable=False, unique=True)
    head_user_id = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    users = db.relationship('User', backref='department', lazy=True,
                            foreign_keys='User.department_id')

    def __repr__(self):
        return f'<Department {self.department_code}: {self.department_name}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.Enum('receptionist', 'dept_user', 'admin', 'superadmin',
                             name='user_role_enum'), nullable=False)
    department_id = db.Column(
        db.Integer,
        db.ForeignKey('departments.department_id', ondelete='SET NULL', onupdate='CASCADE'),
        nullable=True
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def get_id(self):
        return str(self.user_id)

    @property
    def is_active_user(self):
        return self.is_active

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Document(db.Model):
    __tablename__ = 'documents'

    document_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracking_id = db.Column(db.String(20), nullable=False, unique=True, index=True)
    date_received = db.Column(db.Date, nullable=False)
    time_received = db.Column(db.Time, nullable=False)
    mode_of_receipt = db.Column(
        db.Enum('courier', 'speed_post', 'registered_post', 'hand_delivery',
                name='receipt_mode_enum'),
        nullable=False
    )
    sender_name = db.Column(db.String(100), nullable=False)
    sender_organisation = db.Column(db.String(150), nullable=True)
    sender_address = db.Column(db.Text, nullable=True)
    subject_description = db.Column(db.String(255), nullable=False)
    number_of_pages = db.Column(db.Integer, nullable=False, default=1)
    file_path = db.Column(db.String(255), nullable=True)
    file_type = db.Column(
        db.Enum('pdf', 'jpeg', 'png', name='file_type_enum'), nullable=True
    )
    ocr_text = db.Column(db.Text, nullable=True)
    ocr_status = db.Column(
        db.Enum('pending', 'completed', 'failed', name='ocr_status_enum'),
        nullable=False, default='pending'
    )
    status = db.Column(
        db.Enum('received', 'scanned', 'categorised', 'routed', 'notified',
                'acknowledged', 'escalated', 'archived', name='doc_status_enum'),
        nullable=False, default='received'
    )
    created_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # Relationships
    creator = db.relationship('User', backref='created_documents',
                              foreign_keys=[created_by])
    categorisation = db.relationship('Categorisation', backref='document',
                                     uselist=False, cascade='all, delete-orphan')
    routing = db.relationship('Routing', backref='document',
                              uselist=False, cascade='all, delete-orphan')
    acknowledgement = db.relationship('Acknowledgement', backref='document',
                                      uselist=False, cascade='all, delete-orphan')
    tracking_events = db.relationship('TrackingEvent', backref='document',
                                      lazy=True, cascade='all, delete-orphan',
                                      order_by='TrackingEvent.performed_at')
    notifications = db.relationship('Notification', backref='document',
                                    lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Document {self.tracking_id}>'


class Categorisation(db.Model):
    __tablename__ = 'categorisations'

    categorisation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey('documents.document_id', ondelete='CASCADE'),
        nullable=False, unique=True
    )
    suggested_department_id = db.Column(
        db.Integer,
        db.ForeignKey('departments.department_id', ondelete='SET NULL'),
        nullable=True
    )
    suggested_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True
    )
    document_type = db.Column(
        db.Enum('circular', 'legal_notice', 'tender', 'bill',
                'correspondence', 'audit', 'other', name='doc_type_enum'),
        nullable=False
    )
    confidence_score = db.Column(db.Numeric(4, 3), nullable=True)
    method = db.Column(
        db.Enum('ai_auto', 'ai_override', 'manual', name='cat_method_enum'),
        nullable=False
    )
    categorised_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True
    )
    categorised_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    suggested_department = db.relationship('Department',
                                           foreign_keys=[suggested_department_id])
    suggested_user = db.relationship('User', foreign_keys=[suggested_user_id])
    categoriser = db.relationship('User', foreign_keys=[categorised_by])

    def __repr__(self):
        return f'<Categorisation doc={self.document_id} type={self.document_type}>'


class Routing(db.Model):
    __tablename__ = 'routings'

    routing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey('documents.document_id', ondelete='CASCADE'),
        nullable=False, unique=True
    )
    routed_to_department_id = db.Column(
        db.Integer,
        db.ForeignKey('departments.department_id', ondelete='RESTRICT'),
        nullable=False
    )
    routed_to_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='RESTRICT'),
        nullable=False
    )
    routed_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='RESTRICT'),
        nullable=False
    )
    routed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sla_deadline = db.Column(db.DateTime, nullable=False)

    # Relationships
    routed_department = db.relationship('Department',
                                        foreign_keys=[routed_to_department_id])
    routed_user = db.relationship('User', foreign_keys=[routed_to_user_id])
    router = db.relationship('User', foreign_keys=[routed_by])

    def __repr__(self):
        return f'<Routing doc={self.document_id} -> dept={self.routed_to_department_id}>'


class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey('documents.document_id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )
    notification_type = db.Column(
        db.Enum('new_document', 'escalation', 'reminder',
                'acknowledgement_done', name='notif_type_enum'),
        nullable=False
    )
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', backref='notifications',
                           foreign_keys=[user_id])

    def __repr__(self):
        return f'<Notification {self.notification_type} for user={self.user_id}>'


class Acknowledgement(db.Model):
    __tablename__ = 'acknowledgements'

    acknowledgement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey('documents.document_id', ondelete='CASCADE'),
        nullable=False, unique=True
    )
    acknowledged_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='RESTRICT'),
        nullable=False
    )
    acknowledged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    remarks = db.Column(db.Text, nullable=True)
    was_escalated = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    acknowledger = db.relationship('User', foreign_keys=[acknowledged_by])

    def __repr__(self):
        return f'<Acknowledgement doc={self.document_id}>'


class TrackingEvent(db.Model):
    __tablename__ = 'tracking_events'

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey('documents.document_id', ondelete='CASCADE'),
        nullable=False
    )
    event_type = db.Column(db.String(50), nullable=False)
    event_description = db.Column(db.String(255), nullable=False)
    performed_by = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True
    )
    performed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    performer = db.relationship('User', foreign_keys=[performed_by])

    def __repr__(self):
        return f'<TrackingEvent {self.event_type} doc={self.document_id}>'


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(100), nullable=False)
    document_id = db.Column(
        db.Integer,
        db.ForeignKey('documents.document_id', ondelete='SET NULL'),
        nullable=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True
    )
    ip_address = db.Column(db.String(45), nullable=True)
    details = db.Column(db.Text, nullable=True)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    doc = db.relationship('Document', foreign_keys=[document_id])

    def __repr__(self):
        return f'<AuditLog {self.event_type} at {self.logged_at}>'
