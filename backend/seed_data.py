"""
Seed Script for AI Job Recommendation System
Populates master skills, demo users, freelancer profiles, and job postings with required skills.
"""

import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db, bcrypt
from models import (
    User, RoleEnum, AccountStatusEnum, Profile, Skill,
    FreelancerSkill, Project, ProjectStatusEnum, ProjectSkill
)

app = create_app()

def seed_database():
    with app.app_context():
        print("[SEEDING] Recreating database tables...")
        db.drop_all()
        db.create_all()

        # 1. Seed Master Skills
        skills_list = [
            "Python", "JavaScript", "React", "Flask", "Django", "SQL", "MySQL",
            "Docker", "Kubernetes", "Machine Learning", "NLP", "Data Science",
            "AWS", "REST API", "HTML", "CSS", "Git", "Node.js", "C++", "PyTorch"
        ]
        skill_objects = {}
        for s_name in skills_list:
            skill = Skill.query.filter_by(name=s_name).first()
            if not skill:
                skill = Skill(name=s_name)
                db.session.add(skill)
                db.session.flush()
            skill_objects[s_name] = skill

        # 2. Seed Admin User
        admin_email = "admin@example.com"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name="System Administrator",
                email=admin_email,
                password_hash=bcrypt.generate_password_hash("Password123!").decode("utf-8"),
                role=RoleEnum.ADMIN,
                is_verified=True
            )
            db.session.add(admin)

        # 3. Seed Client User
        client_email = "client@example.com"
        client = User.query.filter_by(email=client_email).first()
        if not client:
            client = User(
                name="Tech Client Inc",
                email=client_email,
                password_hash=bcrypt.generate_password_hash("Password123!").decode("utf-8"),
                role=RoleEnum.CLIENT,
                is_verified=True
            )
            db.session.add(client)
            db.session.flush()

            client_profile = Profile(
                user_id=client.id,
                bio="Leading hiring partner for top AI & software engineering talent.",
                company="TechClient Enterprise"
            ) if hasattr(Profile, 'company') else Profile(user_id=client.id, bio="Tech hiring client")
            db.session.add(client_profile)

        # 4. Seed Freelancer Users
        freelancer_email = "freelancer@example.com"
        freelancer = User.query.filter_by(email=freelancer_email).first()
        if not freelancer:
            freelancer = User(
                name="Alex Dev",
                email=freelancer_email,
                password_hash=bcrypt.generate_password_hash("Password123!").decode("utf-8"),
                role=RoleEnum.FREELANCER,
                is_verified=True
            )
            db.session.add(freelancer)
            db.session.flush()

            fl_profile = Profile(
                user_id=freelancer.id,
                title="Full Stack Python & AI Developer",
                bio="Experienced Python developer specializing in Flask, MySQL, React, and Machine Learning algorithms.",
                experience_years=5,
                hourly_rate=65.00
            )
            db.session.add(fl_profile)
            db.session.flush()

            # Attach skills
            fl_skills = ["Python", "Flask", "React", "SQL", "REST API", "Git"]
            for sk_name in fl_skills:
                fs = FreelancerSkill(profile_id=fl_profile.id, skill_id=skill_objects[sk_name].id)
                db.session.add(fs)

        db.session.commit()

        # 5. Seed Projects with Required Skills
        sample_projects = [
            {
                "title": "AI-Powered Job Recommendation System",
                "description": "Build an end-to-end recommendation engine using Python, Flask, MySQL, and NLP skill extraction with Scikit-Learn TF-IDF vectorization.",
                "category": "Artificial Intelligence",
                "budget_min": 1200.0,
                "budget_max": 2500.0,
                "required_skills": ["Python", "Flask", "MySQL", "Machine Learning", "NLP", "REST API"]
            },
            {
                "title": "Full Stack Web Application Development",
                "description": "Develop a responsive React dashboard integrated with a Python Flask REST API backend and clean database design.",
                "category": "Web Development",
                "budget_min": 800.0,
                "budget_max": 1800.0,
                "required_skills": ["Python", "Flask", "React", "JavaScript", "SQL"]
            },
            {
                "title": "Cloud DevOps & Microservices Containerization",
                "description": "Deploy Docker containerized backend services with automated Gunicorn WSGI runners and MySQL replication.",
                "category": "DevOps & Cloud",
                "budget_min": 1000.0,
                "budget_max": 2000.0,
                "required_skills": ["Docker", "Kubernetes", "AWS", "Python"]
            }
        ]

        for p_data in sample_projects:
            proj = Project.query.filter_by(title=p_data["title"]).first()
            if not proj and client:
                proj = Project(
                    client_id=client.id,
                    title=p_data["title"],
                    description=p_data["description"],
                    category=p_data["category"],
                    budget_min=p_data["budget_min"],
                    budget_max=p_data["budget_max"],
                    status=ProjectStatusEnum.OPEN
                )
                db.session.add(proj)
                db.session.flush()

                for sk_name in p_data["required_skills"]:
                    if sk_name in skill_objects:
                        ps = ProjectSkill(project_id=proj.id, skill_id=skill_objects[sk_name].id)
                        db.session.add(ps)

        db.session.commit()
        print("[SUCCESS] Seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
