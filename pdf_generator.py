from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import os
import tempfile

def create_pdf(itinerary_data, destination, duration, budget, interests, party_size):
    """Create a PDF file from the itinerary data"""
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    temp_file.close()
    
    # Create the PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles with text wrapping
    title_style = styles['Heading1']
    heading2_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add text wrapping to normal style
    wrapped_style = ParagraphStyle(
        'WrappedStyle',
        parent=normal_style,
        spaceBefore=6,
        spaceAfter=6
    )
    
    # Create the content
    content = []
    
    # Title
    content.append(Paragraph(f"Travel Itinerary: {destination}", title_style))
    content.append(Spacer(1, 0.25*inch))
    
    # Trip details
    content.append(Paragraph(f"Duration: {duration} days", wrapped_style))
    content.append(Paragraph(f"Budget: {budget}", wrapped_style))
    content.append(Paragraph(f"Interests: {interests}", wrapped_style))
    content.append(Paragraph(f"Party Size: {party_size}", wrapped_style))
    content.append(Spacer(1, 0.25*inch))
    
    # Daily plans
    content.append(Paragraph("Daily Itinerary", heading2_style))
    content.append(Spacer(1, 0.1*inch))
    
    for day in itinerary_data['daily_plans']:
        content.append(Paragraph(f"Day {day['day']}", styles['Heading3']))
        
        # Create a table for activities
        data = [["Time", "Activity", "Category", "Cost"]]
        
        for activity in day['activities']:
            # Ensure text wrapping for description
            description = Paragraph(activity['description'], wrapped_style)
            data.append([
                activity['time'],
                description,
                activity['category'],
                f"${activity['estimated_cost']}"
            ])
        
        # Create the table with appropriate column widths
        table = Table(data, colWidths=[0.8*inch, 3.5*inch, 1.2*inch, 0.8*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Allow text wrapping in the description column
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 0.2*inch))
    
    # Budget breakdown
    content.append(Paragraph("Budget Breakdown", heading2_style))
    content.append(Spacer(1, 0.1*inch))
    
    budget_data = [["Category", "Amount"]]
    for category, amount in itinerary_data['budget_breakdown'].items():
        budget_data.append([category, f"${amount}"])
    
    budget_table = Table(budget_data, colWidths=[3*inch, 1.5*inch])
    budget_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Highlight the total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    content.append(budget_table)
    content.append(Spacer(1, 0.2*inch))
    
    # Tips
    content.append(Paragraph("Travel Tips", heading2_style))
    content.append(Spacer(1, 0.1*inch))
    
    for tip in itinerary_data['tips']:
        content.append(Paragraph(f"• {tip}", wrapped_style))
    
    # Build the PDF
    doc.build(content)
    
    return pdf_path
