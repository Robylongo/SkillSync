from . import db
from .models import User, Repository

def github_handler():
    username = "idk"
    # API Call for ALL repos
    user = User.query.filter_by(github_username = username).first()
    repos = []
    for repo in repos:
        repo_name = "idk"
        repo_description = "idk"
        repo = Repository(user_id = user.id, 
                          name = repo_name, 
                          languages = get_languages(repo), 
                          description = repo_description, 
                          commit_summary = make_commit_summary(repo))
    return None


def get_languages(repo):
    return None

def make_commit_summary(repo):
    return None

