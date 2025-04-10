from datetime import datetime, timezone
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models import Ticket
from app.models.ticket import TicketReply
from app.models.user import User 

from . import api_v1_bp

# This endpoint allows users to create a new ticket.
@api_v1_bp.route('/ticket', methods=['POST'])
@jwt_required()
def create_ticket():
    data = data = request.get_json()

    # Get current user
    current_user_id = get_jwt_identity()

    user = db.session.query(User).get(current_user_id)

    # Check if the user is an admin
    if user.role != 'user':
        return jsonify({"error": "You admins, are not authorized to perform this action! Only Users can create tickets"}), 403

    if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
    
    user_id = data.get('user_id', '').strip()
    query = data.get('query', '').strip()

    # Validate required fields
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    if not query:
        return jsonify({'error': 'query is required'}), 400

    try:
        new_ticket = Ticket(user_id=user_id, query=query)
        db.session.add(new_ticket)
        db.session.commit()

        return jsonify({
            'message': 'Ticket created successfully',
            'ticket_id': str(new_ticket.id),
            'status': new_ticket.status
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create ticket', 'details': str(e)}), 500

@api_v1_bp.route('/tickets', methods=['GET'])
@jwt_required()
def get_tickets():

     # Get current user
    current_user_id = get_jwt_identity()

    user = db.session.query(User).get(current_user_id)

    # Check if the user is an admin
    if user.role != 'admin':
        return jsonify({"error": "you haven't permission access this"}), 403

    status = request.args.get('status')
    assigned = request.args.get('assigned')

    ticket_query = db.session.query(Ticket)

    # Filter by status if provided
    if status:
        ticket_query = ticket_query.filter(Ticket.status == status)

    # Filter by agent assignment
    if assigned is not None:
        if assigned.lower() == 'true':
            ticket_query = ticket_query.filter(Ticket.agent_id.isnot(None))
        elif assigned.lower() == 'false':
            ticket_query = ticket_query.filter(Ticket.agent_id.is_(None))
        else:
            return jsonify({'error': 'Invalid value for "assigned". Use true or false.'}), 400

    tickets = ticket_query.order_by(Ticket.id.desc()).all()

    ticket_list = [
        {
            'ticket_id': str(t.id),
            'user_id': t.user_id,
            'query': t.query,
            'status': t.status,
            'agent_id': t.agent_id
        }
        for t in tickets
    ]

    return jsonify(ticket_list), 200

@api_v1_bp.route('/tickets/<ticket_id>/status', methods=['PUT'])
@jwt_required()
def update_ticket_status(ticket_id):
    try:
        
         # Get current user
        current_user_id = get_jwt_identity()

        user = db.session.query(User).get(current_user_id)

        # Check if the user is an admin
        if user.role != 'admin':
            return jsonify({"error": "you haven't permission access this"}), 403

        # Get the new status from request body
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Missing status in request body'}), 400
            
        new_status = data['status']
        
        # Validate the status value (optional, add your valid statuses)
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Find the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
            
        # Update the status
        ticket.status = new_status
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'ticket_id': str(ticket.id),
            'status': ticket.status,
            'message': 'Ticket status updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update ticket status: {str(e)}'}), 500
    
@api_v1_bp.route('/tickets/<ticket_id>/assign', methods=['PUT'])
@jwt_required()
def assign_ticket(ticket_id):
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(current_user_id)

        if not user:
            return jsonify({'error': 'Unauthorized user'}), 403

        # Check user role
        if user.role not in ['admin', 'agent']:
            return jsonify({'error': "You don't have permission to assign tickets"}), 403

        # Find the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        # Admin assigns to another agent
        if user.role == 'admin':
            data = request.get_json()
            agent_id = data.get('agent_id') if data else None

            if not agent_id:
                return jsonify({'error': 'Missing agent_id in request body'}), 400

            assigned_agent = db.session.query(User).get(agent_id)
            if not assigned_agent or assigned_agent.role != 'agent':
                return jsonify({'error': 'Invalid agent_id'}), 400

            ticket.agent_id = agent_id

        # Agent assigns the ticket to themselves
        elif user.role == 'agent':
            ticket.agent_id = current_user_id

        # Update ticket status if open
        if ticket.status == 'open':
            ticket.status = 'in_progress'

        # Set assignment timestamp
        ticket.assigned_at = datetime.now(timezone.utc)

        # Commit changes
        db.session.commit()

        return jsonify({
            'ticket_id': str(ticket.id),
            'agent_id': ticket.agent_id,
            'status': ticket.status,
            'message': 'Agent assigned successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to assign agent: {str(e)}'}), 500



@api_v1_bp.route('/tickets/<ticket_id>/unassign', methods=['PUT'])
@jwt_required()
def unassign_ticket(ticket_id):
    try:

        # Get current user
        current_user_id = get_jwt_identity()

        user = db.session.query(User).get(current_user_id)

        # Check if the user is an admin
        if user.role != 'admin':
            return jsonify({"error": "you haven't permission access this"}), 403
        # Find the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Check if ticket is already unassigned
        if ticket.agent_id is None:
            return jsonify({'error': 'Ticket is not assigned to any agent'}), 400
        
        # Unassign the agent
        ticket.agent_id = None
        
        # Reset to open status if it was in progress
        if ticket.status == 'in_progress':
            ticket.status = 'open'
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'ticket_id': str(ticket.id),
            'status': ticket.status,
            'message': 'Agent unassigned successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to unassign agent: {str(e)}'}), 500
    


@api_v1_bp.route('/tickets/<ticket_id>/replies', methods=['POST'])
@jwt_required()
def add_ticket_reply(ticket_id):
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(current_user_id)

        # Validate user role
        if user.role not in ['user', 'agent']:
            return jsonify({"error": "You don't have permission to access this"}), 403

        # Parse and validate request JSON
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400

        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Fetch the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        # Create the reply
        new_reply = TicketReply(
            ticket_id=ticket_id,
            user_id=current_user_id if user.role == "user" else None,
            agent_id=current_user_id if user.role == "agent" else None,
            message=message
        )

        # Update ticket status and timestamps
        if user.role == "agent":
            if ticket.status != 'resolved':
                ticket.status = 'in_progress'
            ticket.last_agent_reply_at = datetime.now(timezone.utc)
        else:  # user.role == "user"
            if ticket.status == 'resolved':
                ticket.status = 'in_progress'
            ticket.last_user_reply_at = datetime.now(timezone.utc)

        # Save changes
        db.session.add(new_reply)
        db.session.commit()

        return jsonify({
            'message': 'Reply added successfully',
            'reply_id': str(new_reply.id),
            'ticket_id': str(ticket.id),
            'ticket_status': ticket.status
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add reply: {str(e)}'}), 500
    
# Get all replies for a ticket
@api_v1_bp.route('/tickets/<ticket_id>/replies', methods=['GET'])
@jwt_required()
def get_ticket_replies(ticket_id):
    try:

       # Get current user
        current_user_id = get_jwt_identity()

        user = db.session.query(User).get(current_user_id)

        # Check if the user is an user
        if user.role != 'admin':
            return jsonify({"error": "you haven't permission access this"}), 403

        # Find the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
            
        # Get all replies for the ticket, ordered by creation time
        replies = db.session.query(TicketReply).filter(
            TicketReply.ticket_id == ticket_id
        ).order_by(TicketReply.created_at).all()
        
        reply_list = [
            {
                'reply_id': str(r.id),
                'ticket_id': str(r.ticket_id),
                'user_id': r.user_id,
                'agent_id': r.agent_id,
                'message': r.message,
                'created_at': r.created_at.isoformat(),
                'is_agent_reply': r.agent_id is not None
            }
            for r in replies
        ]
        
        return jsonify(reply_list), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get replies: {str(e)}'}), 500

# Mark a ticket as resolved (by agent)
@api_v1_bp.route('/tickets/<ticket_id>/resolve', methods=['PUT'])
@jwt_required()
def resolve_ticket(ticket_id):
    try:

        # Get current user
        current_user_id = get_jwt_identity()

        user = db.session.query(User).get(current_user_id)

        # Check if the user is an admin
        if user.role != 'agent':
            return jsonify({"error": "you haven't permission access this"}), 403

        data = request.get_json() or {}
        
        resolution_note = data.get('resolution_note', '')
       
            
        # Find the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404

        print(f"Ticket found: {ticket.agent_id}")  # Debug print
        print(f"Current user: {current_user_id}")  # Debug print
        # Check if the agent is assigned to this ticket
        if ticket.agent_id != current_user_id:
            return jsonify({'error': 'Only the assigned agent can resolve this ticket'}), 403
            
        # Update ticket status
        ticket.status = 'resolved'
        ticket.resolution_note = resolution_note
        ticket.resolved_at = datetime.utcnow()
        
        # Add a resolution reply if there's a note
        if resolution_note:
            resolution_reply = TicketReply(
                ticket_id=ticket_id,
                agent_id=current_user_id,
                message=f"Resolution: {resolution_note}"
            )
            db.session.add(resolution_reply)
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'ticket_id': str(ticket.id),
            'status': ticket.status,
            'message': 'Ticket resolved successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to resolve ticket: {str(e)}'}), 500
    
# Get tickets assigned to a specific agent
@api_v1_bp.route('/agents/<agent_id>/tickets', methods=['GET'])
@jwt_required()
def get_agent_tickets(agent_id):

    # Get current user
    current_user_id = get_jwt_identity()

    user = db.session.query(User).get(current_user_id)

    # Check if the user is an admin
    if user.role != 'admin':
        return jsonify({"error": "you haven't permission access this"}), 403

    status = request.args.get('status')
    
    ticket_query = db.session.query(Ticket).filter(Ticket.agent_id == agent_id)
    
    # Filter by status if provided
    if status:
        ticket_query = ticket_query.filter(Ticket.status == status)
    
    tickets = ticket_query.order_by(Ticket.last_user_reply_at.desc().nullslast(), Ticket.id.desc()).all()
    
    ticket_list = [
        {
            'ticket_id': str(t.id),
            'user_id': t.user_id,
            'query': t.query,
            'status': t.status,
            'created_at': t.created_at.isoformat() if t.created_at else None,
            'last_user_reply_at': t.last_user_reply_at.isoformat() if t.last_user_reply_at else None
        }
        for t in tickets
    ]
    
    return jsonify(ticket_list), 200