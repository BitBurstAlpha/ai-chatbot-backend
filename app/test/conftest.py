import pytest
from app import create_app, db
from flask_jwt_extended import create_access_token
from app.models import User

@pytest.fixture

def app_instance():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgresql://ai-test-db_owner:npg_3CuQ1TIMKBJU@ep-quiet-art-a1bte4xh-pooler.ap-southeast-1.aws.neon.tech/ai-test-db?sslmode=require',  # in-memory DB
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': 'test-secret'
    }
    app = create_app(test_config)
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
    user = User(email="dilshan@gmail.com", password="dilshan")
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return {'user': user, 'token': token}

@pytest.fixture
def auth_header(auth_user):
    return {'Authorization': f'Bearer {auth_user["token"]}'}
