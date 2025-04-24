import os
from pathlib import Path
import uuid
from flask import current_app, jsonify, request
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.knowledge import KnowledgeBase
from app.models.user import User
from app.service.rag_service import generate_rag_response
from app.service.storage_service import upload_to_s3
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api_v1_bp

@api_v1_bp.route('/knowledge', methods=['GET'])
@jwt_required()
def get_knowledge():
    """Fetch knowledge base entries."""
    current_user_id = get_jwt_identity()

    user = db.session.query(User).get(current_user_id)

    try:
        if user.role == 'admin':
            # Admin: get all entries
            knowledge_entries = db.session.query(KnowledgeBase).all()
        elif user.role == 'user':
            # Normal user: get only their own entries
            knowledge_entries = db.session.query(KnowledgeBase).filter_by(user_id=current_user_id).all()
        else:
            return jsonify({"error": "Unauthorized role"}), 403

        return jsonify([{
            'id': entry.id,
            'title': entry.title,
            'user_id': entry.user_id,
            'description': entry.description,
            'original_filename': entry.original_filename,
            'file_type': entry.file_type,
            'file_size': entry.file_size,
            'created_at': entry.created_at.isoformat() if entry.created_at else None
        } for entry in knowledge_entries])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# This endpoint allows users to create a new ticket.
@api_v1_bp.route('/knowledge/upload', methods=['POST'])
@jwt_required()
def upload_file():

    # Get current user
    current_user_id = get_jwt_identity()

    user = db.session.query(User).get(current_user_id)

    if user.role != 'user':
            return jsonify({"error": "you haven't permission access this"}), 403

    """Upload a file to the knowledge base."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    title = request.form.get('title', 'Untitled')
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Check file extension
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    
    if file and allowed_file(file.filename):
        # Generate unique ID and secure filename
        knowledge_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)

    
    if file and allowed_file(file.filename):
        try:
            # Generate unique ID and secure filename
            knowledge_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            
            # Create temp directory if it doesn't exist
            temp_path = Path(current_app.config['TEMP_FOLDER'], filename)
            temp_path.mkdir(parents=True, exist_ok=True)
        

            # Use Path for proper cross-platform path handling
            temp_path = temp_path / filename
            
            # Save temporarily
            file.save(str(temp_path))
            
            # Get file size
            file_size = os.path.getsize(temp_path)
            
            # Get file type
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            # Create S3 key
            s3_key = f"knowledge/{knowledge_id}/{filename}"
            
            # Create database entry
            new_entry = KnowledgeBase(
                id=knowledge_id,
                title=title,
                description=description,
                s3_key=s3_key,
                original_filename=filename,
                file_type=file_type,
                file_size=file_size,
                user_id=current_user_id,
            )
            db.session.add(new_entry)
            
            # Upload to S3
            if upload_to_s3(str(temp_path), s3_key):
                db.session.commit()
                
                # Clean up temp file
                os.remove(temp_path)
                
                return jsonify({
                    "success": True, 
                    "id": knowledge_id
                }), 200
            else:
                db.session.rollback()
                os.remove(temp_path)
                return jsonify({"error": "Failed to upload to S3"}), 500
            
        except Exception as e:
            # Handle any errors
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

@api_v1_bp.route('/query', methods=['POST'])
def query():
    """Process query against knowledge base."""
    # Get parameters from request
    data = request.json or {}
    query_text = data.get('query')
    knowledge_ids = data.get('knowledge_ids', [])
    
    # If parameters are in query string (for compatibility)
    if not query_text:
        query_text = request.args.get('query')
    if not knowledge_ids:
        knowledge_ids = request.args.getlist('knowledge_ids') or \
                        (request.args.get('knowledge_ids', '').split(',') if request.args.get('knowledge_ids') else [])
    
    # Validate parameters
    if not query_text:
        return jsonify({"error": "Query is required"}), 400
    
    if not knowledge_ids:
        return jsonify({"error": "At least one knowledge source must be selected"}), 400
    
    try:
        # Generate RAG response
        response = generate_rag_response(query_text, knowledge_ids)
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500