import os
import pickle
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from minio import Minio
from tika import parser
import yaml

class VectorStore:
    def __init__(self, config_path, use_cache=True):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.use_cache = use_cache
        self.minio_client = Minio(
            self.config['minio']['endpoint'],
            access_key=self.config['minio']['access_key'],
            secret_key=self.config['minio']['secret_key'],
            secure=self.config['minio']['secure']
        )
        
        self.embeddings = OllamaEmbeddings(
            model=self.config['embedding_model']['model_name']
        )
        self.chunker = CharacterTextSplitter(chunk_size=self.config["text_chunker"]["chunk_size"], chunk_overlap=self.config["text_chunker"]["chunk_overlap"])
        self.vector_store = None
        self.cache_file = self.config.get('vector_store', {}).get('cache_file', 'faiss_index_cache.pkl')
        
        if use_cache and os.path.exists(self.cache_file):
            self.load_index_from_cache()
        else:
            self.initialize_index()
        if os.path.exists(self.cache_file):
            self.save_index_to_cache()
        
    def process_document(self, file_data):
        parsed = parser.from_buffer(file_data)
        return parsed["content"]

    def chunk_text(self, text):
        return self.chunker.split_text(text)

    def initialize_index(self):
        print("Initializing index from scratch...")
        docs_bucket = self.config['minio']['docs_bucket']
        documents = []
        for obj in self.minio_client.list_objects(docs_bucket):
            obj_response = self.minio_client.get_object(docs_bucket, obj.object_name)
            content = self.process_document(obj_response)
            chunks = self.chunk_text(content)
            for chunk in chunks:
                documents.append(Document(page_content=chunk, metadata={"source": obj.object_name}))
        
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        print("Index initialization complete.")
        self.retriever = self.vector_store.as_retriever(search_kwargs={'k': 5})

    def save_index_to_cache(self):
        print(f"Saving index to cache: {self.cache_file}")
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.vector_store, f)

    def load_index_from_cache(self):
        print(f"Loading index from cache: {self.cache_file}")
        with open(self.cache_file, "rb") as f:
            self.vector_store = pickle.load(f)
        self.retriever = self.vector_store.as_retriever(search_kwargs={'k': 5})

    def add_document(self, file_data, object_name):
        content = self.process_document(file_data)
        chunks = self.chunk_text(content)
        documents = [Document(page_content=chunk, metadata={"source": object_name}) for chunk in chunks]
        self.vector_store.add_documents(documents)
        self.save_index_to_cache()  # Update cache after adding new document

    def search(self, query, k=5):
        return self.vector_store.similarity_search(query, k=k)

    def remove_document(self):
        self.initialize_index()
        if self.use_cache:
            self.save_index_to_cache()
        
    def update_document(self, file_data, object_name):
        self.remove_document(object_name)
        self.add_document(file_data, object_name)
        self.save_index_to_cache()  # Update cache after updating document