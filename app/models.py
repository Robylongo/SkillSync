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
    TBD
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    _access_token = db.Column("access_token", db.LargeBinary)
    github_username = db.Column(db.String(64), nullable = False, unique=True)
    resume_uploaded = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def serialize(self):
        return {
            "id": self.id,
            "github_username": self.github_username,
            "resume_uploaded": self.resume_uploaded
        }
    
    @hybrid_property
    def access_token(self):
        if self._access_token:
            return fernet.decrypt(self._access_token).decode()
        return None
    
    @access_token.setter
    def access_token(self, token_plaintext):
        self._access_token = fernet.encrypt(token_plaintext.encode())