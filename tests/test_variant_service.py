"""
Tests for Variant Service CRUD operations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from backend.services.variant_service import (
    VariantService,
    VariantFilter,
    PaginationParams,
    PaginatedResult,
    VariantCache,
    VariantNotFoundError,
    DuplicateVariantError,
    VariantServiceError,
    create_variant_service,
)
from backend.database.models import Variant, VCFFile, Patient


TEST_DATA_DIR = Path(__file__).parent / "data"
SAMPLE_VCF = TEST_DATA_DIR / "sample.vcf"


class TestVariantFilter:
    def test_default_filter(self):
        filter_obj = VariantFilter()
        assert filter_obj.chromosome is None
        assert filter_obj.position_start is None
        assert filter_obj.position_end is None
        assert filter_obj.variant_type is None
        assert filter_obj.min_quality is None
        assert filter_obj.max_quality is None
        assert filter_obj.acmg_classification is None

    def test_custom_filter(self):
        filter_obj = VariantFilter(
            chromosome="chr1",
            position_start=1000,
            position_end=2000,
            variant_type="SNV",
            min_quality=30.0
        )
        assert filter_obj.chromosome == "chr1"
        assert filter_obj.position_start == 1000
        assert filter_obj.position_end == 2000
        assert filter_obj.variant_type == "SNV"
        assert filter_obj.min_quality == 30.0


class TestPaginationParams:
    def test_default_pagination(self):
        pagination = PaginationParams()
        assert pagination.page == 1
        assert pagination.page_size == 50
        assert pagination.sort_by == "position"
        assert pagination.sort_desc is False

    def test_custom_pagination(self):
        pagination = PaginationParams(
            page=2,
            page_size=100,
            sort_by="quality",
            sort_desc=True
        )
        assert pagination.page == 2
        assert pagination.page_size == 100
        assert pagination.sort_by == "quality"
        assert pagination.sort_desc is True


class TestPaginatedResult:
    def test_empty_result(self):
        result = PaginatedResult()
        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.page_size == 50
        assert result.total_pages == 0

    def test_with_items(self):
        items = [Mock(spec=Variant), Mock(spec=Variant)]
        result = PaginatedResult(items=items, total=10, page=1, page_size=5, total_pages=2)
        assert len(result.items) == 2
        assert result.total == 10
        assert result.total_pages == 2


class TestVariantCache:
    def test_disabled_cache(self):
        with patch.object(VariantCache, '_get_connection', return_value=None):
            cache = VariantCache()
            cache._enabled = False
            assert cache.get("test_key") is None
            assert cache.set("test_key", {"data": "test"}) is False
            assert cache.delete("test_key") is False

    def test_cache_key_generation(self):
        key = VariantService._generate_variant_key("chr1", 1000, "A", "G")
        assert key.startswith("variant:")
        assert len(key) > len("variant:")


class TestVariantService:
    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.fixture
    def mock_cache(self):
        cache = Mock(spec=VariantCache)
        cache.get.return_value = None
        cache.set.return_value = True
        cache.delete.return_value = True
        cache.delete_pattern.return_value = 0
        return cache

    @pytest.fixture
    def variant_service(self, mock_db, mock_cache):
        return VariantService(mock_db, mock_cache)

    def test_create_variant(self, variant_service, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        variant_data = {
            "chromosome": "chr1",
            "position": 1000,
            "ref": "A",
            "alt": "G",
            "variant_type": "SNV",
            "vcf_file_id": 1
        }

        result = variant_service.create(variant_data)
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_create_duplicate_variant_raises_error(self, variant_service, mock_db):
        existing_variant = Mock(spec=Variant)
        mock_db.query.return_value.filter.return_value.first.return_value = existing_variant

        variant_data = {
            "chromosome": "chr1",
            "position": 1000,
            "ref": "A",
            "alt": "G",
            "variant_type": "SNV",
            "vcf_file_id": 1
        }

        with pytest.raises(DuplicateVariantError):
            variant_service.create(variant_data)

    def test_create_missing_field_raises_error(self, variant_service, mock_db):
        variant_data = {
            "chromosome": "chr1",
            "position": 1000,
        }

        with pytest.raises(VariantServiceError):
            variant_service.create(variant_data)

    def test_get_by_id(self, variant_service, mock_db):
        mock_variant = Mock(spec=Variant)
        mock_variant.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_variant

        result = variant_service.get_by_id(1)
        assert result.id == 1

    def test_get_by_id_not_found(self, variant_service, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(VariantNotFoundError):
            variant_service.get_by_id(999)

    def test_update_variant(self, variant_service, mock_db):
        mock_variant = Mock(spec=Variant)
        mock_variant.id = 1
        mock_variant.chromosome = "chr1"
        mock_variant.position = 1000
        mock_variant.ref = "A"
        mock_variant.alt = "G"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_variant
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        result = variant_service.update(1, {"quality": 50.0})
        assert mock_db.commit.called

    def test_delete_variant(self, variant_service, mock_db):
        mock_variant = Mock(spec=Variant)
        mock_variant.id = 1
        mock_variant.chromosome = "chr1"
        mock_variant.position = 1000
        mock_variant.ref = "A"
        mock_variant.alt = "G"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_variant
        mock_db.delete = Mock()
        mock_db.commit = Mock()

        result = variant_service.delete(1)
        assert result is True
        assert mock_db.delete.called

    def test_list_with_filters(self, variant_service, mock_db):
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 10
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        filters = VariantFilter(chromosome="chr1")
        pagination = PaginationParams(page=1, page_size=10)

        result = variant_service.list_with_filters(filters, pagination)
        assert result.total == 10

    def test_get_by_range(self, variant_service, mock_db):
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        result = variant_service.get_by_range("chr1", 1000, 2000)
        assert mock_query.filter.called

    def test_get_variant_count_by_chromosome(self, variant_service, mock_db):
        mock_result = Mock()
        mock_result.chromosome = "chr1"
        mock_result.count = 100
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [mock_result]

        result = variant_service.get_variant_count_by_chromosome(1)
        assert "chr1" in result

    def test_get_variant_count_by_type(self, variant_service, mock_db):
        mock_result = Mock()
        mock_result.variant_type = "SNV"
        mock_result.count = 50
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [mock_result]

        result = variant_service.get_variant_count_by_type(1)
        assert "SNV" in result


class TestBatchOperations:
    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.fixture
    def mock_cache(self):
        cache = Mock(spec=VariantCache)
        cache.get.return_value = None
        cache.set.return_value = True
        cache.delete_pattern.return_value = 0
        return cache

    @pytest.fixture
    def variant_service(self, mock_db, mock_cache):
        return VariantService(mock_db, mock_cache)

    def test_batch_create(self, variant_service, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        variants_data = [
            {
                "chromosome": "chr1",
                "position": 1000 + i,
                "ref": "A",
                "alt": "G",
                "variant_type": "SNV",
                "vcf_file_id": 1
            }
            for i in range(5)
        ]

        created, duplicates = variant_service.batch_create(variants_data)
        assert created == 5
        assert duplicates == 0

    def test_import_from_vcf_variant(self, variant_service, mock_db):
        from backend.services.vcf_parser import VCFVariant

        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()

        vcf_variant = VCFVariant(
            chromosome="chr1",
            position=1000,
            variant_id="rs123",
            reference="A",
            alternate="G",
            quality=50.0,
            filter_status="PASS",
            info={}
        )

        result = variant_service.import_from_vcf_variant(vcf_variant, 1, batch_mode=True)
        assert mock_db.add.called


class TestFactoryFunction:
    def test_create_variant_service(self):
        mock_db = Mock()
        service = create_variant_service(mock_db)
        assert isinstance(service, VariantService)


class TestIntegration:
    @pytest.fixture
    def db_session(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from backend.database.base import Base

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_full_crud_workflow(self, db_session):
        from backend.database.models import Patient, VCFFile

        patient = Patient(name="Test Patient")
        db_session.add(patient)
        db_session.commit()

        vcf_file = VCFFile(
            file_name="test.vcf",
            file_path="/tmp/test.vcf",
            patient_id=patient.id
        )
        db_session.add(vcf_file)
        db_session.commit()

        cache = VariantCache()
        cache._enabled = False
        service = VariantService(db_session, cache)

        variant_data = {
            "chromosome": "chr1",
            "position": 1000,
            "ref": "A",
            "alt": "G",
            "variant_type": "SNV",
            "quality": 50.0,
            "filter_status": "PASS",
            "info_field": {},
            "vcf_file_id": vcf_file.id
        }

        created = service.create(variant_data)
        assert created.id is not None

        retrieved = service.get_by_id(created.id)
        assert retrieved.chromosome == "chr1"
        assert retrieved.position == 1000

        updated = service.update(created.id, {"quality": 60.0})
        assert updated.quality == 60.0

        deleted = service.delete(created.id)
        assert deleted is True

        with pytest.raises(VariantNotFoundError):
            service.get_by_id(created.id)
