from . import db
from .models import User, Repository
import requests

def github_handler(username, access_token):
    # API Call for ALL repos
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get("https://api.github.com/user/repos", headers=headers)

    user = User.query.filter_by(github_username = username).first()

    if response.status_code != 200 or not user:
        return
    repos = response.json()
    for repo in repos:
        fork = repo.get("fork")
        if fork:
            continue
        repo_name = repo.get("name")
        repo_description = repo.get("description")
        repo = Repository(user_id = user.id, 
                          name = repo_name, 
                          languages = get_languages(repo), 
                          description = repo_description, 
                          commit_summary = make_commit_summary(repo))
        db.session.add(repo)
        db.session.commit()
    db.session.commit()


def get_languages(repo):
    return None

def make_commit_summary(repo):
    return None

