"""
Learning Service
================
Provides:
- Phase 11: Detailed Skill Gap Analysis
- Phase 14: Automated Personalized Learning Roadmap & Resources
"""

from typing import List, Dict, Any
from models import Profile, Project, ProjectStatusEnum


RESOURCE_DATABASE = {
    "python": {
        "title": "Python for Everybody & Advanced Concepts",
        "doc_url": "https://docs.python.org/3/tutorial/",
        "course_url": "https://www.coursera.org/specializations/python",
        "youtube_search": "https://www.youtube.com/results?search_query=python+programming+full+course",
        "estimated_hours": 20,
        "difficulty": "Beginner to Intermediate"
    },
    "javascript": {
        "title": "Modern JavaScript (ES6+)",
        "doc_url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "course_url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
        "youtube_search": "https://www.youtube.com/results?search_query=javascript+full+course",
        "estimated_hours": 25,
        "difficulty": "Beginner to Intermediate"
    },
    "react": {
        "title": "React.js Frontend Masterclass",
        "doc_url": "https://react.dev/learn",
        "course_url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
        "youtube_search": "https://www.youtube.com/results?search_query=reactjs+tutorial+for+beginners",
        "estimated_hours": 30,
        "difficulty": "Intermediate"
    },
    "flask": {
        "title": "Flask Web Development in Python",
        "doc_url": "https://flask.palletsprojects.com/",
        "course_url": "https://testdriven.io/courses/learn-flask/",
        "youtube_search": "https://www.youtube.com/results?search_query=flask+python+tutorial",
        "estimated_hours": 15,
        "difficulty": "Intermediate"
    },
    "sql": {
        "title": "Relational Databases & SQL Queries",
        "doc_url": "https://dev.mysql.com/doc/refman/8.0/en/",
        "course_url": "https://www.sqlbolt.com/",
        "youtube_search": "https://www.youtube.com/results?search_query=sql+database+tutorial",
        "estimated_hours": 15,
        "difficulty": "Beginner"
    },
    "docker": {
        "title": "Docker Containers & Microservices",
        "doc_url": "https://docs.docker.com/get-started/",
        "course_url": "https://www.udemy.com/course/docker-mastery/",
        "youtube_search": "https://www.youtube.com/results?search_query=docker+tutorial+for+beginners",
        "estimated_hours": 10,
        "difficulty": "Intermediate"
    },
    "machine learning": {
        "title": "Machine Learning & Scikit-Learn Fundamentals",
        "doc_url": "https://scikit-learn.org/stable/user_guide.html",
        "course_url": "https://www.coursera.org/learn/machine-learning",
        "youtube_search": "https://www.youtube.com/results?search_query=machine+learning+course+python",
        "estimated_hours": 40,
        "difficulty": "Advanced"
    }
}


def get_skill_resources(skill_name: str) -> Dict[str, Any]:
    key = skill_name.strip().lower()
    if key in RESOURCE_DATABASE:
        res = RESOURCE_DATABASE[key]
        return {
            "skill": skill_name,
            "title": res["title"],
            "doc_url": res["doc_url"],
            "course_url": res["course_url"],
            "youtube_url": res["youtube_search"],
            "estimated_hours": res["estimated_hours"],
            "difficulty": res["difficulty"]
        }

    # Dynamic fallback resource generator for any missing skill
    query = skill_name.replace(" ", "+")
    return {
        "skill": skill_name,
        "title": f"Mastering {skill_name}",
        "doc_url": f"https://www.google.com/search?q={query}+official+documentation",
        "course_url": f"https://www.coursera.org/search?query={query}",
        "youtube_url": f"https://www.youtube.com/results?search_query={query}+tutorial+for+beginners",
        "estimated_hours": 15,
        "difficulty": "Intermediate"
    }


def analyze_skill_gap(user_id: int, project_id: int) -> Dict[str, Any]:
    """
    Phase 11: Analyze Skill Gap for a user against a target project.
    """
    profile = Profile.query.filter_by(user_id=user_id).first()
    project = Project.query.get(project_id)

    if not profile or not project:
        return {"error": "Profile or project not found"}

    user_skills = [s.skill.name for s in profile.skills] if profile.skills else []
    job_skills = [s.skill.name for s in project.skills] if project.skills else []

    user_set = set(s.lower() for s in user_skills)
    job_set = set(s.lower() for s in job_skills)

    matched = []
    missing = []

    for s in job_skills:
        if s.lower() in user_set:
            matched.append(s)
        else:
            missing.append(s)

    match_percent = (len(matched) / len(job_skills) * 100.0) if job_skills else 100.0

    if match_percent >= 80:
        readiness = "Ready to Apply (High Fit)"
        recommendation_note = "You possess almost all required skills for this job. Submit your proposal!"
    elif match_percent >= 50:
        readiness = "Minor Skill Gap"
        recommendation_note = "You have a solid foundation. Review the recommended learning resources below to bridge your missing skills."
    else:
        readiness = "Major Skill Gap"
        recommendation_note = "Consider taking 1-2 weeks to complete the recommended roadmap before applying."

    return {
        "project_id": project.id,
        "project_title": project.title,
        "match_percentage": round(match_percent, 1),
        "readiness": readiness,
        "recommendation_note": recommendation_note,
        "possessed_skills": user_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "total_required_skills_count": len(job_skills)
    }


def generate_learning_roadmap(missing_skills: List[str]) -> Dict[str, Any]:
    """
    Phase 14: Generate a multi-stage personalized learning roadmap.
    """
    if not missing_skills:
        return {
            "total_missing_skills": 0,
            "estimated_days": 0,
            "roadmap_stages": [],
            "message": "Congratulations! You have all required skills for this role."
        }

    skill_modules = [get_skill_resources(s) for s in missing_skills]
    total_hours = sum(m["estimated_hours"] for m in skill_modules)
    estimated_days = max(1, round(total_hours / 3.0))  # Assuming 3 hours/day study

    stages = [
        {
            "stage_number": 1,
            "title": "Stage 1: Core Fundamentals & Theory",
            "description": "Understand language syntax, core concepts, and official documentation.",
            "skills": missing_skills[:2],
            "action": "Read official docs & watch introductory video courses."
        },
        {
            "stage_number": 2,
            "title": "Stage 2: Hands-on Exercises & Small Modules",
            "description": "Build miniature practice projects, write unit tests, and solve coding tasks.",
            "skills": missing_skills,
            "action": "Complete interactive coding exercises on FreeCodeCamp / LeetCode."
        },
        {
            "stage_number": 3,
            "title": "Stage 3: Portfolio Integration & Job Readiness",
            "description": "Combine newly learned skills into a showcase project and update your profile resume.",
            "skills": missing_skills,
            "action": "Build a real-world demo app and attach code link to your profile."
        }
    ]

    return {
        "total_missing_skills": len(missing_skills),
        "total_estimated_hours": total_hours,
        "estimated_days": estimated_days,
        "skill_modules": skill_modules,
        "roadmap_stages": stages
    }
