"""
Automated Integration Tests for AI Job Recommendation System
"""

import unittest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from services.nlp_service import extract_skills_from_text
from services.recommendation_service import (
    calculate_skill_overlap,
    calculate_tfidf_similarity
)
from services.learning_service import generate_learning_roadmap
from services.chatbot_service import process_chatbot_query


class TestRecommendationSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_nlp_skill_extraction(self):
        sample_resume_text = """
        John Doe
        Senior Full Stack Software Engineer
        Proficient in Python, Flask, React.js, MySQL, Docker, and REST API development.
        Familiar with Machine Learning, Scikit-Learn, and Git version control.
        """
        res = extract_skills_from_text(sample_resume_text)
        self.assertGreaterEqual(res["skill_count"], 5)
        self.assertIn("Python", res["skills"])
        self.assertIn("Flask", res["skills"])
        self.assertIn("React", res["skills"])
        self.assertIn("Docker", res["skills"])

    def test_skill_overlap_calculation(self):
        user_skills = ["Python", "Flask", "React", "SQL"]
        job_skills = ["Python", "Flask", "Docker", "AWS"]

        overlap = calculate_skill_overlap(user_skills, job_skills)
        self.assertEqual(overlap["score"], 50.0)
        self.assertIn("Python", overlap["matched_skills"])
        self.assertIn("Flask", overlap["matched_skills"])
        self.assertIn("Docker", overlap["missing_skills"])
        self.assertIn("AWS", overlap["missing_skills"])

    def test_tfidf_similarity(self):
        candidate_profile = "Python Flask React full stack web developer building APIs and databases"
        job_description = "Seeking a Python Flask developer to create REST APIs with database models"
        unrelated_job = "Senior Graphic Designer creating Logos and Photoshop illustrations"

        sim_high = calculate_tfidf_similarity(candidate_profile, job_description)
        sim_low = calculate_tfidf_similarity(candidate_profile, unrelated_job)

        self.assertGreater(sim_high, sim_low)
        self.assertGreater(sim_high, 30.0)

    def test_learning_roadmap_generation(self):
        missing_skills = ["Docker", "Kubernetes"]
        roadmap = generate_learning_roadmap(missing_skills)

        self.assertEqual(roadmap["total_missing_skills"], 2)
        self.assertEqual(len(roadmap["roadmap_stages"]), 3)
        self.assertEqual(len(roadmap["skill_modules"]), 2)

    def test_chatbot_query(self):
        res = process_chatbot_query(user_id=None, query="Hello")
        self.assertEqual(res["intent"], "greeting")
        self.assertIn("AI Career", res["response"])

        score_info = process_chatbot_query(user_id=None, query="How is match score calculated?")
        self.assertEqual(score_info["intent"], "algorithm_info")
        self.assertIn("TF-IDF", score_info["response"])


if __name__ == "__main__":
    unittest.main()
