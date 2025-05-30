from db import db

class FileModel(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(220), unique=True, nullable=False)
    path = db.Column(db.String(220), unique=True, nullable=False)