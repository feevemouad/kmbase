from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn
import os 
import yaml
from src.agent_factory import agent_factory
from src.config import Config, SELECTED_DBS

from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEndpoint 
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_together import ChatTogether


config_path = '../config/config.yml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

try:
    os.environ["LANGCHAIN_TRACING_V2"] = config["langsmith"]["LANGCHAIN_TRACING_V2"]
    os.environ["LANGCHAIN_ENDPOINT"] = config["langsmith"]["LANGCHAIN_ENDPOINT"]
    os.environ["LANGCHAIN_API_KEY"] = config["langsmith"]["LANGCHAIN_API_KEY"]
    os.environ["LANGCHAIN_PROJECT"] = config["langsmith"]["LANGCHAIN_PROJECT"]
except:
    pass

app = FastAPI()

class LLMModel(BaseModel):
    provider: str
    model_name: str
    api_key: Optional[str] = None
    model_id: Optional[str] = None

class DatabaseQueryRequest(BaseModel):
    database_type: str
    database_url: str
    user_question: str
    llm_model: LLMModel

def initialize_llm(llm_model: LLMModel):
        try:
            if llm_model.provider == "ollama":
                return ChatOllama(model=llm_model.model_name, base_url=config["chat_model"]["endpoint"], temperature=0.0)
            
            elif llm_model.provider == "openai":
                return ChatOpenAI(model=llm_model.model_name, temperature=0.1, api_key=llm_model.api_key)
            
            elif llm_model.provider == "huggingface":
                return HuggingFaceEndpoint(repo_id=llm_model.model_id, task="text-generation",
                                                            temperature=0.1,
                                                            huggingfacehub_api_token=llm_model.api_key)
                
            elif llm_model.provider == "groq":
                return ChatGroq(model=llm_model.model_name, api_key=llm_model.api_key, temperature=0.1)
            
            elif llm_model.provider == "together":
                return ChatTogether(together_api_key=llm_model.api_key, model=llm_model.model_name, temperature=0.1)
            
            else:
                raise ValueError(f"Unknown LLM provider: {llm_model.get('provider')}")
            
        except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error initializing LLM: {str(e)}")

@app.post("/query-database")
async def query_database(request: DatabaseQueryRequest):

    if request.database_type.lower() not in SELECTED_DBS:
        raise HTTPException(status_code=400, detail=f"Invalid database type. Supported types are: {', '.join(SELECTED_DBS)}")

    try:
        # Initialize the LLM
        llm = initialize_llm(request.llm_model)

        # Initialize the Config object with the request parameters
        cfg = Config(database_type = request.database_type.lower(), database_url = request.database_url, llm = llm)

        # Create the agent executor
        agent_executor = agent_factory(cfg)

        # Run the query
        result = agent_executor.invoke(request.user_question)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)