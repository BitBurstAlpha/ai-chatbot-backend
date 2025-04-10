
from flask import jsonify, request
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User
from flask import current_app

from . import api_v1_bp


@api_v1_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    try:
        user_count = User.query.count()
        is_first_admin = (
            email == current_app.config.get("ADMIN_EMAIL") and user_count == 0
        )

        role = "admin" if is_first_admin else "user"
        new_user = User(email=email, password=password, role=role)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to register user", "details": str(e)}), 500
    
# Main Entry Point, To Authenticate Users
@api_v1_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Fetch user from the database
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 401

    print(f"User found: {user.email}")  # Debug print
    print(f"User password hash: {user.password_hash}")  # Debug print

    if not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT Token
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200
