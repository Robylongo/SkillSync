import os
from cryptography.fernet import Fernet
from sqlalchemy.ext.hybrid import hybrid_property
from dotenv import load_dotenv

from . import db

load_dotenv()
fernet = Fernet(os.getenv("ENCRYPTION_KEY"))

class User(db.Model):
    """
    User model
    """

    id = db.Column(db.Integer, primary_key=True)
    _access_token = db.Column("access_token", db.LargeBinary)
    github_username = db.Column(db.String(64), nullable = False, unique=True)
    resume_uploaded = db.Column(db.Boolean, default=False)

    # relationship
    repositories = db.relationship("Repository", backref="user",lazy=True)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def serialize(self):
        """
        Serialized version of a user. Includes repositories
        """
        return {
            "id": self.id,
            "github_username": self.github_username,
            "resume_uploaded": self.resume_uploaded,
            "repositories": [reps.serialize() for reps in self.repositories]
        }
    
    @hybrid_property
    def access_token(self):
        if self._access_token:
            return fernet.decrypt(self._access_token).decode()
        return None
    
    @access_token.setter
    def access_token(self, token_plaintext):
        self._access_token = fernet.encrypt(token_plaintext.encode())

class Repository(db.Model):
    """
    Model to store a user's repositories, with a summary of their commit messages.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String)
    languages = db.Column(db.JSON, default=list)
    description = db.Column(db.String, nullable=True)
    commit_summary = db.Column(db.JSON, default=list)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def serialize(self):
        return {
            "id" : self.id,
            "name": self.name,
            "languages": self.languages,
            "description": self.description,
            "commit_summary": self.commit_summary
        }

class ResumeData(db.Model):
    """
    Model to store a user's resume
    """
    id = db.Column(db.Integer, primary_key=True)
    og_filename = db.Column(db.String)
    extracted_skills = db.Column(db.JSON, nullable=True)
    supported_skills = db.Column(db.JSON, nullable=True)
    skill_gaps = db.Column(db.JSON, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", backref="resume_data")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def serialize(self):
        return {
            "id": self.id,
            "og_filename": self.og_filename,
            "extracted_skills": self.extracted_skills,
            "supported_skills": self.supported_skills,
            "skill_gaps": self.skill_gaps,
            "user_id": self.user_id
        }