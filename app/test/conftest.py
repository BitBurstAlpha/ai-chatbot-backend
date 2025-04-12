import pytest
from app import create_app, db
from flask_jwt_extended import create_access_token
from app.models import User

@pytest.fixture
def app_instance():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

@pytest.fixture
def auth_user(app_instance):
    user = User(email="irosha@gmail.com", password="irosha")
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return {'user': user, 'token': token}

@pytest.fixture
def auth_header(auth_user):
    return {'Authorization': f'Bearer {auth_user["token"]}'}
