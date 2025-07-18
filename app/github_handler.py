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
                          languages = get_languages(username, repo_name, access_token), 
                          description = repo_description, 
                          commit_summary = make_commit_summary(username, repo_name, access_token))
        db.session.add(repo)
    db.session.commit()


def get_languages(username, repo_name, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(f"https://api.github.com/repos/{username}/{repo_name}/languages", headers=headers)

    if response.status_code != 200:
        return
    
    languages = response.json()
    total = languages.sum()
    main_languages = {
        language: byte
        for language, byte in languages.items()
        if byte/total >= 0.05
    }
    lang_string = ", ".join(main_languages.keys())
    return lang_string

def make_commit_summary(username, repo_name, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    params = {"per_page": 100}
    commits = []

    while url:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return ""

        data = response.json()
        for commit in data:
            message = commit.get("commit", {}).get("message")
            if message:
                commits.append(message)

        if "next" in response.links:
            url = response.links["next"]["url"]
            params = None
        else:
            break

    # we have commits as a full list of commits
