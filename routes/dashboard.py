# routes/dashboard.py – Dashboard page
from flask import Blueprint, render_template
from utils.jwt_helper import token_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@token_required
def dashboard(current_user):
    """Serve the main dashboard for authenticated users."""
    return render_template("dashboard.html")
