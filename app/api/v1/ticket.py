from datetime import datetime, timezone
from flask import jsonify, request
from app.extensions import db
from app.models import Ticket
from app.models.ticket import TicketReply 

from . import api_v1_bp

# This endpoint allows users to create a new ticket.
@api_v1_bp.route('/ticket', methods=['POST'])
def create_ticket():
    data = data = request.get_json()
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
def get_tickets():
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
def update_ticket_status(ticket_id):
    try:
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
def assign_ticket(ticket_id):
    try:
        # Get the agent_id from request body
        data = request.get_json()
        if not data or 'agent_id' not in data:
            return jsonify({'error': 'Missing agent_id in request body'}), 400
        
        agent_id = data['agent_id']
        
        # Find the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Update the agent assignment
        ticket.agent_id = agent_id
        
        # If ticket was in 'open' status, move it to 'in_progress'
        if ticket.status == 'open':
            ticket.status = 'in_progress'
        
        # Update assigned timestamp
        ticket.assigned_at = datetime.now(timezone.utc)
        
        # Commit the changes
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
def unassign_ticket(ticket_id):
    try:
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
def add_ticket_reply(ticket_id):
    try:
        # Get reply data from request body
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
            
        user_id = data.get('user_id')
        agent_id = data.get('agent_id')
        message = data.get('message', '').strip()
        
        # Validate required fields
        if not message:
            return jsonify({'error': 'message is required'}), 400
            
        # Either user_id or agent_id must be provided (not both)
        if not (user_id or agent_id) or (user_id and agent_id):
            return jsonify({'error': 'Either user_id or agent_id must be provided (not both)'}), 400
            
        # Find the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
            
        # Create new reply
        new_reply = TicketReply(
            ticket_id=ticket_id,
            user_id=user_id,
            agent_id=agent_id,
            message=message
        )
        
        # Update ticket status based on who replied
        if agent_id:
            # If agent replied to a resolved ticket, keep it resolved
            if ticket.status != 'resolved':
                ticket.status = 'in_progress'
            ticket.last_agent_reply_at = datetime.now(timezone.utc)
        elif user_id:
            # If user replied to a resolved ticket, move back to in_progress
            if ticket.status == 'resolved':
                ticket.status = 'in_progress'
            ticket.last_user_reply_at = datetime.now(timezone.utc)
        
        # Save the reply and update ticket
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
def get_ticket_replies(ticket_id):
    try:
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
def resolve_ticket(ticket_id):
    try:
        data = request.get_json() or {}
        resolution_note = data.get('resolution_note', '')
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({'error': 'agent_id is required'}), 400
            
        # Find the ticket
        ticket = db.session.query(Ticket).get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
            
        # Check if the agent is assigned to this ticket
        if ticket.agent_id != agent_id:
            return jsonify({'error': 'Only the assigned agent can resolve this ticket'}), 403
            
        # Update ticket status
        ticket.status = 'resolved'
        ticket.resolution_note = resolution_note
        ticket.resolved_at = datetime.utcnow()
        
        # Add a resolution reply if there's a note
        if resolution_note:
            resolution_reply = TicketReply(
                ticket_id=ticket_id,
                agent_id=agent_id,
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
def get_agent_tickets(agent_id):
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