# utils/pdf_generator.py – Professional medical PDF reports using ReportLab
from io import BytesIO
from datetime import datetime
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


# -- Colour palette -----------------------------------------------------------

PINK        = colors.HexColor("#D94675")
LIGHT_PINK  = colors.HexColor("#FFF0F5")
PINK_BORDER = colors.HexColor("#FECDD3")
GREEN       = colors.HexColor("#10B981")
RED         = colors.HexColor("#EF4444")
YELLOW      = colors.HexColor("#F59E0B")
DARK        = colors.HexColor("#1E293B")
GREY        = colors.HexColor("#64748B")
LIGHT_GREY  = colors.HexColor("#F8FAFC")
WHITE       = colors.white


def _severity_color(severity: str):
    return {"Mild": GREEN, "Moderate": YELLOW, "Severe": RED}.get(severity, GREY)


# -- Style helpers ------------------------------------------------------------

def _build_styles():
    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            fontSize=22,
            fontName="Helvetica-Bold",
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            fontSize=11,
            fontName="Helvetica",
            textColor=colors.HexColor("#FECDD3"),
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        "section_header": ParagraphStyle(
            "SectionHeader",
            fontSize=12,
            fontName="Helvetica-Bold",
            textColor=PINK,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            fontSize=10,
            fontName="Helvetica",
            textColor=DARK,
            leading=16,
            alignment=TA_JUSTIFY,
        ),
        "label": ParagraphStyle(
            "Label",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=GREY,
        ),
        "disclaimer": ParagraphStyle(
            "Disclaimer",
            fontSize=8,
            fontName="Helvetica-Oblique",
            textColor=GREY,
            leading=12,
            alignment=TA_JUSTIFY,
        ),
        "condition": ParagraphStyle(
            "Condition",
            fontSize=15,
            fontName="Helvetica-Bold",
            textColor=PINK,
            alignment=TA_LEFT,
            spaceBefore=2,
            spaceAfter=2,
        ),
    }
    return styles


# -- Main generator -----------------------------------------------------------

def _safe_text(value, default="") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return str(value or default)


def _safe_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []


def _safe_dict(value):
    if isinstance(value, dict):
        return value
    return {}


def generate_pdf(assessment: dict, user: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm,
        title="AI Clinical Intelligence Report",
        author="Symptom Checker",
    )

    styles = _build_styles()
    story = []

    # -- Header banner --------------------------------------------------------
    header_data = [[
        Paragraph("Symptom Intelligence Engine", styles["title"]),
        Paragraph("Clinical Intelligence Report", styles["subtitle"]),
    ]]
    header_table = Table(header_data, colWidths=[10 * cm, 7 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PINK),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4 * cm))

    # -- Report metadata ------------------------------------------------------
    generated_at = datetime.now().strftime("%d %B %Y, %I:%M %p")
    report_id = assessment.get("id") or 0
    meta_data = [[
        "Report ID:", f"CLN-{int(report_id):04d}",
        "Generated:", generated_at,
    ]]
    meta_table = Table(meta_data, colWidths=[3 * cm, 5.5 * cm, 3 * cm, 5.5 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",  (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), GREY),
        ("TEXTCOLOR", (2, 0), (2, -1), GREY),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK),
        ("TEXTCOLOR", (3, 0), (3, -1), DARK),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4 * cm))

    # -- Emergency Banner ----------------------------------------------------
    if assessment.get("emergency_flag"):
        emerg_text = (
            "<b>🚨 EMERGENCY ALERT: IMMEDIATE MEDICAL ATTENTION RECOMMENDED</b><br/>"
            "This consultation matches clinical emergency indicators. Home care is bypassed. "
            "Seek immediate care or call local emergency services."
        )
        urgency_style = ParagraphStyle(
            "UrgencyStyle",
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=RED,
            leading=14
        )
        emerg_table = Table([[Paragraph(emerg_text, urgency_style)]], colWidths=[17 * cm])
        emerg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEE2E2")),
            ("BOX", (0, 0), (-1, -1), 1.5, RED),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
        story.append(emerg_table)
        story.append(Spacer(1, 0.4 * cm))

    story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))

    # -- Patient Information --------------------------------------------------
    story.append(Paragraph("Patient Information", styles["section_header"]))

    style_body = styles["body"]
    style_label = styles["label"]

    full_name = _safe_text(user.get("fullname"), "Unknown")
    email = _safe_text(user.get("email"), "N/A")
    age = _safe_text(assessment.get("age"), "N/A")
    gender = _safe_text(assessment.get("gender"), "N/A")
    duration = _safe_text(assessment.get("duration"), "N/A")
    created_date = _safe_text(assessment.get("created_date"), "N/A")

    patient_data = [
        [Paragraph("Full Name", style_label), Paragraph(full_name, style_body),
         Paragraph("Email", style_label), Paragraph(email, style_body)],
        
        [Paragraph("Age", style_label), Paragraph(str(age), style_body),
         Paragraph("Gender", style_label), Paragraph(gender.capitalize() if gender and gender != "N/A" else gender, style_body)],
         
        [Paragraph("Symptom Duration", style_label), Paragraph(duration, style_body),
         Paragraph("Assessment Date", style_label), Paragraph(created_date, style_body)],
         
        [Paragraph("Height / Weight", style_label), Paragraph(f"{_safe_text(assessment.get('height'), 'N/A')} / {_safe_text(assessment.get('weight'), 'N/A')}", style_body),
         Paragraph("Blood Pressure", style_label), Paragraph(_safe_text(assessment.get("blood_pressure"), "N/A"), style_body)],
         
        [Paragraph("Temp / Pain Level", style_label), Paragraph(f"{_safe_text(assessment.get('body_temperature'), 'N/A')}°F / Pain: {_safe_text(assessment.get('pain_level'), 'N/A')}/10", style_body),
         Paragraph("Pregnancy Status", style_label), Paragraph(_safe_text(assessment.get("pregnancy_status"), "N/A"), style_body)],
         
        [Paragraph("Medications", style_label), Paragraph(_safe_text(assessment.get("medications"), "None"), style_body),
         Paragraph("Allergies", style_label), Paragraph(_safe_text(assessment.get("allergies"), "None"), style_body)],
         
        [Paragraph("Existing Conditions", style_label), Paragraph(_safe_text(assessment.get("medical_conditions"), "None"), style_body),
         Paragraph("Smoking / Alcohol", style_label), Paragraph(f"{_safe_text(assessment.get('smoking_status'), 'N/A')} / {_safe_text(assessment.get('alcohol_consumption'), 'N/A')}", style_body)]
    ]

    patient_table = Table(patient_data, colWidths=[4 * cm, 4.5 * cm, 4 * cm, 4.5 * cm])
    patient_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_PINK, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, PINK_BORDER),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.4 * cm))

    # -- Reported Symptoms ----------------------------------------------------
    story.append(Paragraph("Primary & Secondary Symptoms", styles["section_header"]))
    story.append(Paragraph(_safe_text(assessment.get("symptoms"), "No symptoms recorded."), styles["body"]))
    story.append(Spacer(1, 0.4 * cm))

    # -- Suspected Clinical Conditions (Top 3) --------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))
    story.append(Paragraph("Clinical Analysis & Sussed Conditions", styles["section_header"]))

    conds_table_data = [[
        Paragraph("<b>Suspected Condition</b>", style_label),
        Paragraph("<b>Confidence</b>", style_label),
        Paragraph("<b>Severity</b>", style_label),
        Paragraph("<b>Department</b>", style_label)
    ]]
    
    for c in _safe_list(assessment.get("top_conditions")):
        cond = _safe_dict(c)
        severity = _safe_text(cond.get("severity"), "Moderate")
        sev_col = _severity_color(severity)
        conds_table_data.append([
            Paragraph(f"<b>{_safe_text(cond.get('condition'), 'Unknown condition')}</b>", style_body),
            Paragraph(f"{_safe_text(cond.get('confidence'), '0')}%", style_body),
            Paragraph(f"<font color='{sev_col}'><b>{severity}</b></font>", style_body),
            Paragraph(_safe_text(cond.get('recommended_department'), 'General Physician'), style_body)
        ])
        
    conds_table = Table(conds_table_data, colWidths=[6.5 * cm, 3 * cm, 3.5 * cm, 4 * cm])
    conds_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_PINK),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, PINK_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(conds_table)
    story.append(Spacer(1, 0.4 * cm))

    # Primary suspection detailed text
    story.append(Paragraph("Primary suspection details:", styles["label"]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph(_safe_text(assessment.get("explanation"), "No explanation available."), styles["body"]))
    story.append(Spacer(1, 0.4 * cm))

    # -- Recommended Specialist -----------------------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))
    story.append(Paragraph("Recommended Specialist", styles["section_header"]))

    doctor_data = [[
        Paragraph("Consult a:", styles["label"]),
        Paragraph(f"<b>{_safe_text(assessment.get('recommended_doctor'), 'General Physician')}</b>",
                  ParagraphStyle("DocName", fontSize=14, fontName="Helvetica-Bold",
                                 textColor=PINK)),
    ]]
    doc_table = Table(doctor_data, colWidths=[4 * cm, 13 * cm])
    doc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_PINK),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BOX",           (0, 0), (-1, -1), 1, PINK_BORDER),
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 0.4 * cm))

    # -- Health Advice --------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))
    story.append(Paragraph("Safe Home Care & Medical Guidance", styles["section_header"]))

    health_advice = _safe_text(assessment.get("health_advice"), "Please consult a healthcare professional.")
    for line in health_advice.split("\n"):
        line = line.strip()
        if line and not line.startswith("⚠"):
            story.append(Paragraph(line, styles["body"]))
            story.append(Spacer(1, 0.1 * cm))

    # -- Phase 3: Consultation Q&A History ------------------------------------
    conv_history = _safe_list(assessment.get("conversation_history"))
    follow_up_answers = _safe_dict(assessment.get("follow_up_answers"))
    if conv_history or follow_up_answers:
        story.append(Spacer(1, 0.4 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))
        story.append(Paragraph("Consultation Q&A History", styles["section_header"]))

        qa_data = [[Paragraph("<b>Question</b>", style_label), Paragraph("<b>Answer</b>", style_label)]]
        if follow_up_answers:
            for q, a in follow_up_answers.items():
                qa_data.append([
                    Paragraph(_safe_text(q), style_body),
                    Paragraph(_safe_text(a), style_body)
                ])
        elif conv_history:
            for i in range(0, len(conv_history) - 1, 2):
                q_msg = conv_history[i] if i < len(conv_history) else {}
                a_msg = conv_history[i + 1] if i + 1 < len(conv_history) else {}
                if q_msg.get("role") == "assistant" and a_msg.get("role") == "user":
                    qa_data.append([
                        Paragraph(_safe_text(q_msg.get("content")), style_body),
                        Paragraph(_safe_text(a_msg.get("content")), style_body)
                    ])
        if len(qa_data) > 1:
            qa_table = Table(qa_data, colWidths=[9 * cm, 8 * cm])
            qa_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT_PINK),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, PINK_BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_PINK]),
            ]))
            story.append(qa_table)
            story.append(Spacer(1, 0.4 * cm))

    # -- Phase 3: Top 5 Differential Diagnoses --------------------------------
    top5 = _safe_list(assessment.get("top5_conditions"))
    if top5:
        story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))
        story.append(Paragraph("Top 5 Differential Diagnoses", styles["section_header"]))

        top5_header = [
            Paragraph("<b>#</b>", style_label),
            Paragraph("<b>Condition</b>", style_label),
            Paragraph("<b>Probability</b>", style_label),
            Paragraph("<b>Severity</b>", style_label),
            Paragraph("<b>Matching Symptoms</b>", style_label),
        ]
        top5_data = [top5_header]
        for i, c in enumerate(_safe_list(top5)):
            cd = _safe_dict(c)
            sev = _safe_text(cd.get("severity"), "Moderate")
            top5_data.append([
                Paragraph(str(i + 1), style_body),
                Paragraph(f"<b>{_safe_text(cd.get('condition'), 'Unknown')}</b>", style_body),
                Paragraph(f"{_safe_text(cd.get('probability'), '0')}%", style_body),
                Paragraph(f"<font color='{_severity_color(sev)}'><b>{sev}</b></font>", style_body),
                Paragraph(_safe_text(cd.get("matching_symptoms"), "—"), style_body),
            ])
        top5_table = Table(top5_data, colWidths=[1 * cm, 5 * cm, 2.5 * cm, 2.5 * cm, 6 * cm])
        top5_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT_PINK),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, PINK_BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_PINK]),
        ]))
        story.append(top5_table)

        # Reasoning for each condition
        story.append(Spacer(1, 0.3 * cm))
        for i, c in enumerate(_safe_list(top5)):
            cd = _safe_dict(c)
            reasoning = _safe_text(cd.get("reasoning"), "")
            if reasoning:
                story.append(Paragraph(
                    f"<b>#{i+1} {_safe_text(cd.get('condition'))}:</b> {reasoning}",
                    ParagraphStyle("Reasoning", fontSize=9, fontName="Helvetica",
                                   leading=13, textColor=DARK, spaceAfter=4)
                ))
        story.append(Spacer(1, 0.4 * cm))

    # -- Phase 3: Recommended Specialist (if different from doctor) -----------
    specialist = _safe_text(assessment.get("recommended_specialist"), "")
    specialist_reason = _safe_text(assessment.get("specialist_reason"), "")
    if specialist and specialist != _safe_text(assessment.get("recommended_doctor"), ""):
        story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))
        story.append(Paragraph("Recommended Specialist (Triage)", styles["section_header"]))
        spec_data = [[
            Paragraph("Specialist:", styles["label"]),
            Paragraph(f"<b>{specialist}</b>",
                      ParagraphStyle("SpecName", fontSize=13, fontName="Helvetica-Bold", textColor=PINK)),
        ]]
        if specialist_reason:
            spec_data.append([
                Paragraph("Reason:", styles["label"]),
                Paragraph(specialist_reason, style_body),
            ])
        spec_table = Table(spec_data, colWidths=[4 * cm, 13 * cm])
        spec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_PINK),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 1, PINK_BORDER),
        ]))
        story.append(spec_table)
        story.append(Spacer(1, 0.4 * cm))

    # -- Medical Evidence Reference Sources -----------------------------------
    sources = _safe_list(assessment.get("evidence_sources")) or _safe_list(assessment.get("medical_references"))
    if sources:
        story.append(Spacer(1, 0.4 * cm))
        story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))
        story.append(Paragraph("Clinical Evidence & Grounded Sources", styles["section_header"]))
        
        for ev in sources:
            source_title = ev.get("source", "Reference")
            title_text = ev.get("title", "")
            url = ev.get("url", "")
            summary = ev.get("summary", "")
            
            ref_para = f"<b>{source_title}: {title_text}</b>"
            if url:
                ref_para += f" (Link: <font color='blue'><u><a href='{url}'>{url}</a></u></font>)"
            
            story.append(Paragraph(ref_para, ParagraphStyle("RefTitle", fontSize=9, fontName="Helvetica", leading=12, textColor=DARK)))
            if summary:
                story.append(Paragraph(summary, ParagraphStyle("RefSummary", fontSize=8, fontName="Helvetica-Oblique", leading=11, textColor=GREY)))
            story.append(Spacer(1, 0.15 * cm))

    # -- Disclaimer -----------------------------------------------------------
    story.append(Spacer(1, 0.5 * cm))
    disclaimer_text = (
        "MEDICAL DISCLAIMER: This report is generated by an AI system for informational "
        "purposes only. It does NOT constitute a medical diagnosis, treatment plan, or "
        "professional medical advice. Always consult a qualified and licensed healthcare "
        "professional for accurate diagnosis and appropriate treatment. In case of an emergency, "
        "please contact your local emergency services immediately."
    )
    disc_table = Table([[Paragraph(disclaimer_text, styles["disclaimer"])]],
                       colWidths=[17 * cm])
    disc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 1, YELLOW),
    ]))
    story.append(disc_table)

    # -- Footer ---------------------------------------------------------------
    story.append(Spacer(1, 0.5 * cm))
    footer_table = Table([[
        Paragraph(
            f"Generated by Clinical Intelligence Engine  |  {generated_at}  |  Not for clinical use",
            ParagraphStyle("Footer", fontSize=8, fontName="Helvetica",
                           textColor=GREY, alignment=TA_CENTER),
        )
    ]], colWidths=[17 * cm])
    footer_table.setStyle(TableStyle([
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("LINEABOVE",   (0, 0), (-1, -1), 0.5, PINK_BORDER),
    ]))
    story.append(footer_table)

    doc.build(story)
    return buffer.getvalue()
