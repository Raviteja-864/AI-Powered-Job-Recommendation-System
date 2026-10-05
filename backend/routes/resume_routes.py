import os
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from extensions import db
from models import User, Profile, Skill, FreelancerSkill
from services.nlp_service import extract_text_from_file, extract_skills_from_text
from utils.responses import success_response, error_response

resume_bp = Blueprint("resume", __name__, url_prefix="/api/resume")

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)

    if "resume" not in request.files:
        return error_response("No resume file uploaded", 400)

    file = request.files["resume"]
    if file.filename == "":
        return error_response("No selected file", 400)

    if not allowed_file(file.filename):
        return error_response("Invalid file extension. Allowed: PDF, DOCX, TXT", 400)

    # Ensure uploads directory exists
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_folder = os.path.join(backend_dir, "uploads", "resumes")
    os.makedirs(upload_folder, exist_ok=True)

    filename = secure_filename(f"user_{user_id}_{file.filename}")
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    try:
        # Extract text using NLP service
        extracted_text = extract_text_from_file(file_path)

        # Get existing master skills
        master_skills = [s.name for s in Skill.query.all()]

        # NLP Skill Extraction
        extraction_result = extract_skills_from_text(extracted_text, custom_skills=master_skills)
        found_skills = extraction_result["skills"]

        # Ensure user profile exists
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = Profile(user_id=user_id)
            db.session.add(profile)
            db.session.flush()

        profile.resume_filename = filename
        profile.extracted_text = extracted_text

        # Automatically associate extracted skills with freelancer profile
        newly_added_skills = []
        for skill_name in found_skills:
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.session.add(skill)
                db.session.flush()

            existing_fs = FreelancerSkill.query.filter_by(profile_id=profile.id, skill_id=skill.id).first()
            if not existing_fs:
                fs = FreelancerSkill(profile_id=profile.id, skill_id=skill.id)
                db.session.add(fs)
                newly_added_skills.append(skill_name)

        db.session.commit()

        return success_response(
            "Resume uploaded and skills successfully extracted via NLP!",
            data={
                "filename": filename,
                "raw_text_length": len(extracted_text),
                "extracted_skills": found_skills,
                "newly_added_skills": newly_added_skills,
                "total_profile_skills": [s.skill.name for s in profile.skills]
            },
            status_code=200
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error processing resume: {str(e)}", 500)


@resume_bp.route("/parsed", methods=["GET"])
@jwt_required()
def get_parsed_resume():
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile or not profile.resume_filename:
        return error_response("No resume uploaded yet", 404)

    return success_response(
        "Parsed resume data retrieved",
        data={
            "resume_filename": profile.resume_filename,
            "extracted_text_preview": (profile.extracted_text[:500] + "...") if profile.extracted_text else "",
            "skills": [s.skill.name for s in profile.skills] if profile.skills else []
        }
    )
