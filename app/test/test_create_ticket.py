def test_successful_ticket_creation(client, auth_user, auth_header):
    payload = {
        "user_id": str(auth_user["user"].id),
        "query": "System is not responding"
    }
    response = client.post('/api/v1/ticket', json=payload, headers=auth_header)
    assert response.status_code == 201
    data = response.get_json()
    assert 'ticket_id' in data
    assert data['status'] == 'open'

def test_missing_required_field(client, auth_user, auth_header):
    payload = {
        "user_id": str(auth_user["user"].id)
        # Missing 'query'
    }
    response = client.post('/api/v1/ticket', json=payload, headers=auth_header)

    assert response.status_code == 400
    assert response.get_json()['error'] == 'query is required'

def test_unauthenticated_user(client):
    payload = {
        "user_id": "123",
        "query": "Help needed"
    }
    response = client.post('/api/v1/ticket', json=payload)

    assert response.status_code == 401
    assert "msg" in response.get_json()