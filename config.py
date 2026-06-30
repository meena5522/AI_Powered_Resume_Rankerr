import os

class Config:
    """Application configuration class."""
    # Flask Secret Key for Session Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_resume_ranker_2026_xyz')
    
    # Base directory of the project
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database configuration
    DATABASE = os.path.join(BASE_DIR, 'resume_ranker.db')
    
    # Upload and Report directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')
    CHARTS_FOLDER = os.path.join(BASE_DIR, 'static', 'charts')
    
    # File upload configurations
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
