
import os
import io
import yaml
import faiss
import pickle
import numpy as np
from minio import Minio

from .document_processor import DocumentProcessor
from .embedding_model import EmbeddingModel
from .text_chunker import TextChunker


class VectorStore:
    def __init__(self, config_path, use_index_stub=True, stubs_path =  '../Stubs/vector_index_stub.pkl'):
        print("Initializing VectorStore")
        self.config_path = config_path
        self.use_index_stub = use_index_stub
        self.index_stub_path = stubs_path
        
        self.initialize_from_config()
        
        if self.use_index_stub and self.load_index_from_stub():
            print("Loaded index from stub")
        else:
            self.initialize_index()
            if self.use_index_stub:
                self.save_index_to_stub()

    def initialize_from_config(self):
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.dimension = self.config['vector_store']['dimension']
        
        self.minio_client = Minio(
            self.config['minio']['endpoint'],
            access_key=self.config['minio']['access_key'],
            secret_key=self.config['minio']['secret_key'],
            secure=self.config['minio']['secure']
        )
        
        self.document_processor = DocumentProcessor(self.config_path)
        self.embedding_model = EmbeddingModel(self.config_path)
        self.text_chunker = TextChunker(self.config_path)
        
        self.create_index()

    def create_index(self):
        print("Creating index")
        quantizer = faiss.IndexFlatL2(self.dimension)
        self.index = faiss.IndexIDMap(quantizer)
        self.id_to_chunk = {}
        self.next_id = 0

    def initialize_index(self):
        print("Initializing index")
        docs_bucket = self.config['minio']['docs_bucket']
        objects = self.minio_client.list_objects(docs_bucket)
        print("Parsing objects")
        for obj in objects:
            obj_response = self.minio_client.get_object(docs_bucket, obj.object_name)
            file_like_data = io.BytesIO(obj_response.read())
            self.add_document(file_like_data, obj.object_name)

    def add_document(self, file_data, object_name):
        print(f"-----processing {object_name}------")
        text_content = self.document_processor.process_document(file_data)
        print("chunking", object_name)
        chunks = self.text_chunker.chunk_text(text_content)
        print("generating embeddings for", object_name)
        embeddings = self.embedding_model.get_embeddings(chunks)
        self.add_embeddings(embeddings, chunks, object_name)
        print(f"-----{object_name} done -----")

    def add_embeddings(self, embeddings, chunks, object_name):
        print("add", object_name, "embeddings to vector database")
        if len(embeddings) != len(chunks):
            raise ValueError("Number of embeddings must match number of chunks")

        ids = np.arange(self.next_id, self.next_id + len(embeddings), dtype='int64')
        self.index.add_with_ids(np.array(embeddings).astype('float32'), ids)

        for id, chunk in zip(ids, chunks):
            self.id_to_chunk[int(id)] = {
                'chunk': chunk,
                'object_name': object_name
            }

        self.next_id += len(embeddings)

    def search(self, query_embedding, k=5):
        query_embedding = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for i, idx in enumerate(indices[0]):
            chunk_info = self.id_to_chunk.get(int(idx))
            if chunk_info:
                chunk = chunk_info.get('chunk')
                object_name = chunk_info.get('object_name')
                if chunk and object_name:
                    results.append({
                        'distance': float(distances[0][i]),
                        'chunk': chunk,
                        'object_name': object_name
                    })
        return results

    def __len__(self):
        return self.index.ntotal

    def remove_document(self, object_name):
        ids_to_remove = [id for id, info in self.id_to_chunk.items() if info['object_name'] == object_name]
        if ids_to_remove:
            self.index.remove_ids(np.array(ids_to_remove))
            for id in ids_to_remove:
                del self.id_to_chunk[id]

    def update_document(self, file_data, object_name):
        self.remove_document(object_name)
        self.add_document(file_data, object_name)

    def load_index_from_stub(self):
        if os.path.exists(self.index_stub_path):
            try:
                with open(self.index_stub_path, 'rb') as f:
                    index_data = pickle.load(f)
                self.index = index_data['index']
                self.id_to_chunk = index_data['id_to_chunk']
                self.next_id = index_data['next_id']
                return True
            except Exception as e:
                print(f"Error loading index from stub: {e}")
        return False

    def save_index_to_stub(self):
        try:
            index_data = {
                'index': self.index,
                'id_to_chunk': self.id_to_chunk,
                'next_id': self.next_id
            }
            with open(self.index_stub_path, 'wb') as f:
                pickle.dump(index_data, f)
            print("Saved index to stub")
        except Exception as e:
            print(f"Error saving index to stub: {e}")

# # src/vector_store.py

# import io
# import faiss
# import numpy as np
# import yaml
# from minio import Minio

# from .document_processor import DocumentProcessor
# from .embedding_model import EmbeddingModel
# from .text_chunker import TextChunker

# class VectorStore:
#     def __init__(self, config_path):
#         print ("Initializing VectorStore")
#         with open(config_path, 'r') as f:
#             self.config = yaml.safe_load(f)
        
#         self.dimension = self.config['vector_store']['dimension']
        
#         self.minio_client = Minio(
#             self.config['minio']['endpoint'],
#             access_key=self.config['minio']['access_key'],
#             secret_key=self.config['minio']['secret_key'],
#             secure=self.config['minio']['secure']
#         )
        
#         self.document_processor = DocumentProcessor(config_path)
#         self.embedding_model = EmbeddingModel(config_path)
#         self.text_chunker = TextChunker(config_path)
        
#         self.create_index()
#         self.initialize_index()

#     def create_index(self):
#         print("Creating index")
#         quantizer = faiss.IndexFlatL2(self.dimension)
#         self.index = faiss.IndexIDMap(quantizer)
#         self.id_to_chunk = {}
#         self.next_id = 0

#     def initialize_index(self):
#         print ("Initializing index")
#         docs_bucket = self.config['minio']['docs_bucket']
#         objects = self.minio_client.list_objects(docs_bucket)
#         print("Parsing objects")
#         for obj in objects:
#             obj_response  = self.minio_client.get_object(docs_bucket, obj.object_name)
#             file_like_data = io.BytesIO(obj_response.read())
#             self.add_document(file_like_data, obj.object_name)

#     def add_document(self, file_data, object_name):
#         print (f"-----processing{object_name}------")
#         print ("processing",object_name)
#         text_content = self.document_processor.process_document(file_data)
#         print ("chunking",object_name)
#         chunks = self.text_chunker.chunk_text(text_content)
#         print ("generating embeddings for",object_name)
#         embeddings = self.embedding_model.get_embeddings(chunks)
#         self.add_embeddings(embeddings, chunks, object_name)
#         print (f"-----{object_name}done -----")

#     def add_embeddings(self, embeddings, chunks, object_name):
#         print ("add ",object_name," embeddings to vector database")
#         if len(embeddings) != len(chunks):
#             raise ValueError("Number of embeddings must match number of chunks")

#         ids = np.arange(self.next_id, self.next_id + len(embeddings), dtype='int64')
#         self.index.add_with_ids(np.array(embeddings).astype('float32'), ids)

#         for id, chunk in zip(ids, chunks):
#             self.id_to_chunk[int(id)] = {
#                 'chunk': chunk,
#                 'object_name': object_name
#             }

#         self.next_id += len(embeddings)

#     def search(self, query_embedding, k=5):
#         query_embedding = np.array([query_embedding]).astype('float32')
#         distances, indices = self.index.search(query_embedding, k)
#         results = []
#         for i, idx in enumerate(indices[0]):
#             chunk_info = self.id_to_chunk.get(int(idx))
#             if chunk_info:
#                 chunk = chunk_info.get('chunk')
#                 object_name = chunk_info.get('object_name')
#                 if chunk and object_name:
#                     results.append({
#                         'distance': float(distances[0][i]),
#                         'chunk': chunk,
#                         'object_name': object_name
#                     })
#         return results

    
#     def __len__(self):
#         return self.index.ntotal

#     def remove_document(self, object_name):
#         ids_to_remove = [id for id, info in self.id_to_chunk.items() if info['object_name'] == object_name]
#         if ids_to_remove:
#             self.index.remove_ids(np.array(ids_to_remove))
#             for id in ids_to_remove:
#                 del self.id_to_chunk[id]

#     def update_document(self, file_data, object_name):
#         self.remove_document(object_name)
#         self.add_document(file_data, object_name)