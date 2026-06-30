import csv
import os
import logging
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_csv_report(job_title: str, rankings: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generates a CSV report summarizing resume rankings for a job description.
    
    Args:
        job_title (str): Job description title.
        rankings (List[Dict]): List of candidates rankings data.
        output_path (str): File destination path.
    """
    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write Header Info
            writer.writerow(["Job Position", job_title])
            writer.writerow([])
            # Table Headers
            writer.writerow(["Rank", "Candidate Name", "Score (%)", "Recommendation", "Matching Skills", "Missing Skills"])
            
            # Rows
            for idx, candidate in enumerate(rankings, 1):
                writer.writerow([
                    idx,
                    candidate.get("candidate_name"),
                    f"{candidate.get('score'):.2f}%",
                    candidate.get("recommendation"),
                    candidate.get("matching_skills"),
                    candidate.get("missing_skills")
                ])
                
        logger.info(f"Successfully generated CSV report at: {output_path}")
    except Exception as e:
        logger.error(f"Error generating CSV report: {e}")
        raise

def generate_pdf_report(job_title: str, job_desc: str, rankings: List[Dict[str, Any]], output_path: str) -> None:
    """
    Generates a professional PDF report containing the ranked candidates table.
    
    Args:
        job_title (str): Job description title.
        job_desc (str): Full text of the Job Description.
        rankings (List[Dict]): List of candidate ranking records.
        output_path (str): Destination file path.
    """
    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build ReportLab Document
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles to prevent overlapping and allow line wraps
        title_style = ParagraphStyle(
            name='DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=15,
            alignment=TA_LEFT
        )
        
        subtitle_style = ParagraphStyle(
            name='DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=25
        )
        
        section_heading = ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15
        )
        
        body_style = ParagraphStyle(
            name='Body',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=9.5,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8
        )
        
        table_text_style = ParagraphStyle(
            name='TableText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            textColor=colors.HexColor('#2c3e50')
        )
        
        table_header_style = ParagraphStyle(
            name='TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.white
        )

        elements = []
        
        # Title Block
        elements.append(Paragraph("Candidate Ranking Report", title_style))
        elements.append(Paragraph(f"<b>Job Position:</b> {job_title} | <b>Generated on:</b> 2026-06-28", subtitle_style))
        
        # Summary description
        short_desc = job_desc[:250] + "..." if len(job_desc) > 250 else job_desc
        elements.append(Paragraph("Job Description Summary", section_heading))
        elements.append(Paragraph(short_desc, body_style))
        elements.append(Spacer(1, 10))
        
        # Candidate table title
        elements.append(Paragraph("Ranked Candidates Table", section_heading))
        
        # Build Table Data
        # Column Headers: Rank, Name, Score, Recommendation, Skills (Match/Missing)
        # Note: ReportLab cells should wrap using Paragraph to avoid horizontal overflow
        table_data = [[
            Paragraph("Rank", table_header_style),
            Paragraph("Candidate Name", table_header_style),
            Paragraph("Score (%)", table_header_style),
            Paragraph("Status", table_header_style),
            Paragraph("Matching Skills", table_header_style),
            Paragraph("Missing Skills", table_header_style)
        ]]
        
        for idx, candidate in enumerate(rankings, 1):
            matching_s = candidate.get("matching_skills", "")
            missing_s = candidate.get("missing_skills", "")
            
            table_data.append([
                Paragraph(str(idx), table_text_style),
                Paragraph(candidate.get("candidate_name", "N/A"), table_text_style),
                Paragraph(f"{candidate.get('score'):.2f}%", table_text_style),
                Paragraph(candidate.get("recommendation", "N/A"), table_text_style),
                Paragraph(matching_s.replace(",", ", "), table_text_style),
                Paragraph(missing_s.replace(",", ", "), table_text_style)
            ])
            
        # Table Styling
        # Table dimensions (Total printable width = Letter width (612) - Margins (80) = 532)
        # Allocate: Rank (32), Name (100), Score (60), Recommendation (100), Matching (120), Missing (120)
        col_widths = [32, 100, 60, 100, 120, 120]
        
        rankings_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        rankings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(rankings_table)
        
        # Build document
        doc.build(elements)
        logger.info(f"Successfully generated PDF report at: {output_path}")
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise
