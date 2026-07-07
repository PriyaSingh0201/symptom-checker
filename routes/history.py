# routes/history.py – Assessment history, search, filter, delete
from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import or_, func
from database import db
from models.assessment import Assessment
from utils.jwt_helper import token_required

history_bp = Blueprint("history", __name__)


@history_bp.route("/history")
@token_required
def history_page(current_user):
    """Serve the assessment history page."""
    return render_template("history.html")


@history_bp.route("/api/history", methods=["GET"])
@token_required
def get_history(current_user):
    """
    GET /api/history
    Query params: page, per_page, severity, keyword, doctor, sort, date_from, date_to
    Returns: paginated list of assessments for the current user.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    severity = request.args.get("severity", "").strip()
    keyword = request.args.get("keyword", "").strip()
    doctor = request.args.get("doctor", "").strip()
    sort = request.args.get("sort", "newest")           # newest | oldest
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()

    query = Assessment.query.filter_by(user_id=current_user.id)

    # ── Filters ────────────────────────────────────────────────────────────
    if severity:
        query = query.filter(Assessment.severity == severity)
    if doctor:
        query = query.filter(Assessment.recommended_doctor.ilike(f"%{doctor}%"))
    if keyword:
        query = query.filter(
            or_(
                Assessment.symptoms.ilike(f"%{keyword}%"),
                Assessment.possible_condition.ilike(f"%{keyword}%"),
            )
        )
    if date_from:
        query = query.filter(func.date(Assessment.created_at) >= date_from)
    if date_to:
        query = query.filter(func.date(Assessment.created_at) <= date_to)

    # ── Sorting ────────────────────────────────────────────────────────────
    if sort == "oldest":
        query = query.order_by(Assessment.created_at.asc())
    else:
        query = query.order_by(Assessment.created_at.desc())

    # ── Pagination ─────────────────────────────────────────────────────────
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "assessments": [a.to_dict() for a in paginated.items],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": page,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev,
    }), 200


@history_bp.route("/api/history/<int:assessment_id>", methods=["GET"])
@token_required
def get_assessment(current_user, assessment_id):
    """GET /api/history/<id> – Retrieve a single assessment and load into memory."""
    assessment = Assessment.query.filter_by(
        id=assessment_id, user_id=current_user.id
    ).first_or_404()
    
    from utils.conversation_memory import store_consultation
    store_consultation(assessment.to_dict())
    
    return jsonify(assessment.to_dict()), 200


@history_bp.route("/api/history/<int:assessment_id>", methods=["DELETE"])
@token_required
def delete_assessment(current_user, assessment_id):
    """DELETE /api/history/<id> – Delete one of the user's assessments."""
    assessment = Assessment.query.filter_by(
        id=assessment_id, user_id=current_user.id
    ).first()

    if not assessment:
        return jsonify({"error": "Assessment not found."}), 404

    db.session.delete(assessment)
    db.session.commit()
    return jsonify({"message": "Assessment deleted successfully."}), 200
