from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_feedback_report_pdf(lecturer, feedback_list, stats):
    """Generate a comprehensive feedback report PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#6a11cb'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(f"Feedback Report - {lecturer.get_full_name()}", title_style)
    elements.append(title)
    
    # Report Info
    report_info = Paragraph(
        f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}<br/>"
        f"<b>Department:</b> {lecturer.department or 'N/A'}<br/>"
        f"<b>Total Feedback:</b> {len(feedback_list)}",
        styles['Normal']
    )
    elements.append(report_info)
    elements.append(Spacer(1, 0.3*inch))
    
    # Statistics Summary
    elements.append(Paragraph("📊 Overall Statistics", heading_style))
    
    stats_data = [
        ['Metric', 'Rating'],
        ['Overall Rating', f"{stats.get('avg_rating', 0):.2f} / 5.00"],
        ['Teaching Quality', f"{stats.get('avg_teaching', 0):.2f} / 5.00"],
        ['Communication', f"{stats.get('avg_communication', 0):.2f} / 5.00"],
        ['Student Engagement', f"{stats.get('avg_engagement', 0):.2f} / 5.00"],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Feedback Details
    if feedback_list:
        elements.append(Paragraph("💬 Detailed Feedback", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        for idx, fb in enumerate(feedback_list, 1):
            # Feedback header
            fb_header = Paragraph(
                f"<b>Feedback #{idx}</b> - {fb.course.code}: {fb.course.name}",
                styles['Heading3']
            )
            elements.append(fb_header)
            
            # Ratings
            ratings_text = f"<b>Overall:</b> {fb.rating}/5"
            if fb.teaching_rating:
                ratings_text += f" | <b>Teaching:</b> {fb.teaching_rating}/5"
            if fb.communication_rating:
                ratings_text += f" | <b>Communication:</b> {fb.communication_rating}/5"
            if fb.engagement_rating:
                ratings_text += f" | <b>Engagement:</b> {fb.engagement_rating}/5"
            
            if hasattr(fb, 'sentiment') and fb.sentiment:
                sentiment_emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😟'}
                ratings_text += f" | <b>Sentiment:</b> {sentiment_emoji.get(fb.sentiment, '')} {fb.sentiment.title()}"
            
            ratings_para = Paragraph(ratings_text, styles['Normal'])
            elements.append(ratings_para)
            
            # Comment
            if fb.comment:
                comment_style = ParagraphStyle(
                    'Comment',
                    parent=styles['Normal'],
                    leftIndent=20,
                    rightIndent=20,
                    spaceAfter=10,
                    borderColor=colors.HexColor('#e0e0e0'),
                    borderWidth=1,
                    borderPadding=10,
                    backColor=colors.HexColor('#f8f9fa')
                )
                comment = Paragraph(f"<i>\"{fb.comment}\"</i>", comment_style)
                elements.append(Spacer(1, 0.1*inch))
                elements.append(comment)
            
            # Date
            date_para = Paragraph(
                f"<i>Submitted: {fb.created_at.strftime('%B %d, %Y')}</i>",
                styles['Normal']
            )
            elements.append(date_para)
            elements.append(Spacer(1, 0.3*inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer