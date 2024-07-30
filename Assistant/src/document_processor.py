import io
from tika import parser
import yaml

class DocumentProcessor:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def process_document(self, obj_response ):
        obj_bytes = obj_response.read()
        file_like = io.BytesIO(obj_bytes)
        parsed_file = parser.from_buffer(file_like)
        return parsed_file["content"]
