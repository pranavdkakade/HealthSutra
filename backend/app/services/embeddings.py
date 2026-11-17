import os
import logging
from typing import List, Union
import numpy as np
from app.config import settings

# Prefer local cached weights to avoid online commit checks in sandboxed environments
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

logger = logging.getLogger("healthsutra.embeddings")

class EmbeddingService:
    _instance = None
    _model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EmbeddingService()
        return cls._instance

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self._load_model()

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading multilingual embedding model: {self.model_name}...")
                try:
                    self._model = SentenceTransformer(self.model_name, local_files_only=True)
                except Exception:
                    self._model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load sentence-transformers model ({e}). Lazy loading on first query.")
                self._model = None

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generates L2-normalized dense vector embeddings.
        Inner product on normalized vectors corresponds to Cosine Similarity.
        """
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)

        if isinstance(texts, str):
            texts = [texts]

        embeddings = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.astype("float32")
