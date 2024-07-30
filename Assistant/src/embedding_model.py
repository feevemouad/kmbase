import numpy as np
import yaml
import requests

class EmbeddingModel:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['embedding_model']
        
        self.endpoint = self.config['endpoint']
        self.model_name = self.config['model_name']

    def get_embeddings(self, texts):
        embeddings = []
        for text in texts:
            response = requests.post(
                f"{self.endpoint}",
                json={"model": self.model_name, "prompt": text}
            )
            if response.status_code == 200:
                embeddings.append(np.array(response.json()['embedding']))
            else:
                raise Exception(f"Error getting embedding: {response.text}")
        return embeddings