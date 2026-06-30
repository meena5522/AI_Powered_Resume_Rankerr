# Deployment Guide - AI-Powered Resume Ranker

This guide outlines deployment options for hosting the AI-Powered Resume Ranker application. It includes local testing configurations, production deployments using standard WSGI containers, cloud hosting options, and database considerations.

---

## 💻 1. Local Deployment (Development Mode)

This mode is designed for sandbox testing, developer reviews, and local demo presentations.

1.  **Configure Env Variables:**
    By default, `app.py` falls back to a development secret key. For a cleaner local profile:
    ```bash
    # Windows Command Prompt
    set SECRET_KEY=your_development_secret_key_123

    # Windows PowerShell
    $env:SECRET_KEY="your_development_secret_key_123"

    # macOS/Linux
    export SECRET_KEY="your_development_secret_key_123"
    ```
2.  **Start Server:**
    Run `python app.py`. This boots the Flask built-in server in `debug=True` mode on `127.0.0.1:5000`.
    *Warning: Do not use the built-in development server in production environments as it is single-threaded and not optimized for heavy connection loads.*

---

## 🌐 2. Production Linux Deployment (Gunicorn + Nginx)

For standard VPS hostings (Ubuntu, Debian, CentOS), a combination of **Gunicorn** (WSGI Application Server) and **Nginx** (Reverse Proxy) is the industry standard.

### Step 1: Install System Packages
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx supervisor -y
```

### Step 2: Configure Application & Dependencies
Clone your files into `/var/www/resume-ranker/` and set up permissions:
```bash
cd /var/www/
sudo chown -R ubuntu:ubuntu resume-ranker/
cd resume-ranker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
```

### Step 3: Configure Supervisor (Process Manager)
Create a supervisor config to manage and keep Gunicorn alive:
`sudo nano /etc/supervisor/conf.d/resume_ranker.conf`

```ini
[program:resume_ranker]
directory=/var/www/resume-ranker
command=/var/www/resume-ranker/venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 app:app
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/resume_ranker.err.log
stdout_logfile=/var/log/resume_ranker.out.log
environment=SECRET_KEY="your_secure_production_secret_key"
```
Apply supervisor rules:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

### Step 4: Configure Nginx (Reverse Proxy)
Create an Nginx configuration file:
`sudo nano /etc/nginx/sites-available/resume_ranker`

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static assets directly for better performance
    location /static/ {
        alias /var/www/resume-ranker/static/;
        expires 30d;
    }
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/resume_ranker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ☁️ 3. Cloud Platform Deployment (PaaS)

### Render (Recommended)
1.  Create a new Web Service on Render and link your GitHub repository.
2.  Set the following environment configurations:
    *   **Runtime:** `Python`
    *   **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
    *   **Start Command:** `gunicorn app:app`
3.  Add environment variables in the Dashboard tab:
    *   `SECRET_KEY` = `a_very_long_random_alphanumeric_sequence`
4.  *Note: Render uses an ephemeral filesystem. If your service spins down, uploaded PDFs and SQLite databases will reset. To persist upload records, mount a Render Disk or read the database scaling advice below.*

### Heroku
Create a `Procfile` in the project root:
```
web: gunicorn app:app
```
Provide the SpaCy model installation in `requirements.txt` or using a Heroku buildpack.

---

## 🗄️ 4. Production Database Scaling

This application is built with a SQLite database (`resume_ranker.db`) stored on disk. While SQLite is light and requires zero-setup:
*   It does not support concurrent write operations under heavy loads.
*   Cloud PaaS options (Render, Heroku) wipe internal databases on redeployment due to ephemeral disks.

### Migrating to PostgreSQL/MySQL
1.  **Refactor Connector:** Modify `models/database.py` to use `psycopg2` or `pymysql` libraries.
2.  **Environment Credentials:** Replace file paths with a DB connection string URI (`DATABASE_URL=postgresql://user:pass@host:port/dbname`).
3.  **Connection Pooling:** Use SQLAlchemy or connection pool managers to safely recycle database threads in production.
