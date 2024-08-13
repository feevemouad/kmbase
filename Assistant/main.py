from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Tuple
import uvicorn
import os 
import yaml
import io

from src.chat_model import ChatModel
from src.vector_store import VectorStore

config_path = '../config/config.yml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
    
os.environ["LANGCHAIN_TRACING_V2"]=config["langsmith"]["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_ENDPOINT"]=config["langsmith"]["LANGCHAIN_ENDPOINT"]
os.environ["LANGCHAIN_API_KEY"]=config["langsmith"]["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_PROJECT"]=config["langsmith"]["LANGCHAIN_PROJECT"]


vector_store = VectorStore(config_path, use_cache=True)
app = FastAPI()

class SearchRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    user_input: str
    conversation_history: List[Tuple]
    llm_model : Dict # {"provider": "ollama", "model_name": "llama3.1")}
    
class DatabaseQueryRequest(BaseModel):
    database_type: str
    database_url: str
    user_question: str
    llm_model : Dict

@app.post("/search")
async def search_documents(request: SearchRequest):
    try:
        search_results = vector_store.search(request.query)
        document_names = list(set([doc.metadata['source'] for doc in search_results]))
        return JSONResponse(content={"document_names": document_names})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhookcallback")
async def webhook(request: Request):
    content = await request.json()
    for record in content['Records']:
        event_name = record['eventName']
        bucket_name = record['s3']['bucket']['name']
        object_name = record['s3']['object']['key']

        if "ObjectCreated" in event_name:
            obj_response = vector_store.minio_client.get_object(bucket_name, object_name)
            file_like_data = io.BytesIO(obj_response.read())
            vector_store.add_document(file_like_data, object_name)
        elif "ObjectRemoved" in event_name:
            vector_store.remove_document()

    return JSONResponse(content={"message": "Index updated successfully."})

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        chat_model = ChatModel(vector_store, request.llm_model)
        answer, source_documents = chat_model.generate_response(
            request.user_input,
            request.conversation_history
        )

        sources = [doc.metadata['source'] for doc in source_documents]
 
        return JSONResponse(content={"answer": answer, "source_documents": sources})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/database_query")
async def database_query(request: DatabaseQueryRequest):
    try:
        chat_model = ChatModel( vector_store,
                                request.llm_model,
                                database_chat_model = True
                               )
        result = chat_model.generate_database_response(request.database_type, request.database_url, request.user_question)
        return JSONResponse(content={"answer": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)