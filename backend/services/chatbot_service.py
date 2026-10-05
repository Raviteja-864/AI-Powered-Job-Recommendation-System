"""
AI Chatbot Service
==================
Phase 15: Intelligent Career & Job Recommendation Chat Assistant
"""

import re
from typing import Dict, Any
from models import Profile, User
from services.recommendation_service import get_recommendations_for_user


def process_chatbot_query(user_id: int, query: str) -> Dict[str, Any]:
    """
    Process user query and generate AI career guidance response.
    """
    query_clean = query.strip().lower()
    profile = Profile.query.filter_by(user_id=user_id).first() if user_id else None
    user = User.query.get(user_id) if user_id else None

    user_name = user.name if user else "Job Seeker"

    # Intent 1: Greetings
    if any(w in query_clean for w in ["hi", "hello", "hey", "greetings", "start"]):
        response = (
            f"Hello {user_name}! 👋 I am your AI Career & Job Recommendation Assistant. "
            "How can I help you today? You can ask me:\n"
            "- 'Show my top job recommendations'\n"
            "- 'How do I improve my resume?'\n"
            "- 'What skills am I missing?'\n"
            "- 'How does match score calculation work?'"
        )
        return {"response": response, "intent": "greeting"}

    # Intent 2: Recommendation query
    if any(w in query_clean for w in ["recommend", "matched job", "jobs for me", "job list", "find job"]):
        if not user_id:
            return {"response": "Please log in to view your personalized AI job recommendations.", "intent": "auth_required"}

        recs = get_recommendations_for_user(user_id, limit=3)
        if not recs:
            response = (
                "I couldn't find active jobs matching your profile yet. "
                "Try adding more skills to your profile or uploading your resume!"
            )
        else:
            job_list_str = "\n".join(
                [f"• **{r['project']['title']}** — Match Score: **{r['match_score']}%** ({r['tier']})" for r in recs]
            )
            response = (
                f"Here are your top AI-recommended job matches, {user_name}:\n\n"
                f"{job_list_str}\n\n"
                "Visit the **AI Recommendations** page to see complete skill gap details and apply!"
            )
        return {"response": response, "intent": "recommendations"}

    # Intent 3: Resume advice
    if any(w in query_clean for w in ["resume", "cv", "upload", "extract"]):
        if profile and profile.resume_filename:
            response = (
                f"📄 You have uploaded `{profile.resume_filename}`. "
                f"Our NLP engine extracted {len(profile.skills)} skills from your profile. "
                "To increase your match score, make sure your resume lists technical keywords, tools, and quantifiable project achievements!"
            )
        else:
            response = (
                "📄 You haven't uploaded a resume yet! Upload your PDF/DOCX resume in the Dashboard. "
                "Our NLP Skill Extractor will automatically scan your resume and match you to top tech jobs."
            )
        return {"response": response, "intent": "resume_advice"}

    # Intent 4: Skill gap or learning
    if any(w in query_clean for w in ["gap", "missing skill", "learn", "course", "roadmap"]):
        response = (
            "🎯 **Skill Gap Analysis & Roadmap**:\n"
            "Our system compares your skills directly against required job postings. "
            "When you view any job in your feed, click **'Skill Gap & Roadmap'** to view curated tutorials, "
            "documentation, and step-by-step learning stages to master missing skills!"
        )
        return {"response": response, "intent": "learning"}

    # Intent 5: How match score works
    if any(w in query_clean for w in ["score", "algorithm", "tfidf", "how it works", "calculate"]):
        response = (
            "🧠 **AI Match Score Algorithm**:\n"
            "Your match percentage is calculated using 3 components:\n"
            "1. **50% Skill Overlap**: Exact matching between your skills & job requirements.\n"
            "2. **30% TF-IDF Cosine Similarity**: AI text vector analysis comparing your resume/bio text against job descriptions.\n"
            "3. **20% Category & Title Fit**: Alignment of job titles and domain specialization."
        )
        return {"response": response, "intent": "algorithm_info"}

    # Default fallback
    response = (
        f"I'm here to help you find your dream job, {user_name}! "
        "Try asking me about your **job recommendations**, **resume tips**, **skill gap analysis**, "
        "or how to **boost your match score**."
    )
    return {"response": response, "intent": "general"}
