"""
Recommendation Engine Service
==============================
Provides multi-tiered recommendation algorithms:
- Phase 8: Basic Skill Matching (Jaccard Overlap)
- Phase 12: TF-IDF & Cosine Similarity
- Phase 13: Hybrid Semantic AI Match Score & Job Ranking
"""

import math
from typing import List, Dict, Any, Tuple

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from models import Project, Profile, Skill, ProjectSkill, FreelancerSkill, ProjectStatusEnum


def calculate_skill_overlap(user_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
    """
    Phase 8: Basic Skill Matcher
    Calculates exact overlap, missing skills, and overlap score percentage.
    """
    user_set = set(s.strip().lower() for s in user_skills if s)
    job_set = set(s.strip().lower() for s in job_skills if s)

    if not job_set:
        return {
            "score": 100.0 if user_set else 50.0,
            "matched_skills": list(user_skills),
            "missing_skills": [],
            "total_job_skills": 0
        }

    matched_lower = user_set.intersection(job_set)
    missing_lower = job_set - user_set

    # Map back to original casing
    orig_job_map = {s.lower(): s for s in job_skills}
    matched_skills = [orig_job_map[s] for s in matched_lower if s in orig_job_map]
    missing_skills = [orig_job_map[s] for s in missing_lower if s in orig_job_map]

    overlap_score = (len(matched_lower) / len(job_set)) * 100.0

    return {
        "score": round(overlap_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_job_skills": len(job_set)
    }


def calculate_tfidf_similarity(user_text: str, job_text: str) -> float:
    """
    Phase 12: TF-IDF & Cosine Similarity Score (0-100%)
    """
    if not user_text.strip() or not job_text.strip():
        return 0.0

    if HAS_SKLEARN:
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([user_text, job_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(float(similarity) * 100.0, 1)
        except Exception:
            pass

    # Pure Python TF-IDF term frequency & cosine similarity fallback
    words1 = [w.lower() for w in user_text.split() if len(w) > 2]
    words2 = [w.lower() for w in job_text.split() if len(w) > 2]
    if not words1 or not words2:
        return 0.0

    vocab = set(words1 + words2)
    vec1 = [words1.count(w) for w in vocab]
    vec2 = [words2.count(w) for w in vocab]

    dot_prod = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    mag1 = math.sqrt(sum(v1 ** 2 for v1 in vec1))
    mag2 = math.sqrt(sum(v2 ** 2 for v2 in vec2))

    if mag1 == 0 or mag2 == 0:
        return 0.0

    cosine_sim = dot_prod / (mag1 * mag2)
    return round(float(cosine_sim) * 100.0, 1)


def compute_hybrid_match_score(
    profile: Profile,
    project: Project
) -> Dict[str, Any]:
    """
    Phase 13: Hybrid Semantic AI Match Score
    Weights:
      - 50%: Skill Overlap
      - 30%: TF-IDF Cosine Similarity of Bio/Resume vs Job Description
      - 20%: Category / Title fit
    """
    user_skills = [s.skill.name for s in profile.skills] if profile.skills else []
    job_skills = [s.skill.name for s in project.skills] if project.skills else []

    # 1. Skill Overlap Score (50%)
    skill_match = calculate_skill_overlap(user_skills, job_skills)
    skill_score = skill_match["score"]

    # 2. TF-IDF Text Similarity (30%)
    user_corpus = f"{profile.title or ''} {profile.bio or ''} {' '.join(user_skills)} {profile.extracted_text or ''}"
    job_corpus = f"{project.title} {project.category or ''} {project.description} {' '.join(job_skills)}"

    tfidf_score = calculate_tfidf_similarity(user_corpus, job_corpus)

    # 3. Category & Title Domain Fit (20%)
    fit_score = 50.0
    if profile.title and project.title:
        title_lower = profile.title.lower()
        proj_title_lower = project.title.lower()
        if any(w in proj_title_lower for w in title_lower.split() if len(w) > 3):
            fit_score += 30.0
    if project.category and profile.title:
        if project.category.lower() in profile.title.lower():
            fit_score += 20.0
    fit_score = min(fit_score, 100.0)

    # Final Combined Weighted Score
    final_score = (skill_score * 0.50) + (tfidf_score * 0.30) + (fit_score * 0.20)
    final_score = round(min(max(final_score, 0.0), 100.0), 1)

    # Fit tier label
    if final_score >= 85.0:
        tier = "Excellent Match"
        badge_class = "badge-success"
    elif final_score >= 70.0:
        tier = "Good Match"
        badge_class = "badge-primary"
    elif final_score >= 50.0:
        tier = "Potential Match"
        badge_class = "badge-warning"
    else:
        tier = "Low Match"
        badge_class = "badge-secondary"

    return {
        "project_id": project.id,
        "project": project.to_dict(),
        "match_score": final_score,
        "skill_score": skill_score,
        "tfidf_score": tfidf_score,
        "fit_score": fit_score,
        "tier": tier,
        "badge_class": badge_class,
        "matched_skills": skill_match["matched_skills"],
        "missing_skills": skill_match["missing_skills"],
        "total_required_skills": skill_match["total_job_skills"]
    }


def get_recommendations_for_user(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch open jobs, score them against user profile, and return top recommendations.
    """
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return []

    # Get open projects
    open_projects = Project.query.filter_by(status=ProjectStatusEnum.OPEN).all()

    recommendations = []
    for proj in open_projects:
        match_data = compute_hybrid_match_score(profile, proj)
        recommendations.append(match_data)

    # Sort descending by match score
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:limit]
