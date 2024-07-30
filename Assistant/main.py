import io
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import your custom classes
from src.chat_model import ChatModel
from src.embedding_model import EmbeddingModel
from src.vector_store import VectorStore

config_path = '../config/config.yaml'
# Initialize your components
embedding_model = EmbeddingModel(config_path)
vector_store = VectorStore(config_path)
chat_model = ChatModel(config_path)

app = FastAPI()

class SearchRequest(BaseModel):
    query: str

class DocumentNameResponse(BaseModel):
    document_names: list
    
class ChatRequest(BaseModel):
    user_input: str
    context : str
    system_prompt : str


@app.post("/search")
async def search_documents(request: SearchRequest):
    query = request.query
    try:
        query_embedding = embedding_model.get_embeddings([query])[0]
        search_results = vector_store.search(query_embedding)
        document_names = list(set([result['object_name'] for result in search_results]))
        return JSONResponse(content={"document_names": document_names})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhookcallback")
async def webhook(request: Request):
    content = await request.json()
    # try:
    for record in content['Records']:
        event_name = record['eventName']
        bucket_name = record['s3']['bucket']['name']
        object_name = record['s3']['object']['key']

        if "ObjectCreated" in event_name:
            # Download the file from Minio
            obj_response = vector_store.minio_client.get_object(bucket_name, object_name)
            obj_bytes = obj_response.read()
            file_like_data = io.BytesIO(obj_bytes)
            # Add the document to the vector store
            vector_store.add_document(file_like_data, object_name)
        elif "ObjectRemoved" in event_name:
            vector_store.remove_document(object_name)

        return JSONResponse(content={"message": "Index updated successfully."})
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/chat")
async def chat(request: ChatRequest):
    system_prompt = request.system_prompt
    context = request.context
    user_input = request.user_input
    try:
        # Embed the user input
        embedded_query = embedding_model.get_embeddings([user_input])[0]
        # Perform the search
        search_results = vector_store.search(embedded_query, k=2)
        # Extract relevant chunks and their object names from search results
        relevant_chunks_with_sources = [
            {"chunk": result['chunk'], "source": result['object_name']}
            for result in search_results
        ]
        # Generate response using ChatModel
        chatbot_response = chat_model.generate_response(system_prompt, context,  user_input, relevant_chunks_with_sources)

        return JSONResponse(content={"response": chatbot_response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
