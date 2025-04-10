
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.extensions import db
from app.models.user import User
from flask import current_app

from . import api_v1_bp

@api_v1_bp.route('/user/agent', methods=['POST'])
@jwt_required()
def create_agent():
    data = request.get_json() or {}

    # Get current user
    current_user_id = get_jwt_identity()

    user = db.session.query(User).get(current_user_id)

    # Check if the user is an admin
    if user.role != 'admin':
        return jsonify({"error" : "you can't create agent"}), 403

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    try:
       
        new_user = User(email=email, password=password, role="agent")

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to register user", "details": str(e)}), 500