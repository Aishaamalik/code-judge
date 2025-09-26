import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import re

def export_to_json(analysis_result: str, metrics: dict, filename: str):
    """
    Export analysis result and metrics to a JSON file.
    """
    data = {
        "analysis": analysis_result,
        "metrics": metrics
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def export_to_pdf(analysis_result: str, metrics: dict, filename: str):
    """
    Export analysis result and metrics to a PDF file using ReportLab.
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(name='Title', fontSize=18, spaceAfter=20, alignment=1)
    story.append(Paragraph("AI Code Analysis Report", title_style))
    story.append(Spacer(1, 12))

    # Metrics Section
    story.append(Paragraph("Code Metrics", styles['Heading2']))
    metric_data = [["Metric", "Value", "Status"]]
    for key, value in metrics.items():
        if isinstance(value, dict):
            metric_data.append([value.get('label', key), str(value.get('value', '')), value.get('status', '')])
        else:
            metric_data.append([key, str(value), ""])
    table = Table(metric_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Analysis Sections
    sections = re.split(r'###\s+', analysis_result)
    for section in sections[1:]:  # Skip empty first part
        lines = section.split('\n', 1)
        if lines:
            header = lines[0].strip()
            content = lines[1] if len(lines) > 1 else ""
            story.append(Paragraph(header, styles['Heading3']))
            story.append(Paragraph(content.replace('\n', '<br/>'), styles['Normal']))
            story.append(Spacer(1, 12))

    doc.build(story)
