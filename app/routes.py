import os
import requests
from flask import Blueprint, jsonify, redirect, request, session, url_for
from .models import User, Repository
from . import db
from .github_handler import github_handler
bp = Blueprint('main', __name__)

# generalized response formats
def success_response(data, code=200):
    """
    Default success response
    """
    return jsonify(data), code


def failure_response(message, code=404):
    """
    Default failure response
    """
    return jsonify({"error": message}), code

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

@bp.route('/')
def nuthin():
    """
    Index route
    """
    return success_response({"message": "Dummy chill backend"})

@bp.route('/users')
def all_user():
    """
    Returns all users.
    """

    users = [user.serialize() for user in User.query.all()]

    return success_response({"users": users})

@bp.route('/<int:user_id>/repos')
def all_repos_for_user(user_id):
    """
    Returns all repos for a user.
    """
    repos = Repository.query.filter_by(user_id=user_id).all()
    repo_list = [repo.serialize() for repo in repos]

    return success_response({"repos": repo_list})

@bp.route('/login/github')
def github_login():
    """
    Redirects the user to Github's OAuth page. Returns a redirect to Githubs authorization endpoint.
    """
    auth_url = "https://github.com/login/oauth/authorize"
    redirect_uri = url_for('main.github_callback', _external=True)

    return redirect(f"{auth_url}?client_id={GITHUB_CLIENT_ID}&redirect_uri={redirect_uri}")

@bp.route('/callback/github')
def github_callback():
    """
    Handles the callback from Github and logs the user in. Returns a response confirming login success.
    """
    code = request.args.get("code")

    response = requests.post("https://github.com/login/oauth/access_token", 
                             headers={"Accept": "application/json"},
                             data = {
                                 "client_id": GITHUB_CLIENT_ID,
                                 "client_secret": GITHUB_CLIENT_SECRET,
                                 "code": code
                             })
    
    token_json = response.json()
    access_token = token_json.get("access_token")
    if not access_token:
        return failure_response("Access token not found", 400)
    
    user_response = requests.get("https://api.github.com/user",
                                 headers={"Authorization": f"token {access_token}"})
    user_data = user_response.json()
    username = user_data['login']
    exists = User.query.filter_by(github_username = username).first()
    if not exists:
        user = User(access_token = access_token, github_username = username)
        db.session.add(user)
        db.session.commit()
    session['github_username'] = username
    session['access_token'] = access_token

    return success_response({"message": f"Logged in as {username}"}, 200)

@bp.route('/github/repos', methods=["POST"])
def github_repos():
    """
    Adds a users repos to the database
    """
    access_token = session.get("access_token")
    username = session.get("github_username")
    if not access_token:
        return failure_response("Unauthorized", 401)
    github_handler(username, access_token)
    return success_response({"message": "successfully added user's repos to the database."})