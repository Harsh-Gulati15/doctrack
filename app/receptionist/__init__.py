from flask import Blueprint
receptionist_bp = Blueprint('receptionist', __name__)
from app.receptionist import routes
