import os
import json
import logging
from typing import List, Dict, Any, Tuple
import faiss
import numpy as np
from app.config import settings
from app.services.embeddings import EmbeddingService

logger = logging.getLogger("healthsutra.retrieval")

class VectorStoreService:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = VectorStoreService()
        return cls._instance

    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        self.metadata_path = settings.CHUNKS_METADATA_PATH
        self.embedding_service = EmbeddingService.get_instance()
        self.index = None
        self.chunks: List[Dict[str, Any]] = []
        self._load_or_init()

    def _load_or_init(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                logger.info(f"Loading existing FAISS index from {self.index_path}")
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                logger.info(f"Loaded {self.index.ntotal} vectors and {len(self.chunks)} chunk metadata records.")
            except Exception as e:
                logger.error(f"Error loading FAISS index ({e}). Initializing empty index.")
                self._init_empty()
        else:
            self._init_empty()

    def _init_empty(self):
        # 384 dimensions for paraphrase-multilingual-MiniLM-L12-v2
        self.index = faiss.IndexFlatIP(384)
        self.chunks = []
        logger.info("Initialized empty FAISS IndexFlatIP(384).")

    def add_chunks(self, new_chunks: List[Dict[str, Any]]) -> int:
        if not new_chunks:
            return 0

        texts = [c["content"] for c in new_chunks]
        embeddings = self.embedding_service.encode(texts)

        self.index.add(embeddings)
        self.chunks.extend(new_chunks)
        self.save()
        logger.info(f"Indexed {len(new_chunks)} new chunks. Total indexed: {self.index.ntotal}")
        return len(new_chunks)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes semantic search against FAISS index.
        Returns chunk dicts with 'score' key.
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Search called on empty FAISS index.")
            return []

        query_vector = self.embedding_service.encode(query)
        scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = dict(self.chunks[idx])
            chunk["score"] = float(score)
            results.append(chunk)

        return results

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        logger.info("FAISS index and metadata saved to disk.")
