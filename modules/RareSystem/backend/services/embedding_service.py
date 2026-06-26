"""
Embedding Service - Vector embedding generation and FAISS index management.

Provides:
- Text embedding generation using sentence-transformers
- FAISS index building and management
- Similarity search for RAG retrieval
"""
import logging
import pickle
import os
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
INDEX_PATH = "data/faiss_index"


@dataclass
class SearchResult:
    document_id: int
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EmbeddingResult:
    document_id: int
    embedding: np.ndarray
    text: str


class EmbeddingServiceError(Exception):
    pass


class ModelNotLoadedError(EmbeddingServiceError):
    pass


class IndexNotBuiltError(EmbeddingServiceError):
    pass


class EmbeddingService:
    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL_NAME,
        dimension: int = EMBEDDING_DIMENSION,
        index_path: str = INDEX_PATH
    ):
        self._model_name = model_name
        self._dimension = dimension
        self._index_path = index_path
        self._model = None
        self._index = None
        self._id_mapping: Dict[int, int] = {}
        self._document_cache: Dict[int, str] = {}

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self._model_name}")
                self._model = SentenceTransformer(self._model_name)
                logger.info("Embedding model loaded successfully")
            except ImportError as e:
                raise ModelNotLoadedError(
                    f"sentence-transformers not installed: {e}. "
                    "Install with: pip install sentence-transformers"
                )
            except Exception as e:
                raise ModelNotLoadedError(f"Failed to load model: {e}")
        return self._model

    def _init_faiss(self):
        if self._index is None:
            try:
                import faiss
                self._index = faiss.IndexFlatIP(self._dimension)
                logger.info(f"FAISS index initialized with dimension {self._dimension}")
            except ImportError as e:
                raise IndexNotBuiltError(
                    f"faiss not installed: {e}. "
                    "Install with: pip install faiss-cpu"
                )
        return self._index

    def generate_embedding(self, text: str) -> np.ndarray:
        model = self._load_model()
        embedding = model.encode([text], convert_to_numpy=True)
        return embedding[0]

    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        model = self._load_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings

    def add_document(
        self,
        document_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        index = self._init_faiss()
        embedding = self.generate_embedding(content)
        embedding = embedding.astype(np.float32).reshape(1, -1)
        
        faiss_id = len(self._id_mapping)
        self._id_mapping[faiss_id] = document_id
        self._document_cache[document_id] = content
        
        index.add(embedding)
        logger.debug(f"Added document {document_id} to index at position {faiss_id}")
        return True

    def add_documents_batch(
        self,
        documents: List[Tuple[int, str, Optional[Dict[str, Any]]]]
    ) -> int:
        if not documents:
            return 0
        
        index = self._init_faiss()
        texts = [doc[1] for doc in documents]
        embeddings = self.generate_embeddings_batch(texts)
        embeddings = embeddings.astype(np.float32)
        
        start_id = len(self._id_mapping)
        for i, (doc_id, content, _) in enumerate(documents):
            faiss_id = start_id + i
            self._id_mapping[faiss_id] = doc_id
            self._document_cache[doc_id] = content
        
        index.add(embeddings)
        logger.info(f"Added {len(documents)} documents to index")
        return len(documents)

    def search(
        self,
        query: str,
        k: int = 5,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        index = self._init_faiss()
        
        if index.ntotal == 0:
            logger.warning("Index is empty, no results")
            return []
        
        query_embedding = self.generate_embedding(query)
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        
        k = min(k, index.ntotal)
        scores, indices = index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or score < min_score:
                continue
            
            document_id = self._id_mapping.get(int(idx))
            if document_id is None:
                continue
            
            content = self._document_cache.get(document_id, "")
            results.append(SearchResult(
                document_id=document_id,
                content=content,
                score=float(score),
                metadata=None
            ))
        
        return results

    def search_with_metadata(
        self,
        query: str,
        documents: Dict[int, Tuple[str, Dict[str, Any]]],
        k: int = 5,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        base_results = self.search(query, k=k * 2, min_score=min_score)
        
        results = []
        for result in base_results:
            if result.document_id in documents:
                content, metadata = documents[result.document_id]
                results.append(SearchResult(
                    document_id=result.document_id,
                    content=content,
                    score=result.score,
                    metadata=metadata
                ))
        
        return results[:k]

    def remove_document(self, document_id: int) -> bool:
        if document_id in self._document_cache:
            del self._document_cache[document_id]
            logger.debug(f"Removed document {document_id} from cache")
            return True
        return False

    def clear_index(self) -> bool:
        self._index = None
        self._id_mapping.clear()
        self._document_cache.clear()
        logger.info("Cleared FAISS index")
        return True

    def get_index_size(self) -> int:
        if self._index is None:
            return 0
        return self._index.ntotal

    def save_index(self, path: Optional[str] = None) -> bool:
        import faiss
        
        path = path or self._index_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        if self._index is None:
            logger.warning("No index to save")
            return False
        
        faiss.write_index(self._index, f"{path}.index")
        
        with open(f"{path}.mapping", "wb") as f:
            pickle.dump({
                "id_mapping": self._id_mapping,
                "document_cache": self._document_cache
            }, f)
        
        logger.info(f"Saved index to {path}")
        return True

    def load_index(self, path: Optional[str] = None) -> bool:
        import faiss
        
        path = path or self._index_path
        
        if not os.path.exists(f"{path}.index"):
            logger.warning(f"Index file not found: {path}.index")
            return False
        
        self._index = faiss.read_index(f"{path}.index")
        
        with open(f"{path}.mapping", "rb") as f:
            data = pickle.load(f)
            self._id_mapping = data["id_mapping"]
            self._document_cache = data["document_cache"]
        
        logger.info(f"Loaded index from {path} with {self._index.ntotal} documents")
        return True

    def get_document_count(self) -> int:
        return len(self._document_cache)


def create_embedding_service(
    model_name: str = EMBEDDING_MODEL_NAME,
    dimension: int = EMBEDDING_DIMENSION
) -> EmbeddingService:
    return EmbeddingService(model_name=model_name, dimension=dimension)


_embedding_service_instance: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance
