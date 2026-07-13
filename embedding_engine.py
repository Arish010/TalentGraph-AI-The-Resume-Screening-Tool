import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class EmbeddingEngine:
    """Handles generating transformer embeddings and calculating semantic similarity scores."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str):
        """Encodes text into a dense vector embedding."""
        if not text.strip():
            raise ValueError("Text content cannot be empty for embedding generation.")
        return self.model.encode(text)

    def calculate_similarity(self, resume_embedding, jd_embedding) -> float:
        """Computes the cosine similarity score between a resume and a job description."""
        res_vector = resume_embedding.reshape(1, -1)
        jd_vector = jd_embedding.reshape(1, -1)
        
        score = cosine_similarity(res_vector, jd_vector)[0][0]
        return float(score)