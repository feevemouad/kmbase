from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import os 
import yaml
import io

from src.chat_model import ChatModel
from src.vector_store import VectorStore

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"]="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"
os.environ["LANGCHAIN_PROJECT"]="kbasellms"

config_path = '../config/config.yml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

vector_store = VectorStore(config_path, use_cache=True)
chat_model = ChatModel(vector_store)

app = FastAPI()

class SearchRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    user_input: str
    conversation_history: List[Dict]

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
        answer, source_documents = chat_model.generate_response(
            request.user_input,
            request.conversation_history
        )

        sources = [doc.metadata['source'] for doc in source_documents]
 
        return JSONResponse(content={"answer": answer, "source_documents": sources})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)