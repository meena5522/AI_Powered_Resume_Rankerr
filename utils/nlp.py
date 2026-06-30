import re
import spacy
import logging
from typing import List, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Programmatic download of SpaCy model to ensure zero-setup experience
nlp = None
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.info("Downloading spacy model en_core_web_sm...")
    import subprocess
    import sys
    try:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        logger.error(f"Failed to load or download spacy model: {e}")
        # Fallback to a basic english tokenizer logic if spacy fails completely, but spacy download should succeed.
        raise RuntimeError("SpaCy model en_core_web_sm could not be loaded or installed.")

# Predefined standard tech and professional skills list for extracting requirements
COMMON_SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "php", "go", "rust", "scala", "kotlin", "swift", "r", "sql", "html", "css", "shell", "bash",
    # Frameworks & Libraries
    "flask", "django", "fastapi", "spring", "node.js", "express", "react", "angular", "vue", "jquery", "bootstrap", "tailwind", "next.js", "nestjs",
    # Data Science & ML
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "spacy", "nltk", "opencv", "matplotlib", "seaborn", "plotly", "tableau", "power bi",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "terraform", "ansible", "ci/cd",
    # Databases
    "sqlite", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "sql server",
    # Methodology & Professional
    "agile", "scrum", "project management", "software development", "web development", "machine learning", "deep learning", "nlp", "computer vision", 
    "data science", "data analysis", "system design", "rest api", "graphql", "microservices", "unit testing", "oop", "communication", "leadership"
]

def preprocess_text(text: str) -> str:
    """
    Cleans, tokenizes, removes stop-words and punctuations, and lemmatizes text using SpaCy.
    
    Args:
        text (str): Raw text.
        
    Returns:
        str: Preprocessed space-separated lemmas.
    """
    if not text:
        return ""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    doc = nlp(text)
    
    clean_tokens = []
    for token in doc:
        # Filter stopwords, punctuations, whitespace, and symbols
        if not token.is_stop and not token.is_punct and not token.is_space and len(token.lemma_.strip()) > 1:
            # Keep only alphanumeric or specific characters (like c++, c#)
            lemma = token.lemma_.lower().strip()
            if re.match(r'^[a-z0-9+#.\-_]+$', lemma):
                clean_tokens.append(lemma)
                
    return " ".join(clean_tokens)

def extract_skills(text: str) -> List[str]:
    """
    Extracts matching skills from text by checking against a predefined vocabulary.
    Handles exact word matching and standard abbreviation boundary formatting.
    
    Args:
        text (str): Input text.
        
    Returns:
        List[str]: Sorted list of unique skills found.
    """
    found_skills = set()
    text_lower = text.lower()
    
    for skill in COMMON_SKILLS:
        # Escape skill for safe regex matching (e.g. c++, node.js)
        escaped_skill = re.escape(skill)
        
        # Word boundary pattern; since '+' and '#' are non-word chars, handle them specially
        if skill.endswith('++') or skill.endswith('#'):
            pattern = r'\b' + escaped_skill
        elif skill.startswith('.') or skill.endswith('.'):
            pattern = escaped_skill
        else:
            pattern = r'\b' + escaped_skill + r'\b'
            
        if re.search(pattern, text_lower):
            found_skills.add(skill)
            
    return sorted(list(found_skills))

def get_skills_analysis(jd_skills: List[str], resume_text: str) -> Tuple[List[str], List[str]]:
    """
    Compares JD skills against Resume text.
    
    Returns:
        Tuple[List[str], List[str]]: (matching_skills, missing_skills)
    """
    resume_skills = set(extract_skills(resume_text))
    jd_skills_set = set(jd_skills)
    
    matching = jd_skills_set.intersection(resume_skills)
    missing = jd_skills_set.difference(resume_skills)
    
    return sorted(list(matching)), sorted(list(missing))

def generate_summary(text: str, num_sentences: int = 3) -> str:
    """
    Generates an extractive summary using SpaCy by ranking sentences
    based on normalized word frequencies.
    
    Args:
        text (str): Raw resume text.
        num_sentences (int): Number of sentences in output summary.
        
    Returns:
        str: Extracted summary sentences.
    """
    if not text:
        return "No text available for summary."
        
    # Split text into sentences using SpaCy
    doc = nlp(text)
    sentences = [sent for sent in doc.sents if len(sent.text.strip()) > 10]
    
    if len(sentences) <= num_sentences:
        return " ".join([sent.text.strip() for sent in sentences])
        
    # Calculate frequency of terms (excluding stopwords & punctuations)
    word_frequencies = {}
    for word in doc:
        if not word.is_stop and not word.is_punct and not word.is_space:
            lemma = word.lemma_.lower()
            word_frequencies[lemma] = word_frequencies.get(lemma, 0) + 1
            
    if not word_frequencies:
        return " ".join([sent.text.strip() for sent in sentences[:num_sentences]])
        
    # Normalize frequencies
    max_freq = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_freq
        
    # Score sentences based on sum of word frequencies
    sentence_scores = {}
    for sent in sentences:
        score = 0
        for word in sent:
            lemma = word.lemma_.lower()
            if lemma in word_frequencies:
                score += word_frequencies[lemma]
        sentence_scores[sent] = score
        
    # Sort and pick top sentences
    top_sentences = sorted(sentence_scores.keys(), key=lambda s: sentence_scores[s], reverse=True)[:num_sentences]
    
    # Sort sentences based on their original position in the text to maintain narrative flow
    top_sentences.sort(key=lambda s: s.start)
    
    return " ".join([sent.text.strip().replace('\n', ' ') for sent in top_sentences])

def compute_similarity(job_desc_clean: str, resumes_clean: List[str]) -> List[float]:
    """
    Computes cosine similarity between a preprocessed Job Description
    and a list of preprocessed Resumes using TF-IDF.
    
    Args:
        job_desc_clean (str): Preprocessed job description.
        resumes_clean (List[str]): List of preprocessed resumes.
        
    Returns:
        List[float]: Similarity percentage scores (0.0 to 100.0) for each resume.
    """
    if not job_desc_clean or not resumes_clean:
        return [0.0] * len(resumes_clean)
        
    # Combine JD and Resumes to fit TF-IDF vectorizer
    documents = [job_desc_clean] + resumes_clean
    
    # Fit and transform
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate similarity between first document (JD) and all other documents (Resumes)
    jd_vector = tfidf_matrix[0:1]
    resume_vectors = tfidf_matrix[1:]
    
    similarities = cosine_similarity(jd_vector, resume_vectors)[0]
    
    # Convert similarity coefficients to percentages (0-100)
    scores = [round(float(score) * 100, 2) for score in similarities]
    return scores

def get_recommendation_status(score: float) -> str:
    """
    Determines candidate recommendation status based on score threshold.
    """
    if score >= 75.0:
        return "Highly Recommended"
    elif score >= 50.0:
        return "Recommended"
    elif score >= 25.0:
        return "Consider"
    else:
        return "Not Recommended"
