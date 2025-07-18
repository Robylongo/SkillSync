from . import db
from .models import User, Repository
import requests

# Topic keywords kindly provided by Chatham Grant-Parker-Turner (ChatGPT)
TOPIC_KEYWORDS = {
    # 🧪 Testing
    "testing": [
        "test", "tests", "pytest", "unittest", "coverage", "assert"
    ],

    # 🔐 Authentication & Authorization
    "auth": [
        "auth", "login", "logout", "register", "signup", "signin", "token", "oauth", "jwt", "session"
    ],

    # 🌐 API Design / Backend
    "api design": [
        "api", "endpoint", "route", "jsonify", "request", "response", "rest", "handler", "query param", "http"
    ],

    # 🧩 Frontend
    "frontend": [
        "ui", "ux", "css", "html", "navbar", "layout", "style", "button", "design", "react", "component"
    ],

    # 🗃️ Database
    "database": [
        "db", "model", "schema", "migration", "sql", "sqlite", "postgres", "mysql", "query", "orm", "foreign key", "relationship"
    ],

    # ⚙️ DevOps / Infrastructure
    "devops": [
        "docker", "container", "build", "ci", "pipeline", "deployment", "heroku", "nginx", "server", "infrastructure"
    ],

    # 🧼 Refactoring / Optimization
    "refactoring": [
        "refactor", "cleanup", "optimize", "simplify", "rename", "extract", "restructure", "performance"
    ],

    # 📦 Package Management
    "dependencies": [
        "requirement", "dependency", "install", "update package", "pip", "npm", "yarn", "package.json", "setup.py"
    ],

    # 🪲 Bug Fixes
    "bugfix": [
        "fix", "bug", "error", "issue", "patch", "broken", "crash", "exception", "debug"
    ],

    # 🛡️ Security
    "security": [
        "vulnerability", "secure", "encryption", "validation", "hash", "csrf", "xss", "injection", "sanitization", "exploit"
    ],

    # 🧠 Machine Learning / Data Science
    "machine learning": [
        "model", "train", "ml", "sklearn", "regression", "classifier", "tensorflow", "pytorch", "fit", "predict", "inference", "dataset"
    ],

    # 📊 Data Engineering
    "data engineering": [
        "etl", "data", "pipeline", "ingest", "transform", "load", "csv", "parquet", "bigquery", "dataset", "dataframe"
    ],

    # 📈 Analytics / Logging
    "analytics": [
        "log", "track", "event", "metric", "analytics", "insight", "report", "monitor", "dashboard"
    ],

    # 🧪 QA / Documentation
    "documentation": [
        "readme", "doc", "docs", "comment", "guide", "instruction", "howto", "markdown"
    ],

    # 🧪 CI/CD (Explicit)
    "cicd": [
        "ci", "cd", "workflow", "github actions", "pipeline", "automate", "deployment"
    ]
}






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
