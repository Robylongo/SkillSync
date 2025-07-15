from . import db

class User(db.Model):
    """
    User model
    TBD
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    access_token = db.Columnd(db.String(64), nullable = False, unique = True)
    github_username = db.Column(db.String(64), nullable = False, unique=True)
    resume_uploaded = db.Column(db.Boolean, default=False)
