import spacy
from spacy.matcher import PhraseMatcher

PROGRAMMING_LANGUAGES = [
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
    "ruby", "rust", "kotlin", "swift", "perl", "php", "scala", "bash"
]
FRAMEWORKS_LIBRARIES = [
    "flask", "django", "fastapi", "spring", "express", "react", "vue",
    "angular", "next.js", "svelte", "rails", "laravel", "tailwind", "bootstrap",
    "node.js", "jquery", "redux", "vite", "socket.io"
]
DATA_SCIENCE = [
    "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "tensorflow",
    "keras", "pytorch", "openai", "huggingface", "nltk", "spacy", "cv2",
    "statsmodels", "xgboost", "lightgbm", "mlflow"
]
DATABASES = [
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "cassandra", "dynamodb",
    "oracle", "neo4j", "elasticsearch", "firebase"
]
CLOUD_DEVOPS = [
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "circleci",
    "github actions", "terraform", "ansible", "nginx", "apache", "vercel",
    "netlify", "heroku", "linux"
]
APIS_PROTOCOLS = [
    "rest", "graphql", "grpc", "soap", "websockets", "oauth", "jwt",
    "openapi", "swagger", "postman"
]
SECURITY_TESTING = [
    "unit testing", "integration testing", "pytest", "jest", "mocha", "chai",
    "pen testing", "ssl", "oauth2", "csrf", "csp", "rate limiting",
    "vulnerability scanning"
]
TOOLS_MISC = [
    "git", "github", "gitlab", "bitbucket", "jira", "notion", "figma",
    "postman", "vscode", "vim", "intellij", "pycharm", "excel", "command line"
]

SKILL_LIST = (
    PROGRAMMING_LANGUAGES +
    FRAMEWORKS_LIBRARIES +
    DATA_SCIENCE +
    DATABASES +
    CLOUD_DEVOPS +
    APIS_PROTOCOLS +
    SECURITY_TESTING +
    TOOLS_MISC
)

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp(skill) for skill in SKILL_LIST]
matcher.add("SKILLS", patterns)

def match_skills(text):
    doc = nlp(text)
    matches = matcher(doc)

    found = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        found.add(span.text.lower())
    return list(found)

def resume_parser(resume):
    """
    extract skills
    """
    return None