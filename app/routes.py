import os
import requests
from flask import Blueprint, jsonify, redirect, request, session, url_for

bp = Blueprint('main', __name__)

# generalized response formats
def success_response(data, code=200):
    return jsonify(data), code


def failure_response(message, code=404):
    return jsonify({"error": message}), code

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

@bp.route('/')
def nuthin():
    return success_response({"message": "Dummy chill backend"})

@bp.route('/login/github')
def github_login():
    auth_url = "https://github.com/login/oauth/authorize"
    redirect_uri = url_for('main.github_callback', _external=True)

    return redirect(f"{auth_url}?client_id={GITHUB_CLIENT_ID}&redirect_uri={redirect_uri}")

@bp.route('/callback/github')
def github_callback():
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
    session['github_username'] = user_data['login']
    session['access_token'] = access_token

    return jsonify({"message": f"Logged in as {user_data['login']}"})