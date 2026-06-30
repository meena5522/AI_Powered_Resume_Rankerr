import os
import sys
import random
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Force Matplotlib to use a non-interactive backend (Agg) for thread safety inside Flask
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import Config
from models import database as db
from utils import pdf_parser, nlp, report_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Ensure required directories exist
for folder in [Config.UPLOAD_FOLDER, Config.REPORT_FOLDER, Config.CHARTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Initialize database schema before requests
with app.app_context():
    db.init_db()

# --- Helper Utilities ---

def allowed_file(filename: str) -> bool:
    """Check if uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def clean_candidate_name(text: str, filename: str) -> str:
    """
    Deduce a candidate's name from resume content or file name.
    """
    # 1. Try to search text for a name (First line check)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        first_line = lines[0]
        # Standard names have 2 to 3 words, are short, and alphabet-oriented
        words = first_line.split()
        if len(words) >= 2 and len(words) <= 4 and all(w.isalpha() for w in words) and len(first_line) < 30:
            return first_line
            
    # 2. Fallback to parsing filename
    base = os.path.splitext(filename)[0]
    # Replace separators with spaces
    base = base.replace('_', ' ').replace('-', ' ')
    # Filter common resume terms
    base = base.lower().replace('resume', '').replace('cv', '').strip()
    return base.title() if base else "Candidate"

def generate_matplotlib_charts(rankings: list) -> None:
    """
    Generate and save evaluation metrics using matplotlib.
    """
    if not rankings:
        return
        
    scores = [r['score'] for r in rankings]
    
    # 1. Histogram of Similarity Scores
    plt.figure(figsize=(4.5, 3.2))
    plt.hist(scores, bins=6, range=(0, 100), color='#6366f1', edgecolor='white', alpha=0.85)
    plt.title('Similarity Score Distribution', fontsize=11, fontweight='bold', pad=10, color='#1e293b')
    plt.xlabel('Score (%)', fontsize=9, color='#475569')
    plt.ylabel('Candidates', fontsize=9, color='#475569')
    plt.grid(True, linestyle='--', alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(Config.CHARTS_FOLDER, 'score_distribution.png'), dpi=150)
    plt.close()
    
    # 2. Donut/Pie Chart of Recommendation Statuses
    recs = [r['recommendation'] for r in rankings]
    categories = ['Highly Recommended', 'Recommended', 'Consider', 'Not Recommended']
    counts = [recs.count(c) for c in categories]
    
    labels_filtered = [c for c, count in zip(categories, counts) if count > 0]
    counts_filtered = [count for count in counts if count > 0]
    
    plt.figure(figsize=(4.5, 3.2))
    if counts_filtered:
        colors_map = {
            'Highly Recommended': '#10b981',
            'Recommended': '#38bdf8',
            'Consider': '#fbbf24',
            'Not Recommended': '#f87171'
        }
        pie_colors = [colors_map[l] for l in labels_filtered]
        plt.pie(
            counts_filtered, 
            labels=labels_filtered, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=pie_colors,
            textprops={'fontsize': 8, 'weight': 'bold', 'color': '#0f172a'},
            wedgeprops={'width': 0.6, 'edgecolor': 'white'}
        )
    else:
        plt.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center')
        
    plt.title('Recommendation Breakdown', fontsize=11, fontweight='bold', pad=10, color='#1e293b')
    plt.tight_layout()
    plt.savefig(os.path.join(Config.CHARTS_FOLDER, 'recommendation_distribution.png'), dpi=150)
    plt.close()

# --- Auth Middlewares ---

@app.before_request
def require_login() -> None:
    """Protect routes, redirecting unauthenticated traffic to /login."""
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint and request.endpoint not in allowed_routes:
        if 'user_id' not in session:
            return redirect(url_for('login'))

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template('register.html')
            
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template('register.html')
            
        if db.get_user_by_username(username):
            flash("Username already exists.", "error")
            return render_template('register.html')
            
        if db.get_user_by_email(email):
            flash("Email address already registered.", "error")
            return render_template('register.html')
            
        password_hash = generate_password_hash(password)
        user_id = db.create_user(username, email, password_hash)
        if user_id:
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Internal error creating user.", "error")
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = db.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Successfully logged out.", "success")
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = db.get_user_by_id(session['user_id'])
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'profile':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            
            if not username or not email:
                flash("Fields cannot be empty.", "error")
            else:
                success = db.update_user_profile(user['id'], username, email)
                if success:
                    session['username'] = username
                    flash("Profile updated successfully.", "success")
                    return redirect(url_for('profile'))
                else:
                    flash("Username or Email already in use.", "error")
                    
        elif form_type == 'password':
            curr_pass = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            conf_pass = request.form.get('confirm_password', '')
            
            if not check_password_hash(user['password_hash'], curr_pass):
                flash("Incorrect current password.", "error")
            elif new_pass != conf_pass:
                flash("New passwords do not match.", "error")
            elif len(new_pass) < 8:
                flash("New password must be at least 8 characters.", "error")
            else:
                hashed = generate_password_hash(new_pass)
                db.update_user_password(user['id'], hashed)
                flash("Password updated successfully.", "success")
                return redirect(url_for('profile'))
                
    return render_template('profile.html', user=user, active_page='profile')

@app.route('/dashboard')
def dashboard():
    stats = db.get_dashboard_stats()
    recent_rankings = db.get_recent_rankings(5)
    
    # Check if visualization charts exist
    charts_exist = os.path.exists(os.path.join(Config.CHARTS_FOLDER, 'score_distribution.png')) and \
                   os.path.exists(os.path.join(Config.CHARTS_FOLDER, 'recommendation_distribution.png'))
                   
    return render_template(
        'dashboard.html', 
        stats=stats, 
        recent_rankings=recent_rankings, 
        charts_exist=charts_exist,
        cache_buster=random.randint(1, 100000),
        active_page='dashboard'
    )

@app.route('/job-descriptions', methods=['GET', 'POST'])
def job_descriptions():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title or not description:
            flash("Job title and description are required.", "error")
        else:
            try:
                # Preprocess text and pull matches against common tech vocabulary
                skills_list = nlp.extract_skills(description)
                skills_str = ",".join(skills_list)
                
                db.create_job_description(title, description, skills_str)
                flash("Job description added and analyzed successfully.", "success")
                return redirect(url_for('job_descriptions'))
            except Exception as e:
                logger.error(f"Error creating job description: {e}")
                flash("An error occurred analyzing the job description.", "error")
                
    jds = db.get_all_job_descriptions()
    return render_template('job_descriptions.html', jds=jds, active_page='job_descriptions')

@app.route('/job-descriptions/delete/<int:jd_id>', methods=['POST'])
def delete_job_description(jd_id: int):
    try:
        db.delete_job_description(jd_id)
        flash("Job description deleted successfully.", "success")
    except Exception as e:
        logger.error(f"Error deleting job description: {e}")
        flash("Failed to delete job description.", "error")
    return redirect(url_for('job_descriptions'))

@app.route('/resumes', methods=['GET', 'POST'])
def resumes():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('resumes')
        
        if not uploaded_files or uploaded_files[0].filename == '':
            flash("No files selected for upload.", "error")
            return redirect(url_for('resumes'))
            
        success_count = 0
        error_messages = []
        
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Avoid duplicate names by prefixing a random token if duplicate encountered
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                if os.path.exists(file_path):
                    filename = f"{random.randint(1000, 9999)}_{filename}"
                    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                    
                try:
                    file.save(file_path)
                    
                    # Run text extraction using PyPDF2
                    extracted_text = pdf_parser.extract_text_from_pdf(file_path)
                    candidate_name = clean_candidate_name(extracted_text, filename)
                    
                    db.create_resume(candidate_name, filename, file_path, extracted_text)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {e}")
                    # Delete the file if saved but failed parsing
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    error_messages.append(f"{file.filename}: {str(e)}")
            else:
                error_messages.append(f"{file.filename}: Invalid format. Only PDF files allowed.")
                
        if success_count > 0:
            flash(f"Successfully processed and uploaded {success_count} resumes.", "success")
        if error_messages:
            for err in error_messages:
                flash(err, "error")
                
        return redirect(url_for('resumes'))
        
    resumes_list = db.get_all_resumes()
    return render_template('resumes.html', resumes=resumes_list, active_page='resumes')

@app.route('/resumes/delete/<int:resume_id>', methods=['POST'])
def delete_resume(resume_id: int):
    try:
        resume = db.get_resume(resume_id)
        if resume:
            # Delete physically
            if os.path.exists(resume['file_path']):
                os.remove(resume['file_path'])
            db.delete_resume(resume_id)
            flash("Resume deleted successfully.", "success")
        else:
            flash("Resume not found.", "error")
    except Exception as e:
        logger.error(f"Error deleting resume: {e}")
        flash("Failed to delete resume.", "error")
    return redirect(url_for('resumes'))

@app.route('/rankings', methods=['GET', 'POST'])
def rankings():
    jds = db.get_all_job_descriptions()
    selected_jd = None
    rankings_list = []
    
    if request.method == 'POST':
        jd_id = request.form.get('jd_id')
        if not jd_id:
            flash("Please select a Job Description.", "error")
            return redirect(url_for('rankings'))
            
        selected_jd = db.get_job_description(int(jd_id))
        all_resumes = db.get_all_resumes()
        
        if not all_resumes:
            flash("No candidate resumes found. Please upload resumes before running similarity matching.", "error")
            return render_template('rankings.html', jds=jds, selected_jd=selected_jd, rankings=[], active_page='rankings')
            
        try:
            # 1. NLP Clean Job Description
            jd_clean = nlp.preprocess_text(selected_jd['description'])
            jd_skills = selected_jd['skills'].split(',') if selected_jd['skills'] else []
            
            # 2. NLP Clean Resumes
            resumes_clean = []
            for resume in all_resumes:
                resumes_clean.append(nlp.preprocess_text(resume['extracted_text']))
                
            # 3. Compute Cosine Similarity scores
            scores = nlp.compute_similarity(jd_clean, resumes_clean)
            
            # 4. Save Rankings back to DB
            for idx, resume in enumerate(all_resumes):
                score = scores[idx]
                matching_skills, missing_skills = nlp.get_skills_analysis(jd_skills, resume['extracted_text'])
                summary = nlp.generate_summary(resume['extracted_text'], 3)
                rec_status = nlp.get_recommendation_status(score)
                
                db.create_ranking(
                    job_description_id=selected_jd['id'],
                    resume_id=resume['id'],
                    score=score,
                    matching_skills=",".join(matching_skills),
                    missing_skills=",".join(missing_skills),
                    summary=summary,
                    recommendation=rec_status
                )
                
            flash("Similarity rankings calculated successfully.", "success")
            # Redirect to GET to avoid form resubmission
            return redirect(url_for('rankings', jd_id=selected_jd['id']))
            
        except Exception as e:
            logger.error(f"Error computing rankings: {e}")
            flash(f"An error occurred computing rankings: {str(e)}", "error")
            
    # GET display logic
    jd_id_param = request.args.get('jd_id')
    if jd_id_param:
        selected_jd = db.get_job_description(int(jd_id_param))
        if selected_jd:
            rankings_list = db.get_rankings_for_job(selected_jd['id'])
            # Generate static charts based on current rankings
            generate_matplotlib_charts(rankings_list)
            
    return render_template(
        'rankings.html', 
        jds=jds, 
        selected_jd=selected_jd, 
        rankings=rankings_list, 
        active_page='rankings'
    )

@app.route('/reports/generate/<int:jd_id>/<string:format>')
def download_report(jd_id: int, format: str):
    """
    Generate and trigger immediate browser download of CSV or PDF reports.
    """
    jd = db.get_job_description(jd_id)
    if not jd:
        flash("Job Description not found.", "error")
        return redirect(url_for('rankings'))
        
    rankings_list = db.get_rankings_for_job(jd_id)
    if not rankings_list:
        flash("No similarity rankings found to export. Run similarity rankings first.", "error")
        return redirect(url_for('rankings', jd_id=jd_id))
        
    filename = f"report_jd_{jd_id}_{random.randint(100, 999)}.{format.lower()}"
    file_path = os.path.join(Config.REPORT_FOLDER, filename)
    
    try:
        if format.lower() == 'csv':
            report_generator.generate_csv_report(jd['title'], rankings_list, file_path)
            db.create_report(jd_id, filename, file_path, 'CSV')
        elif format.lower() == 'pdf':
            report_generator.generate_pdf_report(jd['title'], jd['description'], rankings_list, file_path)
            db.create_report(jd_id, filename, file_path, 'PDF')
        else:
            flash("Invalid report format requested.", "error")
            return redirect(url_for('rankings', jd_id=jd_id))
            
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"Error during report download action: {e}")
        flash("Failed to generate download file.", "error")
        return redirect(url_for('rankings', jd_id=jd_id))

@app.route('/reports')
def reports():
    reports_list = db.get_all_reports()
    return render_template('reports.html', reports=reports_list, active_page='reports')

@app.route('/reports/file/<int:report_id>')
def download_report_file(report_id: int):
    try:
        # Resolve path
        with db.get_db_connection() as conn:
            report = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
            
        if report and os.path.exists(report['file_path']):
            return send_file(report['file_path'], as_attachment=True, download_name=report['filename'])
        else:
            flash("Report file not found on disk.", "error")
    except Exception as e:
        logger.error(f"Error downloading logged report: {e}")
        flash("Download failed.", "error")
    return redirect(url_for('reports'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
