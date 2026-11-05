"""Report generator service to export assessment audit reports into PDF format."""
import io
from typing import Any, Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_pdf_report(session_id: str, target_role: str, evaluations: List[Dict[str, Any]]) -> bytes:
    """Generate printable evaluation PDF report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
    )
    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
    )
    bold_label_style = ParagraphStyle(
        "BoldLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # Title Banner
    story.append(Paragraph("EXECUTIVE PERFORMANCE AUDIT REPORT", title_style))
    story.append(Paragraph(f"Target Role: {target_role} | Session ID: {session_id}", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=14))

    # Aggregates
    if evaluations:
        avg_tech = sum(e.get("technical_accuracy_score", 0.0) for e in evaluations) / len(evaluations)
        avg_comm = sum(e.get("communication_clarity_score", 0.0) for e in evaluations) / len(evaluations)
        composite = round(((avg_tech * 0.6) + (avg_comm * 0.4)) * 10, 1)

        summary_data = [
            [
                Paragraph("<b>Composite Index</b>", subtitle_style),
                Paragraph("<b>Technical Mastery</b>", subtitle_style),
                Paragraph("<b>Communication Index</b>", subtitle_style),
            ],
            [
                Paragraph(f"<font size=16 color='#0f172a'><b>{composite} / 100</b></font>", body_style),
                Paragraph(f"<font size=16 color='#0f172a'><b>{round(avg_tech, 1)} / 10</b></font>", body_style),
                Paragraph(f"<font size=16 color='#0f172a'><b>{round(avg_comm, 1)} / 10</b></font>", body_style),
            ],
        ]
        table = Table(summary_data, colWidths=[175, 175, 175])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(table)
        story.append(Spacer(1, 16))

    # Turn-by-Turn Breakdown
    story.append(Paragraph("TURN-BY-TURN TECHNICAL AUDIT", h2_style))

    for idx, ev in enumerate(evaluations, start=1):
        q_text = ev.get("question", "")
        a_text = ev.get("candidate_answer", "")
        tech_score = ev.get("technical_accuracy_score", 0.0)
        comm_score = ev.get("communication_clarity_score", 0.0)
        strengths = ", ".join(ev.get("key_strengths", []))
        deficits = ", ".join(ev.get("critical_deficits", []))
        ideal = ev.get("suggested_ideal_response", "")

        story.append(Paragraph(f"<b>Turn {idx}: {q_text}</b>", bold_label_style))
        story.append(Paragraph(f"<b>Candidate Answer:</b> {a_text}", body_style))
        story.append(Paragraph(f"<b>Scores:</b> Technical: {tech_score}/10 | Communication: {comm_score}/10", subtitle_style))
        story.append(Paragraph(f"<b>Identified Strengths:</b> {strengths}", body_style))
        story.append(Paragraph(f"<b>Critical Deficits:</b> {deficits}", body_style))
        story.append(Paragraph(f"<b>Benchmarked Ideal Response:</b> {ideal}", body_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#f1f5f9"), spaceAfter=8))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
