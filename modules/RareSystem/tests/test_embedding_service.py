"""
Tests for Embedding Service.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from backend.services.embedding_service import (
    EmbeddingService,
    SearchResult,
    EmbeddingServiceError,
    ModelNotLoadedError,
    IndexNotBuiltError,
    create_embedding_service,
)


class TestEmbeddingService:
    def test_init(self):
        service = EmbeddingService()
        assert service._model_name == "all-MiniLM-L6-v2"
        assert service._dimension == 384
        assert service._index is None
        assert service._model is None

    def test_init_custom_params(self):
        service = EmbeddingService(
            model_name="custom-model",
            dimension=768,
            index_path="custom/path"
        )
        assert service._model_name == "custom-model"
        assert service._dimension == 768
        assert service._index_path == "custom/path"

    @patch('services.embedding_service.SentenceTransformer')
    def test_load_model_success(self, mock_transformer):
        service = EmbeddingService()
        mock_model = Mock()
        mock_transformer.return_value = mock_model
        
        model = service._load_model()
        
        assert model == mock_model
        mock_transformer.assert_called_once_with("all-MiniLM-L6-v2")

    def test_load_model_import_error(self):
        service = EmbeddingService()
        
        with patch.dict('sys.modules', {'sentence_transformers': None}):
            with pytest.raises(ModelNotLoadedError):
                service._load_model()

    @patch('services.embedding_service.faiss')
    def test_init_faiss_success(self, mock_faiss):
        service = EmbeddingService()
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        index = service._init_faiss()
        
        assert index == mock_index
        mock_faiss.IndexFlatIP.assert_called_once_with(384)

    @patch.object(EmbeddingService, '_load_model')
    def test_generate_embedding(self, mock_load_model):
        service = EmbeddingService()
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_load_model.return_value = mock_model
        
        embedding = service.generate_embedding("test text")
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (3,)
        mock_model.encode.assert_called_once_with(["test text"], convert_to_numpy=True)

    @patch.object(EmbeddingService, '_load_model')
    def test_generate_embeddings_batch(self, mock_load_model):
        service = EmbeddingService()
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1], [0.2], [0.3]])
        mock_load_model.return_value = mock_model
        
        texts = ["text1", "text2", "text3"]
        embeddings = service.generate_embeddings_batch(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (3, 1)
        mock_model.encode.assert_called_once()

    @patch.object(EmbeddingService, '_init_faiss')
    @patch.object(EmbeddingService, 'generate_embedding')
    def test_add_document(self, mock_gen_embedding, mock_init_faiss):
        service = EmbeddingService()
        mock_index = Mock()
        mock_init_faiss.return_value = mock_index
        mock_gen_embedding.return_value = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        result = service.add_document(1, "test content", {"key": "value"})
        
        assert result is True
        assert 1 in service._document_cache
        assert 0 in service._id_mapping
        assert service._id_mapping[0] == 1

    @patch.object(EmbeddingService, '_init_faiss')
    @patch.object(EmbeddingService, 'generate_embeddings_batch')
    def test_add_documents_batch(self, mock_gen_embeddings, mock_init_faiss):
        service = EmbeddingService()
        mock_index = Mock()
        mock_init_faiss.return_value = mock_index
        mock_gen_embeddings.return_value = np.array([[0.1], [0.2]], dtype=np.float32)
        
        documents: list = [(1, "text1", None), (2, "text2", None)]
        count = service.add_documents_batch(documents)
        
        assert count == 2
        assert len(service._document_cache) == 2

    @patch.object(EmbeddingService, '_init_faiss')
    @patch.object(EmbeddingService, 'generate_embedding')
    def test_search_empty_index(self, mock_gen_embedding, mock_init_faiss):
        service = EmbeddingService()
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_init_faiss.return_value = mock_index
        
        results = service.search("test query")
        
        assert results == []

    @patch.object(EmbeddingService, '_init_faiss')
    @patch.object(EmbeddingService, 'generate_embedding')
    def test_search_with_results(self, mock_gen_embedding, mock_init_faiss):
        service = EmbeddingService()
        mock_index = Mock()
        mock_index.ntotal = 2
        mock_index.search.return_value = (
            np.array([[0.9, 0.8]]),
            np.array([[0, 1]])
        )
        mock_init_faiss.return_value = mock_index
        mock_gen_embedding.return_value = np.array([0.1, 0.2], dtype=np.float32)
        
        service._id_mapping = {0: 1, 1: 2}
        service._document_cache = {1: "doc1", 2: "doc2"}
        
        results = service.search("test query", k=2)
        
        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)

    def test_remove_document(self):
        service = EmbeddingService()
        service._document_cache = {1: "content1", 2: "content2"}
        
        result = service.remove_document(1)
        
        assert result is True
        assert 1 not in service._document_cache

    def test_remove_document_not_found(self):
        service = EmbeddingService()
        service._document_cache = {1: "content1"}
        
        result = service.remove_document(999)
        
        assert result is False

    def test_clear_index(self):
        service = EmbeddingService()
        service._id_mapping = {0: 1, 1: 2}
        service._document_cache = {1: "a", 2: "b"}
        
        result = service.clear_index()
        
        assert result is True
        assert len(service._id_mapping) == 0
        assert len(service._document_cache) == 0

    def test_get_index_size(self):
        service = EmbeddingService()
        
        size = service.get_index_size()
        assert size == 0

    def test_get_document_count(self):
        service = EmbeddingService()
        service._document_cache = {1: "a", 2: "b", 3: "c"}
        
        count = service.get_document_count()
        assert count == 3


class TestSearchResult:
    def test_creation(self):
        result = SearchResult(
            document_id=1,
            content="test content",
            score=0.95,
            metadata={"key": "value"}
        )
        
        assert result.document_id == 1
        assert result.content == "test content"
        assert result.score == 0.95
        assert result.metadata == {"key": "value"}

    def test_creation_minimal(self):
        result = SearchResult(
            document_id=1,
            content="test",
            score=0.5
        )
        
        assert result.metadata is None


def test_create_embedding_service():
    service = create_embedding_service()
    assert isinstance(service, EmbeddingService)
    assert service._model_name == "all-MiniLM-L6-v2"
