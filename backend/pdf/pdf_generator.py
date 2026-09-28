from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import os
from datetime import datetime

PDF_DIR = "pdf"

# Ensure directory exists
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

def generate_pdf(report_type: str, summary: str, details: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_type}_{timestamp}.pdf"
    path = os.path.join(PDF_DIR, filename)

    # Create PDF
    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=40
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=22,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor("#00e5ff")
    )

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#00e5ff"),
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalText",
        parent=styles["BodyText"],
        fontSize=11,
        leading=15
    )

    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["BodyText"],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )

    content = []

    # Title
    content.append(Paragraph("CommandOS — PDF Report", title_style))
    content.append(Spacer(1, 12))

    # Horizontal line
    content.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    content.append(Spacer(1, 14))

    # Report Type
    content.append(Paragraph("Report Type", header_style))
    content.append(Paragraph(report_type, normal_style))
    content.append(Spacer(1, 12))

    # Summary
    content.append(Paragraph("Summary", header_style))
    content.append(Paragraph(summary.replace("\n", "<br/>"), normal_style))
    content.append(Spacer(1, 12))

    # Details
    content.append(Paragraph("Details", header_style))
    content.append(Paragraph(details.replace("\n", "<br/>"), normal_style))
    content.append(Spacer(1, 20))

    # Footer
    footer_text = f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
    content.append(HRFlowable(width="40%", thickness=0.7, color=colors.grey))
    content.append(Spacer(1, 6))
    content.append(Paragraph(footer_text, footer_style))

    # Build PDF
    doc.build(content)

    return filename
