from pathlib import Path
from flask import jsonify, request
from app.extensions import db
from app.models import Chatbot
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.chatbot import ChatbotKnowledge
from app.models.knowledge import KnowledgeBase
from app.models.user import User

from . import api_v1_bp

@api_v1_bp.route('/chatbot', methods=['POST'])
@jwt_required()
def createChatbot(): 
    """Fetch knowledge base entries."""
    current_user_id = get_jwt_identity()

    user = db.session.query(User).get(current_user_id)

    data = request.get_json() or {}

    title = data.get('title')

    if not title :
        return jsonify({"error": "Title is required"}), 400

    try:
        # Check if the user is an admin
        if user.role != 'user':
            return jsonify({"error": "you haven't permission access this"}), 403

        # Create database entry
        new_entry = Chatbot(
            title=title,
            user_id=current_user_id,
        )
        db.session.add(new_entry)
        db.session.commit()
        
        return jsonify({
            'id': str(new_entry.id),
            'title': new_entry.title,
            'user_id': new_entry.user_id,
            'created_at': new_entry.created_at.isoformat() if new_entry.created_at else None
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@api_v1_bp.route('/chatbot', methods=['GET'])
@jwt_required()
def getChatbots():
    """Fetch chatbots for the current user."""
    current_user_id = get_jwt_identity()


    try:

        user = db.session.query(User).get(current_user_id)

        if user.role != 'user':
            return jsonify({"error": "you haven't permission access this"}), 403


        chatbots = db.session.query(Chatbot).filter_by(user_id=current_user_id).all()

        chatbot_list = [{
            'id': str(chatbot.id),
            'name': chatbot.title,
            'trained': 'TRAINED',
            'status' : 'LIVE',
        } for chatbot in chatbots]

        return jsonify(chatbot_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_v1_bp.route('/chatbot/<uuid:chatbot_id>', methods=['GET'])
@jwt_required()
def getChatbotById(chatbot_id):
    """Fetch chatbots for the current user."""
    current_user_id = get_jwt_identity()


    try:

        user = db.session.query(User).get(current_user_id)

        if user.role != 'user':
            return jsonify({"error": "you haven't permission access this"}), 403


        chatbot = db.session.query(Chatbot).filter_by(id=chatbot_id, user_id=current_user_id).first()
        if not chatbot:
            return jsonify({"error": "Chatbot not found or unauthorized"}), 404
        
        chatbot_data = {
            'id': str(chatbot.id),
            'name': chatbot.title,
            'trained': 'TRAINED',
            'status' : 'LIVE',
        }
        return jsonify(chatbot_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@api_v1_bp.route('/chatbot/<uuid:chatbot_id>/knowledge', methods=['POST'])
@jwt_required()
def addKnowledgeToChatbot(chatbot_id):
    """Add a knowledge base entry to a chatbot."""
    current_user_id = get_jwt_identity()

    try:
        user = db.session.query(User).get(current_user_id)

        if user.role != 'user':
            return jsonify({"error": "you haven't permission access this"}), 403

        chatbot = db.session.query(Chatbot).filter_by(id=chatbot_id, user_id=current_user_id).first()
        if not chatbot:
            return jsonify({"error": "Chatbot not found or unauthorized"}), 404

        data = request.get_json() or {}
        knowledge_id = data.get('knowledge_id')

        if not knowledge_id:
            return jsonify({"error": "knowledge_id is required"}), 400

        # Check if the knowledge base item belongs to this user
        knowledge = db.session.query(KnowledgeBase).filter_by(id=knowledge_id, user_id=current_user_id).first()
        if not knowledge:
            return jsonify({"error": "Knowledge entry not found or unauthorized"}), 404

        # Create the ChatbotKnowledge entry
        new_knowledge = ChatbotKnowledge(
            chatbot_id=chatbot_id,
            knowledge_id=knowledge_id
        )

        db.session.add(new_knowledge)
        db.session.commit()

        return jsonify({
            "id": str(new_knowledge.id),
            "chatbot_id": str(new_knowledge.chatbot_id),
            "knowledge_id": new_knowledge.knowledge_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
