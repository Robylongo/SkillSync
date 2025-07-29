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
    "git", "github", "gitlab", "postman"
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

SECTION_HEADERS = [
    "skills", # key, important
    "experience",
    "work experience",
    "projects",
    "project experience"
]

# spaCy PhraseMatcher initialization
nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(skill) for skill in SKILL_LIST]
sections = [nlp.make_doc(section) for section in SECTION_HEADERS]
matcher.add("SKILLS", patterns)
matcher.add("SECTIONS", sections)

def match_skills(text):
    """
    Grabs a list of skills from the provided text. Skills are from the above skill list.
    """
    doc = nlp(text)
    matches = matcher(doc)
    skill_matches =[(label, start, end) for (match_id, start, end) in matches
                    if nlp.vocab.strings[match_id] == "SKILLS"
                    for label in [nlp.vocab.strings[match_id]]]

    found = set()
    for _, start, end in skill_matches:
        span = doc[start:end]
        found.add(span.text.lower())
    return list(found)


def split_sections(text):
    """
    Split the resume into sections based on the list SECTION_HEADERS.
    """
    doc = nlp(text)
    matches = matcher(doc)

    section_matches = [(label, start, end) for (match_id, start, end) in matches
                    if nlp.vocab.strings[match_id] == "SECTIONS"
                    for label in [nlp.vocab.strings[match_id]]]
    
    section_matches.sort(key=lambda x: x[1])

    sections = {}
    for i, (_, start, end) in enumerate(section_matches):
        section_name = doc[start:end].text.lower()
        next_start = section_matches[i+1][1] if i+1 < len(section_matches) else len(doc)
        sections[section_name] = doc[end:next_start].text.strip()
    
    return sections


def resume_parser(text):
    """
    extract skills...
    """
    sections = split_sections(text)
    extracted_skills, supported_skills = set(), set()

    for section, sec_text in sections.items():
        found_skills = set(match_skills(sec_text))
        extracted_skills |= found_skills 
        if section != "skills":
            supported_skills |= found_skills

    extracted_skills, supported_skills = list(set(extracted_skills)), list(set(supported_skills))
    skill_gaps = extracted_skills - supported_skills

    return extracted_skills, supported_skills, skill_gaps
