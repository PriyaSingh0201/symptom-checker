# utils/pdf_generator.py – Professional medical PDF reports using ReportLab
from io import BytesIO
from datetime import datetime

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
    meta_data = [[
        "Report ID:", f"CLN-{assessment['id']:04d}",
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

    patient_data = [
        [Paragraph("Full Name", style_label), Paragraph(user["fullname"], style_body),
         Paragraph("Email", style_label), Paragraph(user["email"], style_body)],
         
        [Paragraph("Age", style_label), Paragraph(str(assessment["age"]), style_body),
         Paragraph("Gender", style_label), Paragraph(assessment["gender"].capitalize(), style_body)],
         
        [Paragraph("Symptom Duration", style_label), Paragraph(assessment["duration"], style_body),
         Paragraph("Assessment Date", style_label), Paragraph(assessment["created_date"], style_body)],
         
        [Paragraph("Height / Weight", style_label), Paragraph(f"{assessment.get('height') or 'N/A'} / {assessment.get('weight') or 'N/A'}", style_body),
         Paragraph("Blood Pressure", style_label), Paragraph(assessment.get("blood_pressure") or "N/A", style_body)],
         
        [Paragraph("Temp / Pain Level", style_label), Paragraph(f"{assessment.get('body_temperature')}°F / Pain: {assessment.get('pain_level')}/10", style_body),
         Paragraph("Pregnancy Status", style_label), Paragraph(assessment.get("pregnancy_status") or "N/A", style_body)],
         
        [Paragraph("Medications", style_label), Paragraph(assessment.get("medications") or "None", style_body),
         Paragraph("Allergies", style_label), Paragraph(assessment.get("allergies") or "None", style_body)],
         
        [Paragraph("Existing Conditions", style_label), Paragraph(assessment["medical_conditions"] or "None", style_body),
         Paragraph("Smoking / Alcohol", style_label), Paragraph(f"{assessment.get('smoking_status') or 'N/A'} / {assessment.get('alcohol_consumption') or 'N/A'}", style_body)]
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
    story.append(Paragraph(assessment["symptoms"], styles["body"]))
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
    
    for c in assessment.get("top_conditions", []):
        sev_col = _severity_color(c["severity"])
        conds_table_data.append([
            Paragraph(f"<b>{c['condition']}</b>", style_body),
            Paragraph(f"{c['confidence']}%", style_body),
            Paragraph(f"<font color='{sev_col}'><b>{c['severity']}</b></font>", style_body),
            Paragraph(c.get('recommended_department', 'General Physician'), style_body)
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
    story.append(Paragraph(assessment["explanation"], styles["body"]))
    story.append(Spacer(1, 0.4 * cm))

    # -- Recommended Specialist -----------------------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=PINK_BORDER))
    story.append(Paragraph("Recommended Specialist", styles["section_header"]))

    doctor_data = [[
        Paragraph("Consult a:", styles["label"]),
        Paragraph(f"<b>{assessment['recommended_doctor']}</b>",
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

    for line in assessment["health_advice"].split("\n"):
        line = line.strip()
        if line and not line.startswith("⚠"):
            story.append(Paragraph(line, styles["body"]))
            story.append(Spacer(1, 0.1 * cm))

    # -- Medical Evidence Reference Sources -----------------------------------
    sources = assessment.get("evidence_sources", [])
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
