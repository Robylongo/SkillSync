import os
import requests
from flask import Blueprint, jsonify, redirect, request, session, url_for, render_template
from .models import User, Repository, ResumeData
from . import db
from .github_handler import github_handler
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os 
from wtforms.validators import InputRequired
from .resume_checker import resume_parser
import fitz
from docx import Document
import io

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
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

def allowed_file(filename):
    """
    Checks if a file has the allowed extension.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(filename, byte_content):
    """
    Extracts text from the document depending on what type of extension it has.
    """
    try:

        if filename.lower().endswith(".pdf"):
            with fitz.open(stream=byte_content, filetype="pdf") as doc:
                text = "".join(page.get_text() for page in doc)
        elif filename.lower().endswith(".docx"):
            file_stream = io.BytesIO(byte_content)
            document = Document(file_stream)
            text = "\n".join([para.text for para in document.paragraphs])
        elif filename.lower().endswith(".txt"):
            text = byte_content.decode("utf-8")
    except Exception as e:
        print("Failed to parse resume:", e)
        text = ""
    
    return text

class UploadFileForm(FlaskForm):
    """
    Class to allow for file uploads on the frontend.
    """
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

upload_folder = "static/files"

@bp.route('/')
def nuthin():
    """
    Index route
    """
    return render_template("index.html")


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

@bp.route('/<int:user_id>/resume')
def user_resume(user_id):
    """
    Return the users resume details
    """
    resumes = ResumeData.query.filter_by(user_id=user_id).all()
    resume_list = [resume.serialize() for resume in resumes]
    return success_response({"resume(s)": resume_list})

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
    return redirect(url_for("main.dashboard"))


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

@bp.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    username = session.get("github_username")
    if not username:
        return redirect(url_for("main.github_login"))
    user = User.query.filter_by(github_username=username).first()
    existing_resume = ResumeData.query.filter_by(user_id=user.id).first()

    form = UploadFileForm()

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename.lower())

        if not allowed_file(filename):
            return "Invalid file type. Upload a PDF, DOCX, or TXT."

        byte_content = file.read()
        save_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            upload_folder,
            f"{user.id}_{filename}"
        )
        if existing_resume and os.path.exists(existing_resume.og_filename):
            os.remove(existing_resume.og_filename)
        
        file.save(save_path)

        
        text = extract_text(filename, byte_content)
        if text == "":
            return "Resume could not be parsed"

        extracted_skills, supported_skills, skill_gaps = resume_parser(text)

        if existing_resume:
            # Overwrite fields on existing record
            existing_resume.og_filename = save_path
            existing_resume.extracted_skills = extracted_skills
            existing_resume.supported_skills = supported_skills
            existing_resume.skill_gaps = skill_gaps
        else:
            # Create new record
            new_resume = ResumeData(
                user_id=user.id,
                og_filename=filename,
                extracted_skills=extracted_skills,
                supported_skills=supported_skills,
                skill_gaps=skill_gaps
            )
            user.resume_uploaded = True
            db.session.add(new_resume)

        db.session.commit()

    return render_template("dashboard.html", username=username, form=form)




# RECOMMENDER. WORK IN PROGRESS
@bp.route('/recommendations', methods=["POST"])
def recommendations():
    username = session.get("github_username")
    if not username:
        return failure_response("Unauthorized", 401)
    
    # Example: run skill recommender logic
    user = User.query.filter_by(github_username=username).first()
    resume_data = ResumeData.query.filter_by(user_id=user.id).first()
    if not resume_data:
        return failure_response("No resume found", 400)

    # recs = skill_recommender(resume_data) 
    # return success_response({"recommendations": recs})