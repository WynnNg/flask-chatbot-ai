import uuid
from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import openai
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
from dotenv import load_dotenv
import os
import asyncio


from lightRAG import RAG
from reflection import Reflection
from db import db

import nest_asyncio
nest_asyncio.apply()

blp = Blueprint("chatbot", __name__, description="Operations on chatbot")

# Load environment variables from .env file
load_dotenv()
# Access the key
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')

os.environ["OPENAI_API_KEY"] = OPEN_AI_KEY

# --- Relection Setup --- #
gpt = openai.OpenAI(api_key=OPEN_AI_KEY)
reflection = Reflection(llm=gpt)
# --- End Reflection Setup --- #

WORKING_DIR="./rag_storage"

# Initialize lightRAG
async def initialize_light_rag():
    light_rag = RAG(
        WORKING_DIR,
        openai_embed,
        gpt_4o_mini_complete,
    )
    # await light_rag.init_async()
    return light_rag

def process_query(query):
    return query.lower()

@blp.route("/chat")
class Chatbot(MethodView):
    async def post(self):
        data = list(request.get_json())
       
        query = data[-1]["parts"][0]["text"]

        if not query:
            abort(400, message="No query provided")

        # query = process_query(query)

        reflected_query = reflection(data)
        # Here you would typically process the user message and generate a response.
        
        simple_prompt = f"""<SYS>Bạn là chuyên gia tư vấn bán hàng của Thương hiệu BOTSLAB.
        Bạn là một nhân viên lễ phép luôn bắt đầu đoạn hội thoại bằng từ Dạ và kết thúc bằng từ ạ. 
        Bạn xưng em với khách hàng. Bạn luôn trả lời bằng tiếng Việt. Chỉ sử dung thông tin các sản phẩm của BOTSLAB đã được cung cấp.</SYS>
        Tin nhắn của khách hàng: {reflected_query}
        """

        # Initialize lightRAG
        light_rag = await initialize_light_rag()

        response = await light_rag.perform_rag(
            query=simple_prompt,
            mode="hybrid"
        )

        data.append({
            "role": "user",
            "parts": [
                {
                    "text": simple_prompt,
                }
            ]
        })


        return jsonify({
        'parts': [
            {
            'text': response,    
            }
        ],
        'role': 'model'
        }), 200
    
