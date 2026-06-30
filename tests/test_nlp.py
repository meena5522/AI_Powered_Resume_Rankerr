import unittest
from utils import nlp

class TestNLPPipeline(unittest.TestCase):
    
    def setUp(self):
        self.job_desc = "Looking for a Python Backend Developer experienced in Flask, PostgreSQL, and Git."
        self.resume_match = "Python developer with 3 years of experience building REST APIs using Flask. Experienced with Git and PostgreSQL databases."
        self.resume_nomatch = "Frontend designer skilled in React, CSS, HTML, Vue, and UI layouts. No backend experience."

    def test_preprocess_text(self):
        text = "Running and cleaning, Python developer!"
        cleaned = nlp.preprocess_text(text)
        # Check tokenization, lemmatization and stop-words removal
        # "running" -> "run", "cleaning" -> "clean", "python" -> "python"
        self.assertIn("run", cleaned)
        self.assertIn("clean", cleaned)
        self.assertIn("python", cleaned)
        # Excludes punctuations
        self.assertNotIn("!", cleaned)
        self.assertNotIn(",", cleaned)

    def test_extract_skills(self):
        skills = nlp.extract_skills(self.job_desc)
        self.assertIn("python", skills)
        self.assertIn("flask", skills)
        self.assertIn("postgresql", skills)
        self.assertIn("git", skills)
        self.assertNotIn("react", skills)

    def test_get_skills_analysis(self):
        jd_skills = ["python", "flask", "postgresql", "git"]
        matching, missing = nlp.get_skills_analysis(jd_skills, self.resume_match)
        
        # Candidate has python, flask, git, postgresql
        self.assertEqual(len(matching), 4)
        self.assertEqual(len(missing), 0)
        
        # Test against non-matching resume
        matching2, missing2 = nlp.get_skills_analysis(jd_skills, self.resume_nomatch)
        self.assertEqual(len(matching2), 0)
        self.assertEqual(len(missing2), 4)

    def test_compute_similarity(self):
        jd_clean = nlp.preprocess_text(self.job_desc)
        resume_match_clean = nlp.preprocess_text(self.resume_match)
        resume_nomatch_clean = nlp.preprocess_text(self.resume_nomatch)
        
        scores = nlp.compute_similarity(jd_clean, [resume_match_clean, resume_nomatch_clean])
        
        # Score for match resume should be higher than non-match
        self.assertEqual(len(scores), 2)
        self.assertTrue(scores[0] > scores[1])
        # Score ranges should be percentages
        self.assertTrue(0.0 <= scores[0] <= 100.0)

    def test_generate_summary(self):
        text = "This is a candidate resume. John Doe is a Software Engineer. He has worked at Google for five years. He built backend systems. Google was nice."
        summary = nlp.generate_summary(text, num_sentences=2)
        self.assertTrue(len(summary) > 0)
        # Extracted sentences should be present in original text
        self.assertIn("John Doe", summary)

if __name__ == '__main__':
    unittest.main()
