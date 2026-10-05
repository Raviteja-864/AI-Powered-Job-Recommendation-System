from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.chatbot_service import process_chatbot_query
from utils.responses import success_response, error_response

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")


@chatbot_bp.route("/query", methods=["POST"])
@jwt_required()
def chatbot_query():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    query = data.get("query") or data.get("message")
    if not query:
        return error_response("Query string is required", 400)

    result = process_chatbot_query(user_id=user_id, query=query)
    return success_response(
        "Chatbot response generated",
        data=result
    )
