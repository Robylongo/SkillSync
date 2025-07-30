import spacy
from spacy.matcher import PhraseMatcher

# Topic keywords kindly provided by Chatham Grant-Parker-Turner (ChatGPT)
PROGRAMMING_LANGUAGES = [
    # Common
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
    "ruby", "rust", "kotlin", "swift", "perl", "php", "scala", "bash", "shell",
    "objective-c", "dart", "r", "matlab", "lua",
    # Data / Analytics
    "sas", "stata", "julia", "groovy", "fortran", "abap", "powershell",
    "haskell", "ocaml", "clojure"
]

FRAMEWORKS_LIBRARIES = [
    # Backend
    "flask", "django", "fastapi", "spring", "spring boot", "express", "nest.js",
    "rails", "laravel", "symfony", "adonisjs", "hapi", "micronaut",
    # Frontend
    "react", "vue", "angular", "next.js", "nuxt.js", "svelte", "ember.js",
    "gatsby", "preact", "alpine.js",
    # UI/Styling
    "tailwind", "bootstrap", "material-ui", "chakra ui", "ant design", "foundation",
    # State Management
    "redux", "mobx", "vuex", "pinia",
    # Node Ecosystem
    "node.js", "npm", "yarn", "vite", "webpack", "rollup", "parcel",
    "socket.io", "electron",
    # Testing
    "jest", "mocha", "chai", "enzyme", "cypress", "playwright", "puppeteer"
]

DATA_SCIENCE = [
    "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "tensorflow",
    "keras", "pytorch", "openai", "huggingface", "nltk", "spacy", "opencv",
    "cv2", "statsmodels", "xgboost", "lightgbm", "catboost", "mlflow",
    "scipy", "plotly", "dash", "altair", "streamlit", "bokeh",
    "dask", "polars", "ray", "pyarrow", "modin",
    "prophet", "statsforecast",
    # Big Data
    "spark", "pyspark", "hadoop", "databricks", "flink", "kafka"
]

DATABASES = [
    # SQL
    "postgresql", "mysql", "sqlite", "mariadb", "oracle", "mssql",
    # NoSQL
    "mongodb", "redis", "cassandra", "dynamodb", "couchdb", "cosmos db",
    # Graph DB
    "neo4j", "arangodb", "janusgraph",
    # Search / Analytics
    "elasticsearch", "solr", "opensearch",
    # Time Series
    "influxdb", "timescaledb", "questdb",
    # Cloud-hosted
    "firebase", "supabase", "planetscale"
]

CLOUD_DEVOPS = [
    # Cloud
    "aws", "azure", "gcp", "digitalocean", "linode", "oracle cloud", "ibm cloud",
    # Containers & Orchestration
    "docker", "kubernetes", "podman", "openshift", "rancher",
    # CI/CD
    "jenkins", "circleci", "travisci", "github actions", "gitlab ci", "bitbucket pipelines",
    # Infrastructure-as-Code
    "terraform", "ansible", "pulumi", "chef", "saltstack",
    # Web Servers & Hosting
    "nginx", "apache", "vercel", "netlify", "heroku", "render", "fly.io",
    # OS
    "linux", "ubuntu", "debian", "centos", "arch"
]

APIS_PROTOCOLS = [
    "rest", "graphql", "grpc", "soap", "websockets", "mqtt",
    "oauth", "oauth2", "jwt", "saml", "openid connect",
    "openapi", "swagger", "postman", "insomnia", "asyncapi",
    "json", "xml", "protobuf", "avro"
]

SECURITY_TESTING = [
    "unit testing", "integration testing", "pytest", "unittest", "nose",
    "jest", "mocha", "chai", "cypress", "playwright",
    "pen testing", "penetration testing", "ssl", "tls", "https",
    "oauth2", "csrf", "csp", "rate limiting", "vulnerability scanning",
    "burp suite", "owasp zap", "fuzz testing", "sonarqube"
]

TOOLS_MISC = [
    "git", "github", "gitlab", "bitbucket", "svn", "mercurial",
    "postman", "insomnia",
    # IDEs
    "vscode", "pycharm", "intellij", "eclipse", "netbeans", "android studio", "xcode",
    # Productivity
    "jira", "trello", "asana", "notion", "slack", "monday.com", "miro",
    # Design
    "figma", "adobe xd", "sketch", "canva"
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
nlp = None
matcher = None

def get_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    return nlp

def get_matcher():
    global matcher
    if matcher is None:
        nlp_instance = get_nlp()

        matcher_instance = PhraseMatcher(nlp_instance.vocab, attr="LOWER")

        patterns = [nlp_instance.make_doc(skill) for skill in SKILL_LIST]
        sections = [nlp_instance.make_doc(section) for section in SECTION_HEADERS]

        matcher_instance.add("SKILLS", patterns)
        matcher_instance.add("SECTIONS", sections)

        matcher = matcher_instance

    return matcher

def match_skills(text):
    """
    Grabs a list of skills from the provided text. Skills are from the above skill list.
    """
    doc = get_nlp()(text)
    matches = get_matcher()(doc)
    nlp_instance = get_nlp()

    skill_matches =[(label, start, end) for (match_id, start, end) in matches
                    if nlp_instance.vocab.strings[match_id] == "SKILLS"
                    for label in [nlp_instance.vocab.strings[match_id]]]

    found = set()
    for _, start, end in skill_matches:
        span = doc[start:end]
        found.add(span.text.lower())
    return list(found)


def split_sections(text):
    """
    Split the resume into sections based on SECTION_HEADERS, anchored to line starts.
    """
    doc = get_nlp()(text)
    matches = get_matcher()(doc)
    nlp_instance = get_nlp()

    section_matches = []
    for match_id, start, end in matches:
        label = nlp_instance.vocab.strings[match_id]
        if label != "SECTIONS":
            continue
        
        span = doc[start:end]
        char_start = span.start_char
        if char_start == 0 or text[char_start-1] in ["\n", "\r"]:
            section_matches.append((span.text.lower().strip(), start, end))
    
    deduped_matches = []
    seen_starts = {}
    for name, start, end in section_matches:
        if start not in seen_starts or (end - start) > (seen_starts[start][2] - seen_starts[start][1]):
            seen_starts[start] = (name, start, end)
    deduped_matches = list(seen_starts.values())

    deduped_matches.sort(key=lambda x: x[1])

    sections = {}
    for i, (section_name, start, end) in enumerate(deduped_matches):
        next_start = deduped_matches[i+1][1] if i+1 < len(deduped_matches) else len(doc)
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

    skill_gaps = extracted_skills - supported_skills
    extracted_skills, supported_skills = list(set(extracted_skills)), list(set(supported_skills))

    return extracted_skills, supported_skills, list(skill_gaps)
