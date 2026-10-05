from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Profile, Project
from services.recommendation_service import get_recommendations_for_user, compute_hybrid_match_score
from services.learning_service import analyze_skill_gap, generate_learning_roadmap
from utils.responses import success_response, error_response

recommendation_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")


@recommendation_bp.route("/jobs", methods=["GET"])
@jwt_required()
def get_job_recommendations():
    user_id = get_jwt_identity()
    limit = request.args.get("limit", default=20, type=int)

    recommendations = get_recommendations_for_user(user_id=user_id, limit=limit)
    return success_response(
        "AI job recommendations retrieved successfully",
        data={
            "count": len(recommendations),
            "recommendations": recommendations
        }
    )


@recommendation_bp.route("/skill-gap/<int:project_id>", methods=["GET"])
@jwt_required()
def get_skill_gap_analysis(project_id):
    user_id = get_jwt_identity()
    analysis = analyze_skill_gap(user_id=user_id, project_id=project_id)

    if "error" in analysis:
        return error_response(analysis["error"], 44)

    return success_response(
        "Skill gap analysis generated",
        data=analysis
    )


@recommendation_bp.route("/learning-roadmap/<int:project_id>", methods=["GET"])
@jwt_required()
def get_learning_roadmap(project_id):
    user_id = get_jwt_identity()
    gap_data = analyze_skill_gap(user_id=user_id, project_id=project_id)

    if "error" in gap_data:
        return error_response(gap_data["error"], 404)

    missing_skills = gap_data.get("missing_skills", [])
    roadmap = generate_learning_roadmap(missing_skills)

    return success_response(
        "Personalized learning roadmap generated",
        data={
            "project_id": project_id,
            "project_title": gap_data["project_title"],
            "match_percentage": gap_data["match_percentage"],
            "roadmap": roadmap
        }
    )
