# routes/pdf.py – PDF download endpoint
from flask import Blueprint, send_file, jsonify
from io import BytesIO
from models.assessment import Assessment
from utils.jwt_helper import token_required
from utils.pdf_generator import generate_pdf

pdf_bp = Blueprint("pdf", __name__)


@pdf_bp.route("/api/download-pdf/<int:assessment_id>", methods=["GET"])
@token_required
def download_pdf(current_user, assessment_id):
    """
    GET /api/download-pdf/<id>
    Generate and stream a PDF report for the given assessment.
    """
    assessment = Assessment.query.filter_by(
        id=assessment_id, user_id=current_user.id
    ).first()

    if not assessment:
        return jsonify({"error": "Assessment not found."}), 404

    try:
        pdf_bytes = generate_pdf(assessment.to_dict(), current_user.to_dict())
    except Exception as exc:
        return jsonify({"error": f"PDF generation failed: {str(exc)}"}), 500

    filename = (
        f"health_assessment_{assessment.id}_"
        f"{assessment.created_at.strftime('%Y%m%d')}.pdf"
    )

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
