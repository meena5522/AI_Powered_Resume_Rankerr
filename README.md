# AI-Powered Resume Ranker

A modular, production-ready recruitment and HR intelligence platform built using Python, Flask, SpaCy, and Scikit-learn. This system parses PDF resumes, extracts candidate details, matches tech/professional skills against job descriptions using Natural Language Processing (NLP), and ranks them using TF-IDF and Cosine Similarity. It provides a modern, responsive web dashboard with analytical insights and automated PDF/CSV report generation.

---

## 🌟 Key Features

*   **Recruiter Authentication:** Session-based signup, login, password hashing, and recruiter profile settings (username/email/password updates).
*   **Job Description Management:** Define roles, paste detailed postings, and automatically extract key skill requirements using NLP.
*   **Multiple Resume Uploader:** Upload single or multiple PDF resumes. The system validates formatting and processes them concurrently.
*   **NLP Pipeline & Similarity Engine:**
    *   *Text Extraction:* Parses text from complex PDFs.
    *   *Preprocessing:* Cleans text, tokenizes, removes stop-words/punctuation, and lemmatizes using SpaCy (`en_core_web_sm`).
    *   *Extractive Summarizer:* Automatically extracts a 3-sentence summary of the candidate's experience.
    *   *TF-IDF Vectorizer & Cosine Similarity:* Measures language overlap and terms weighting to compute a match score (0% to 100%).
*   **Interactive HR Dashboard:**
    *   Quick stats cards (Total resumes, job descriptions, similarity score averages).
    *   Matplotlib-generated analytics (Candidate score distribution and recommendation share).
    *   Filter and search tables instantaneously.
*   **Automatic Recommendations:** Automatically labels candidates as *Highly Recommended*, *Recommended*, *Consider*, or *Not Recommended* based on matching thresholds.
*   **Exportable Reports:** One-click downloads for PDF (using ReportLab) and CSV reports.

---

## 📂 Project Structure

```
AI_POWERED_RESUME_RANKER/
├── app.py                  # Server entrypoint, configuration, and controller routes
├── config.py               # Application configurations (folders, secret keys)
├── requirements.txt        # Python dependency manifest
├── .gitignore              # Git ignore rules
├── LICENSE                 # License terms
├── README.md               # User documentation
├── deployment_guide.md     # Production and staging setup manual
├── internship_report.md    # Summary academic report
├── models/
│   └── database.py         # SQLite connection manager and database queries (CRUD)
├── utils/
│   ├── nlp.py              # Text preprocessor, skill analyser, cosine match and summarizer
│   ├── pdf_parser.py       # PDF reader and parser (PyPDF2)
│   └── report_generator.py # CSV and ReportLab PDF document builders
├── static/
│   ├── css/
│   │   └── style.css       # Custom glassmorphic styles and badges
│   ├── js/
│   │   └── main.js         # Table filters, loaders, alert triggers
│   └── charts/             # Folder for generated matplotlib visuals
├── templates/
│   ├── base.html           # Unified master dashboard layout
│   ├── login.html          # Auth login portal
│   ├── register.html       # Auth registration portal
│   ├── profile.html        # Recruiter details updates
│   ├── dashboard.html      # HR stats, charts, and upload logs
│   ├── job_descriptions.html # Job Description posting management
│   ├── resumes.html        # Candidates list and file upload panel
│   ├── rankings.html       # Roles dropdown list and similarity charts
│   └── reports.html        # Downloader catalog for historical exports
├── uploads/                # Repository directory for uploaded candidate files
├── reports/                # Local repository for generated CSV/PDF files
└── tests/
    ├── generate_test_data.py # Helper script to create fake candidate resumes in PDF
    ├── test_auth.py        # Authentication unit tests
    ├── test_nlp.py         # Text preprocessing and NLP unit tests
    └── test_routes.py      # Authorizations and navigation route tests
```

---

## 🚀 Installation & Getting Started

### 1. Prerequisites
Ensure you have Python (version 3.8 to 3.12 recommended) installed on your machine.

### 2. Clone the Repository
Clone or extract the workspace files into your local directory.

### 3. Set Up Virtual Environment
Create a clean environment and activate it:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Install all required modules from the manifest:
```bash
pip install -r requirements.txt
```

### 5. Download the NLP Language Model
Download the English tokenizer and parsing dictionary from SpaCy:
```bash
python -m spacy download en_core_web_sm
```
*(Note: The application is built to automatically download this package on startup if it is not found on the local system)*

### 6. Generate Test Candidates (Optional)
Run the automated test data builder to generate three mock candidates in the `uploads/` directory:
```bash
python tests/generate_test_data.py
```

### 7. Launch the Server
Start the Flask development server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 🧪 Running Unit Tests

Verify code quality and functional behavior by running the unittest suite:
```bash
python -m unittest discover -s tests
```

---

## 🛠️ Tech Stack & Libraries

*   **Framework:** Flask
*   **Database:** SQLite (built-in connector)
*   **NLP:** SpaCy (`en_core_web_sm`)
*   **Similarity Matcher:** Scikit-learn (`TfidfVectorizer`, `cosine_similarity`)
*   **PDF Extraction:** PyPDF2
*   **Data Analysis:** Pandas, NumPy, Matplotlib
*   **PDF Generation:** ReportLab
*   **Front-end Style:** Bootstrap 5, FontAwesome Icons, Custom Glassmorphic CSS
