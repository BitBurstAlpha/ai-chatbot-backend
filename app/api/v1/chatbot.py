import os
from pathlib import Path
import uuid
from flask import jsonify, request
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Chatbot
from flask_jwt_extended import jwt_required, get_jwt_identity

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