# routes/profile.py – User profile and password change
import re
from flask import Blueprint, request, jsonify, render_template
from database import db
from models.user import User
from models.assessment import Assessment
from utils.jwt_helper import token_required

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@token_required
def profile_page(current_user):
    """Serve the user profile page."""
    return render_template("profile.html")


@profile_bp.route("/api/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """GET /api/profile – Return current user's profile data with Phase 2 stats."""
    from collections import Counter
    all_assessments = Assessment.query.filter_by(user_id=current_user.id).all()
    
    total = len(all_assessments)
    member_since = current_user.created_at.strftime("%d %b %Y")
    
    latest = (
        Assessment.query
        .filter_by(user_id=current_user.id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    last_consultation = latest.created_at.strftime("%d %b %Y, %I:%M %p") if latest else "No assessments yet"
    
    # Calculate common symptoms
    symptom_list = []
    for a in all_assessments:
        # Split symptoms by comma and remove spaces
        parts = [p.strip().lower() for p in a.symptoms.split(",") if p.strip()]
        symptom_list.extend(parts)
        
    common_symptoms = "None"
    if symptom_list:
        counts = Counter(symptom_list)
        common_symptoms = ", ".join(k.capitalize() for k, v in counts.most_common(3))
        
    # Calculate average severity
    avg_severity = "None"
    if all_assessments:
        val_map = {"Mild": 1.0, "Moderate": 2.0, "Severe": 3.0}
        total_val = sum(val_map.get(a.severity.capitalize(), 2.0) for a in all_assessments)
        avg_val = total_val / total
        if avg_val < 1.5:
            avg_severity = "Mild"
        elif avg_val < 2.5:
            avg_severity = "Moderate"
        else:
            avg_severity = "Severe"
            
    res = current_user.to_dict()
    res.update({
        "total_assessments": total,
        "common_symptoms": common_symptoms,
        "avg_severity": avg_severity,
        "last_consultation": last_consultation,
        "member_since": member_since
    })
    return jsonify(res), 200


@profile_bp.route("/api/change-password", methods=["POST"])
@token_required
def change_password(current_user):
    """
    POST /api/change-password
    Body: { current_password, new_password, confirm_password }
    """
    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not all([current_password, new_password, confirm_password]):
        return jsonify({"error": "All password fields are required."}), 400

    if not current_user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect."}), 401

    if new_password != confirm_password:
        return jsonify({"error": "New passwords do not match."}), 400

    # Validate strength
    if len(new_password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400
    if not re.search(r"[A-Z]", new_password):
        return jsonify({"error": "Password must contain at least one uppercase letter."}), 400
    if not re.search(r"[a-z]", new_password):
        return jsonify({"error": "Password must contain at least one lowercase letter."}), 400
    if not re.search(r"\d", new_password):
        return jsonify({"error": "Password must contain at least one number."}), 400
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", new_password):
        return jsonify({"error": "Password must contain at least one special character."}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password changed successfully!"}), 200
