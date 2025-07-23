import pytest
from app import create_app
from app.models import User, db, Repository
from unittest.mock import patch

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_slash_route(client):
    """
    Tests that the index route works
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.is_json
    assert response.json["message"] == "Dummy chill backend"

def test_encryption(client, app):
    """
    Tests that the encryption works
    """

    with app.app_context():
        user = User(github_username = "mcalero123", access_token = "TPAB")
        db.session.add(user)
        db.session.commit()

        gotten_user = User.query.filter_by(github_username = "mcalero123").first()
        assert gotten_user.access_token == "TPAB"
        assert gotten_user._access_token != b"TPAB"
        assert isinstance(gotten_user._access_token, bytes)

def test_serialize(client, app):
    """
    Tests that the serialize function returns a proper dictionary
    """
    with app.app_context():
        user = User(github_username = "mcalero123", access_token = "TPAB")
        db.session.add(user)
        db.session.commit()

        data = user.serialize()
        assert "id" in data
        assert "github_username" in data
        assert "access_token" not in data