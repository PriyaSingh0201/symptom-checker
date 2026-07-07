# routes/dashboard.py – Dashboard page
from flask import Blueprint, render_template, jsonify
from models.assessment import Assessment
from utils.jwt_helper import token_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@token_required
def dashboard(current_user):
    """Serve the main dashboard for authenticated users."""
    return render_template("dashboard.html")


@dashboard_bp.route("/api/dashboard")
@token_required
def get_dashboard_data(current_user):
    """GET /api/dashboard – Retrieve latest assessment and summary stats."""
    latest = (
        Assessment.query
        .filter_by(user_id=current_user.id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    
    total = Assessment.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        "fullname": current_user.fullname,
        "total_assessments": total,
        "latest_assessment": latest.to_dict() if latest else None
    }), 200
