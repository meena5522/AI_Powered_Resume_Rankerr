import sqlite3
import os
from typing import List, Dict, Any, Optional
from config import Config

def get_db_connection() -> sqlite3.Connection:
    """Establish a connection to the SQLite database with Row factory enabled."""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db() -> None:
    """Initialize the database schema if tables do not exist."""
    # Ensure database folder exists
    db_dir = os.path.dirname(Config.DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    schema = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        skills TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        extracted_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_description_id INTEGER NOT NULL,
        resume_id INTEGER NOT NULL,
        score REAL NOT NULL,
        matching_skills TEXT NOT NULL,
        missing_skills TEXT NOT NULL,
        summary TEXT NOT NULL,
        recommendation TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE,
        FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_description_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        report_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_description_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
    );
    """
    with get_db_connection() as conn:
        conn.executescript(schema)
        conn.commit()

# --- User Table CRUD ---

def create_user(username: str, email: str, password_hash: str) -> Optional[int]:
    """Create a new user and return the inserted user's ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None

def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    """Retrieve user details by username."""
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    """Retrieve user details by email."""
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    """Retrieve user details by ID."""
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

def update_user_profile(user_id: int, username: str, email: str) -> bool:
    """Update username and email of a user."""
    try:
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE users SET username = ?, email = ? WHERE id = ?",
                (username, email, user_id)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def update_user_password(user_id: int, password_hash: str) -> bool:
    """Update a user's password hash."""
    with get_db_connection() as conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
        conn.commit()
        return True

# --- Job Description Table CRUD ---

def create_job_description(title: str, description: str, skills: str) -> int:
    """Insert a new job description."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO job_descriptions (title, description, skills) VALUES (?, ?, ?)",
            (title, description, skills)
        )
        conn.commit()
        return cursor.lastrowid

def get_job_description(jd_id: int) -> Optional[sqlite3.Row]:
    """Retrieve a job description by ID."""
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM job_descriptions WHERE id = ?", (jd_id,)).fetchone()

def get_all_job_descriptions() -> List[sqlite3.Row]:
    """Retrieve all job descriptions sorted by creation date."""
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM job_descriptions ORDER BY created_at DESC").fetchall()

def delete_job_description(jd_id: int) -> None:
    """Delete a job description and cascade changes."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM job_descriptions WHERE id = ?", (jd_id,))
        conn.commit()

# --- Resume Table CRUD ---

def create_resume(candidate_name: str, filename: str, file_path: str, extracted_text: str) -> int:
    """Insert a new resume record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO resumes (candidate_name, filename, file_path, extracted_text) VALUES (?, ?, ?, ?)",
            (candidate_name, filename, file_path, extracted_text)
        )
        conn.commit()
        return cursor.lastrowid

def get_resume(resume_id: int) -> Optional[sqlite3.Row]:
    """Retrieve a resume record by ID."""
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()

def get_all_resumes() -> List[sqlite3.Row]:
    """Retrieve all resumes sorted by creation date."""
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM resumes ORDER BY created_at DESC").fetchall()

def delete_resume(resume_id: int) -> None:
    """Delete a resume record, which will also delete associated files and database entries."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
        conn.commit()

# --- Rankings Table CRUD ---

def create_ranking(job_description_id: int, resume_id: int, score: float, 
                   matching_skills: str, missing_skills: str, summary: str, recommendation: str) -> int:
    """Insert or update a resume ranking score for a specific job description."""
    with get_db_connection() as conn:
        # Check if ranking already exists for this resume and job description
        existing = conn.execute(
            "SELECT id FROM rankings WHERE job_description_id = ? AND resume_id = ?",
            (job_description_id, resume_id)
        ).fetchone()
        
        cursor = conn.cursor()
        if existing:
            cursor.execute(
                """UPDATE rankings 
                   SET score = ?, matching_skills = ?, missing_skills = ?, summary = ?, recommendation = ?, created_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (score, matching_skills, missing_skills, summary, recommendation, existing['id'])
            )
            conn.commit()
            return existing['id']
        else:
            cursor.execute(
                """INSERT INTO rankings 
                   (job_description_id, resume_id, score, matching_skills, missing_skills, summary, recommendation) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (job_description_id, resume_id, score, matching_skills, missing_skills, summary, recommendation)
            )
            conn.commit()
            return cursor.lastrowid

def get_rankings_for_job(job_description_id: int) -> List[sqlite3.Row]:
    """Retrieve all rankings for a specific job, ordered by score descending."""
    query = """
        SELECT r.id as ranking_id, r.score, r.matching_skills, r.missing_skills, r.summary, r.recommendation, r.created_at,
               res.id as resume_id, res.candidate_name, res.filename, res.file_path, res.extracted_text
        FROM rankings r
        JOIN resumes res ON r.resume_id = res.id
        WHERE r.job_description_id = ?
        ORDER BY r.score DESC, res.candidate_name ASC
    """
    with get_db_connection() as conn:
        return conn.execute(query, (job_description_id,)).fetchall()

def get_recent_rankings(limit: int = 5) -> List[sqlite3.Row]:
    """Retrieve the most recent rankings across all job descriptions."""
    query = """
        SELECT r.id as ranking_id, r.score, r.recommendation, r.created_at,
               res.candidate_name, jd.title as job_title
        FROM rankings r
        JOIN resumes res ON r.resume_id = res.id
        JOIN job_descriptions jd ON r.job_description_id = jd.id
        ORDER BY r.created_at DESC
        LIMIT ?
    """
    with get_db_connection() as conn:
        return conn.execute(query, (limit,)).fetchall()

def delete_rankings_for_job(job_description_id: int) -> None:
    """Clear all rankings for a job description."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM rankings WHERE job_description_id = ?", (job_description_id,))
        conn.commit()

# --- Reports Table CRUD ---

def create_report(job_description_id: int, filename: str, file_path: str, report_type: str) -> int:
    """Insert a record for a generated report."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reports (job_description_id, filename, file_path, report_type) VALUES (?, ?, ?, ?)",
            (job_description_id, filename, file_path, report_type)
        )
        conn.commit()
        return cursor.lastrowid

def get_reports_for_job(job_description_id: int) -> List[sqlite3.Row]:
    """Retrieve all generated reports for a specific job."""
    with get_db_connection() as conn:
        return conn.execute(
            "SELECT * FROM reports WHERE job_description_id = ? ORDER BY created_at DESC", 
            (job_description_id,)
        ).fetchall()

def get_all_reports() -> List[sqlite3.Row]:
    """Retrieve all generated reports with job title context."""
    query = """
        SELECT r.*, jd.title as job_title
        FROM reports r
        JOIN job_descriptions jd ON r.job_description_id = jd.id
        ORDER BY r.created_at DESC
    """
    with get_db_connection() as conn:
        return conn.execute(query).fetchall()

# --- Dashboard Stats Analytics ---

def get_dashboard_stats() -> Dict[str, Any]:
    """Retrieve overall stats to display in dashboard cards."""
    stats = {
        "total_resumes": 0,
        "total_jds": 0,
        "total_rankings": 0,
        "highest_score": 0.0,
        "average_score": 0.0,
        "recent_resumes": []
    }
    
    with get_db_connection() as conn:
        # Total counts
        stats["total_resumes"] = conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
        stats["total_jds"] = conn.execute("SELECT COUNT(*) FROM job_descriptions").fetchone()[0]
        stats["total_rankings"] = conn.execute("SELECT COUNT(*) FROM rankings").fetchone()[0]
        
        # Score stats
        scores = conn.execute("SELECT score FROM rankings").fetchall()
        if scores:
            scores_list = [row["score"] for row in scores]
            stats["highest_score"] = max(scores_list)
            stats["average_score"] = sum(scores_list) / len(scores_list)
            
        # Recent resumes
        stats["recent_resumes"] = conn.execute(
            "SELECT id, candidate_name, filename, created_at FROM resumes ORDER BY created_at DESC LIMIT 5"
        ).fetchall()
        
    return stats
