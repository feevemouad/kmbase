import yaml
import nltk
from nltk.tokenize import sent_tokenize
import re

class TextChunker:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)['text_chunker']
        
        self.chunk_size = self.config['chunk_size']
        self.overlap = self.config['overlap']
        
        nltk.download("punkt", quiet=True)

    def chunk_text(self, text):
        # Split text into paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for paragraph in paragraphs:
            # Split paragraph into sentences
            sentences = sent_tokenize(paragraph)
            
            for sentence in sentences:
                sentence_size = len(sentence)
                
                if current_size + sentence_size > self.chunk_size and current_chunk:
                    # If adding this sentence exceeds the target size, store the current chunk
                    chunks.append(current_chunk.strip())
                    
                    # Start a new chunk with overlap
                    overlap_size = 0
                    overlap_chunk = ""
                    for s in reversed(current_chunk.split('. ')):
                        if overlap_size + len(s) > self.overlap:
                            break
                        overlap_chunk = s + '. ' + overlap_chunk
                        overlap_size += len(s) + 2  # +2 for '. '
                    
                    current_chunk = overlap_chunk + sentence
                    current_size = len(current_chunk)
                else:
                    # Add the sentence to the current chunk
                    current_chunk += ' ' + sentence
                    current_size += sentence_size + 1  # +1 for space
            
            # Add a newline after each paragraph
            current_chunk += '\n\n'
            current_size += 2
        
        # Add the last chunk if it's not empty
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks