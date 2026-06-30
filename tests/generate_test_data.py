import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def create_resume_pdf(filename: str, name: str, details: str, skills: list, experience: str) -> str:
    """Generates a professional single-page PDF resume using ReportLab."""
    pdf_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    
    name_style = ParagraphStyle(
        name='NameStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=5
    )
    
    section_style = ParagraphStyle(
        name='SectionStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#4f46e5'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        name='BodyStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    story = []
    story.append(Paragraph(name, name_style))
    story.append(Paragraph(details, body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Technical Skills Summary", section_style))
    skills_text = ", ".join(skills)
    story.append(Paragraph(skills_text, body_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Professional Experience", section_style))
    story.append(Paragraph(experience, body_style))
    
    doc.build(story)
    return pdf_path

def generate_samples():
    """Generates three distinct candidate resumes in the uploads directory."""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    candidates = [
        {
            "filename": "John_Doe_Resume.pdf",
            "name": "John Doe",
            "details": "Email: john.doe@email.com | Phone: 555-0199 | Github: github.com/johndoe",
            "skills": ["Python", "Flask", "SQL", "PostgreSQL", "Git", "Docker", "REST API", "Unit Testing", "OOP"],
            "experience": "Senior Backend Developer at TechCorp. Responsible for designing scalable web services using Python, Flask, and PostgreSQL. Built microservices packaged with Docker containers. Set up CI/CD workflows and automated unit testing modules. Collaborated using Git versioning tools."
        },
        {
            "filename": "Jane_Smith_Resume.pdf",
            "name": "Jane Smith",
            "details": "Email: smith.jane@email.com | Portfolio: janesmith.dev | LinkedIn: linkedin.com/in/janesmith",
            "skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Tailwind", "Next.js", "Bootstrap", "Git"],
            "experience": "Frontend Engineer at DesignStudio. Developed responsive user interfaces using HTML, CSS, JavaScript, React, and Bootstrap. Experienced with Tailwind CSS styling and headless Next.js layouts. Implemented visual animations and verified responsive rendering across mobile browsers."
        },
        {
            "filename": "Bob_Johnson_Resume.pdf",
            "name": "Bob Johnson",
            "details": "Email: bob.johnson@email.com | Phone: 555-0144",
            "skills": ["Java", "Spring", "SQL", "MySQL", "Agile", "Scrum", "Project Management", "Jira"],
            "experience": "Project Manager and Generalist at SystemSolutions. Managed development sprints utilizing Agile and Scrum methodologies. Experienced in database administration with SQL and MySQL servers. Developed basic internal helper microservices in Java and Spring framework."
        }
    ]
    
    print("Generating sample candidate PDF resumes in uploads/ ...")
    for cand in candidates:
        path = create_resume_pdf(cand["filename"], cand["name"], cand["details"], cand["skills"], cand["experience"])
        print(f"Created: {path}")

if __name__ == '__main__':
    generate_samples()
