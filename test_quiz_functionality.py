import pytest
from app import app, db, User, Topic, Quiz, Score, QuizAttempt
from flask import url_for
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def init_database():
    with app.app_context():
        admin = User(username='admin', password=generate_password_hash('admin123'), is_admin=True)
        user = User(username='testuser', password=generate_password_hash('testpass'), is_admin=False)
        db.session.add_all([admin, user])
        db.session.commit()
        return {'admin': admin, 'user': user}

def test_home_redirect(test_client):
    response = test_client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_register(test_client):
    response = test_client.post('/register', data={
        'username': 'newuser',
        'password': 'newpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_login_user(test_client, init_database):
    response = test_client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass',
        'role': 'user'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_admin(test_client, init_database):
    response = test_client.post('/login', data={
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_logout(test_client, init_database):
    test_client.post('/login', data={'username': 'testuser', 'password': 'testpass', 'role': 'user'})
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have logged out' in response.data

def test_create_topic(test_client, init_database):
    test_client.post('/login', data={'username': 'admin', 'password': 'admin123', 'role': 'admin'})
    response = test_client.post('/admin/create_topic', data={'name': 'Math'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Topic added successfully' in response.data

def test_view_quizzes(test_client):
    response = test_client.get('/view_quizzes')
    assert response.status_code == 200
