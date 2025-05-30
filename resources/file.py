import uuid
import os
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from db import db
from models import FileModel
from schemas import FileSchema

UPLOAD_DIRECTORY = 'uploads/'

blp = Blueprint("Files", __name__, description="Operations on files")

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blp.route("/file/<string:file_id>")
class File(MethodView):
    @blp.response(200, FileSchema)
    def get(self, file_id):
        item = FileModel.query.get_or_404(file_id)
        return item
    
    def delete(self, file_id):
        file = FileModel.query.get_or_404(file_id)
        # Xóa file khỏi hệ thống tệp
        if os.path.exists(file.path):
            os.remove(file.path)

        db.session.delete(file)
        db.session.commit()

        return {"message": "File Deleted"}

@blp.route("/file")
class FileList(MethodView):
    @blp.response(200, FileSchema(many=True))
    def get(self):
        return FileModel.query.all()

    def post(self):
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)
        
        uploaded_file = request.files['file']
            
        if uploaded_file and allowed_file(uploaded_file.filename):
            destination = os.path.join(UPLOAD_DIRECTORY, secure_filename(uploaded_file.filename))
            uploaded_file.save(destination)
            file = FileModel(name=secure_filename(uploaded_file.filename), path=destination)
            db.session.add(file)
            db.session.commit()

        return {"data" : "File uploaded successfully", "file_name": uploaded_file.filename, "id": file.id}, 201
        

    

    
    
