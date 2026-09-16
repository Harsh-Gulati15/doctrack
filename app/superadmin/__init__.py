from flask import Blueprint

superadmin_bp = Blueprint('superadmin', __name__)

from app.superadmin import routes
