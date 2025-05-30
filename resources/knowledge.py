import uuid
import os
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv
import asyncio
import openai
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed

from db import db
from models import FileModel
from schemas import FileSchema
from lightRAG import RAG

import nest_asyncio
nest_asyncio.apply()

blp = Blueprint("Knowledge", __name__, description="Operations on knowledge")

# Load environment variables from .env file
load_dotenv()
# Access the key
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')

os.environ["OPENAI_API_KEY"] = OPEN_AI_KEY

WORKING_DIR="./rag_storage"
KNOWLEDGE_DIRECTORY="knowledge/"
# Initialize lightRAG
async def initialize_light_rag(input_path, output_path):
    light_rag = RAG(
        WORKING_DIR,
        openai_embed,
        gpt_4o_mini_complete,
    )

    response = await light_rag.prepare_data(input_path, output_path)
    # await light_rag.init_async()
    return response

@blp.route("/knowledge/<string:file_id>")
class Knowledge(MethodView):
    async def get(self, file_id):
        try:
            item = FileModel.query.get_or_404(file_id)
            input_path = item.path
            output_path = os.path.join(KNOWLEDGE_DIRECTORY, f"{item.name.rsplit('.', 1)[0]}.txt")
            
            # Đặt timeout cho tác vụ bất đồng bộ
            async with asyncio.timeout(240):  # Timeout 240 giây
            # Initialize lightRAG
                response = await initialize_light_rag(input_path, output_path)

            return response

        except asyncio.TimeoutError:
            abort(504, message="Request timed out after 240 seconds")
        except Exception as e:
            abort(500, message=f"An error occurred: {str(e)}")