import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import setup_logger
import PyPDF2

class RAG:
    def __init__(self, working_dir, embedding_func, llm_model_func):
        
        self.working_dir = working_dir
        self.embedding_func = embedding_func
        self.llm_model_func = llm_model_func

        if not os.path.exists(self.working_dir):
            os.mkdir(self.working_dir)
    
    setup_logger("lightrag", level="INFO")

    async def init_async(self):
        await self.prepare_data()
        return self

    async def initialize_rag(self):
        rag = LightRAG(
            working_dir=self.working_dir,
            embedding_func=self.embedding_func,
            llm_model_func=self.llm_model_func,
        )
        await rag.initialize_storages()
        await initialize_pipeline_status()
        return rag

    async def prepare_data(self, input_path, out_path):
        rag = await self.initialize_rag()
        try:
            # Open the PDF and extract the Text
            pdf_text = []
            with open(f"./{input_path}", "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    pdf_text.append(page.extract_text())

            # Save (Write) a file with the data
            with open(f"./{out_path}", "w", encoding="utf-8") as file:
                for line in pdf_text:
                    file.write(f"{line}\n")
            
            with open(f"./{out_path}", "r", encoding="utf-8") as file:
                rag.insert(file.read())
                
            return {"message": "File insert successfully!"}
        except:
            return {"error" : "file can't insert"}

        
    
    async def perform_rag(self, query, mode):
        rag = await self.initialize_rag()

        response = rag.query(
            query = query,
            param = QueryParam(
                mode = mode,
                response_type="Multiple Paragraphs",
                user_prompt= f"""<SYS>Bạn là chuyên gia tư vấn bán hàng của Thương hiệu STEELMATE. 
                Trả lời đầy đủ thông tin. Không cần kèm nguồn tham khảo trong câu trả lời.</SYS>"""
            )
        )
        return response