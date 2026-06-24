"""
Variant Service Layer - CRUD operations for variant data.

Provides business logic for:
- Saving/retrieving variants from database
- Filtering by chromosome, position, type, quality, ACMG classification
- Pagination for large variant lists
- Caching frequently accessed variants
- Batch import from VCF parser
"""
import logging
import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Generator
from dataclasses import dataclass, field

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import redis

from database.models import Variant, VCFFile, ACMGClassification
from services.vcf_parser import VCFVariant

logger = logging.getLogger(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
CACHE_PREFIX = "variant:"
CACHE_TTL_SECONDS = 3600
POPULAR_VARIANT_TTL = 86400


@dataclass
class VariantFilter:
    chromosome: Optional[str] = None
    position_start: Optional[int] = None
    position_end: Optional[int] = None
    variant_type: Optional[str] = None
    min_quality: Optional[float] = None
    max_quality: Optional[float] = None
    acmg_classification: Optional[str] = None
    filter_status: Optional[str] = None
    gene: Optional[str] = None
    rs_id: Optional[str] = None


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 50
    sort_by: str = "position"
    sort_desc: bool = False


@dataclass
class PaginatedResult:
    items: List[Variant] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 50
    total_pages: int = 0


class VariantServiceError(Exception):
    pass


class VariantNotFoundError(VariantServiceError):
    pass


class DuplicateVariantError(VariantServiceError):
    pass


class CacheConnectionError(VariantServiceError):
    pass


class VariantCache:
    def __init__(self, host: str = REDIS_HOST, port: int = REDIS_PORT, db: int = REDIS_DB):
        self._redis: Optional[redis.Redis] = None
        self._host = host
        self._port = port
        self._db = db
        self._enabled = True

    def _get_connection(self) -> Optional[redis.Redis]:
        if not self._enabled:
            return None
        if self._redis is None:
            try:
                self._redis = redis.Redis(
                    host=self._host,
                    port=self._port,
                    db=self._db,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                self._redis.ping()  # type: ignore
                logger.info("Redis cache connected successfully")
            except redis.ConnectionError as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self._enabled = False
                return None
        return self._redis

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        if conn is None:
            return None
        try:
            data = conn.get(key)
            if data:
                return json.loads(data)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Dict[str, Any], ttl: int = CACHE_TTL_SECONDS) -> bool:
        conn = self._get_connection()
        if conn is None:
            return False
        try:
            conn.setex(key, ttl, json.dumps(value))
            return True
        except redis.RedisError as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        conn = self._get_connection()
        if conn is None:
            return False
        try:
            conn.delete(key)
            return True
        except redis.RedisError as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        conn = self._get_connection()
        if conn is None:
            return 0
        try:
            keys = conn.keys(pattern)
            if keys:
                return conn.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.warning(f"Cache delete_pattern error for {pattern}: {e}")
            return 0

    def is_enabled(self) -> bool:
        return self._enabled


class VariantService:
    def __init__(self, db: Session, cache: Optional[VariantCache] = None):
        self._db = db
        self._cache = cache or VariantCache()

    @staticmethod
    def _generate_variant_key(chromosome: str, position: int, ref: str, alt: str) -> str:
        key_str = f"{chromosome}:{position}:{ref}:{alt}"
        hash_key = hashlib.md5(key_str.encode()).hexdigest()[:16]
        return f"{CACHE_PREFIX}{hash_key}"

    @staticmethod
    def _variant_to_dict(variant: Variant) -> Dict[str, Any]:
        return {
            "id": variant.id,
            "chromosome": variant.chromosome,
            "position": variant.position,
            "ref": variant.ref,
            "alt": variant.alt,
            "variant_type": variant.variant_type,
            "quality": variant.quality,
            "filter_status": variant.filter_status,
            "info_field": variant.info_field,
            "vcf_file_id": variant.vcf_file_id,
        }

    def create(self, variant_data: Dict[str, Any]) -> Variant:
        required_fields = ["chromosome", "position", "ref", "alt", "variant_type", "vcf_file_id"]
        for field in required_fields:
            if field not in variant_data:
                raise VariantServiceError(f"Missing required field: {field}")

        existing = self._db.query(Variant).filter(
            and_(
                Variant.chromosome == variant_data["chromosome"],
                Variant.position == variant_data["position"],
                Variant.ref == variant_data["ref"],
                Variant.alt == variant_data["alt"],
                Variant.vcf_file_id == variant_data["vcf_file_id"]
            )
        ).first()

        if existing:
            raise DuplicateVariantError(
                f"Variant already exists: {variant_data['chromosome']}:{variant_data['position']}"
            )

        variant = Variant(**variant_data)
        self._db.add(variant)
        self._db.commit()
        self._db.refresh(variant)

        cache_key = self._generate_variant_key(
            variant.chromosome, variant.position, variant.ref, variant.alt
        )
        self._cache.set(cache_key, self._variant_to_dict(variant))

        logger.info(f"Created variant: {variant}")
        return variant

    def get_by_id(self, variant_id: int) -> Variant:
        variant = self._db.query(Variant).filter(Variant.id == variant_id).first()
        if not variant:
            raise VariantNotFoundError(f"Variant not found: id={variant_id}")
        return variant

    def get_by_position(
        self,
        chromosome: str,
        position: int,
        vcf_file_id: Optional[int] = None
    ) -> List[Variant]:
        cache_key = self._generate_variant_key(chromosome, position, "", "")
        cached = self._cache.get(cache_key)
        if cached and cached.get("position") == position:
            logger.debug(f"Cache hit for position {chromosome}:{position}")

        query = self._db.query(Variant).filter(
            and_(
                Variant.chromosome == chromosome,
                Variant.position == position
            )
        )

        if vcf_file_id:
            query = query.filter(Variant.vcf_file_id == vcf_file_id)

        return query.all()

    def get_by_range(
        self,
        chromosome: str,
        start: int,
        end: int,
        vcf_file_id: Optional[int] = None
    ) -> List[Variant]:
        query = self._db.query(Variant).filter(
            and_(
                Variant.chromosome == chromosome,
                Variant.position >= start,
                Variant.position <= end
            )
        )

        if vcf_file_id:
            query = query.filter(Variant.vcf_file_id == vcf_file_id)

        return query.order_by(Variant.position).all()

    def update(self, variant_id: int, update_data: Dict[str, Any]) -> Variant:
        variant = self.get_by_id(variant_id)

        for key, value in update_data.items():
            if hasattr(variant, key):
                setattr(variant, key, value)

        self._db.commit()
        self._db.refresh(variant)

        cache_key = self._generate_variant_key(
            variant.chromosome, variant.position, variant.ref, variant.alt
        )
        self._cache.set(cache_key, self._variant_to_dict(variant))

        logger.info(f"Updated variant {variant_id}")
        return variant

    def delete(self, variant_id: int) -> bool:
        variant = self.get_by_id(variant_id)

        cache_key = self._generate_variant_key(
            variant.chromosome, variant.position, variant.ref, variant.alt
        )
        self._cache.delete(cache_key)

        self._db.delete(variant)
        self._db.commit()

        logger.info(f"Deleted variant {variant_id}")
        return True

    def list_with_filters(
        self,
        filters: VariantFilter,
        pagination: Optional[PaginationParams] = None
    ) -> PaginatedResult:
        if pagination is None:
            pagination = PaginationParams()

        query = self._db.query(Variant)

        if filters.chromosome:
            query = query.filter(Variant.chromosome == filters.chromosome)

        if filters.position_start is not None:
            query = query.filter(Variant.position >= filters.position_start)

        if filters.position_end is not None:
            query = query.filter(Variant.position <= filters.position_end)

        if filters.variant_type:
            query = query.filter(Variant.variant_type == filters.variant_type)

        if filters.min_quality is not None:
            query = query.filter(Variant.quality >= filters.min_quality)

        if filters.max_quality is not None:
            query = query.filter(Variant.quality <= filters.max_quality)

        if filters.filter_status:
            query = query.filter(Variant.filter_status == filters.filter_status)

        if filters.acmg_classification:
            query = query.join(ACMGClassification).filter(
                ACMGClassification.classification == filters.acmg_classification
            )

        if filters.rs_id:
            query = query.filter(Variant.info_field["ID"].astext.contains(filters.rs_id))

        total = query.count()

        sort_column = getattr(Variant, pagination.sort_by, Variant.position)
        if pagination.sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        offset = (pagination.page - 1) * pagination.page_size
        items = query.offset(offset).limit(pagination.page_size).all()

        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages
        )

    def get_variants_by_vcf_file(
        self,
        vcf_file_id: int,
        pagination: Optional[PaginationParams] = None
    ) -> PaginatedResult:
        if pagination is None:
            pagination = PaginationParams()

        query = self._db.query(Variant).filter(Variant.vcf_file_id == vcf_file_id)

        total = query.count()

        sort_column = getattr(Variant, pagination.sort_by, Variant.position)
        if pagination.sort_desc:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        offset = (pagination.page - 1) * pagination.page_size
        items = query.offset(offset).limit(pagination.page_size).all()

        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages
        )

    def batch_create(self, variants_data: List[Dict[str, Any]]) -> Tuple[int, int]:
        created = 0
        duplicates = 0

        for variant_data in variants_data:
            try:
                self.create(variant_data)
                created += 1
            except DuplicateVariantError:
                duplicates += 1

        logger.info(f"Batch create: {created} created, {duplicates} duplicates skipped")
        return created, duplicates

    def import_from_vcf_variant(
        self,
        vcf_variant: VCFVariant,
        vcf_file_id: int,
        batch_mode: bool = False
    ) -> Variant:
        variant_data = {
            "chromosome": vcf_variant.chromosome,
            "position": vcf_variant.position,
            "ref": vcf_variant.reference,
            "alt": vcf_variant.alternate,
            "variant_type": vcf_variant.variant_type,
            "quality": vcf_variant.quality,
            "filter_status": vcf_variant.filter_status,
            "info_field": vcf_variant.info,
            "vcf_file_id": vcf_file_id,
        }

        if batch_mode:
            existing = self._db.query(Variant).filter(
                and_(
                    Variant.chromosome == variant_data["chromosome"],
                    Variant.position == variant_data["position"],
                    Variant.ref == variant_data["ref"],
                    Variant.alt == variant_data["alt"],
                    Variant.vcf_file_id == vcf_file_id
                )
            ).first()

            if existing:
                return existing

            variant = Variant(**variant_data)
            self._db.add(variant)
            return variant

        return self.create(variant_data)

    def batch_import_from_vcf(
        self,
        vcf_variants: List[VCFVariant],
        vcf_file_id: int,
        batch_size: int = 1000
    ) -> Tuple[int, int]:
        imported = 0
        duplicates = 0

        for i in range(0, len(vcf_variants), batch_size):
            batch = vcf_variants[i:i + batch_size]

            for vcf_variant in batch:
                try:
                    self.import_from_vcf_variant(vcf_variant, vcf_file_id, batch_mode=True)
                    imported += 1
                except Exception as e:
                    logger.warning(f"Failed to import variant: {e}")
                    duplicates += 1

            self._db.commit()
            logger.info(f"Imported batch {i // batch_size + 1}: {imported} total variants")

        self._cache.delete_pattern(f"{CACHE_PREFIX}*")

        logger.info(f"Batch import complete: {imported} imported, {duplicates} skipped")
        return imported, duplicates

    def stream_import_from_vcf(
        self,
        vcf_variant_iterator: Generator[VCFVariant, None, None],
        vcf_file_id: int,
        batch_size: int = 1000
    ) -> Tuple[int, int]:
        imported = 0
        duplicates = 0
        batch = []

        for vcf_variant in vcf_variant_iterator:
            batch.append(vcf_variant)

            if len(batch) >= batch_size:
                count, dups = self._process_import_batch(batch, vcf_file_id)
                imported += count
                duplicates += dups
                batch = []

        if batch:
            count, dups = self._process_import_batch(batch, vcf_file_id)
            imported += count
            duplicates += dups

        self._cache.delete_pattern(f"{CACHE_PREFIX}*")

        logger.info(f"Stream import complete: {imported} imported, {duplicates} skipped")
        return imported, duplicates

    def _process_import_batch(
        self,
        batch: List[VCFVariant],
        vcf_file_id: int
    ) -> Tuple[int, int]:
        imported = 0
        duplicates = 0

        for vcf_variant in batch:
            try:
                variant_data = {
                    "chromosome": vcf_variant.chromosome,
                    "position": vcf_variant.position,
                    "ref": vcf_variant.reference,
                    "alt": vcf_variant.alternate,
                    "variant_type": vcf_variant.variant_type,
                    "quality": vcf_variant.quality,
                    "filter_status": vcf_variant.filter_status,
                    "info_field": vcf_variant.info,
                    "vcf_file_id": vcf_file_id,
                }

                variant = Variant(**variant_data)
                self._db.add(variant)
                imported += 1

            except Exception as e:
                logger.warning(f"Failed to process variant: {e}")
                duplicates += 1

        self._db.commit()
        return imported, duplicates

    def get_variant_count_by_chromosome(self, vcf_file_id: int) -> Dict[str, int]:
        from sqlalchemy import func

        result = self._db.query(
            Variant.chromosome,
            func.count(Variant.id).label("count")
        ).filter(
            Variant.vcf_file_id == vcf_file_id
        ).group_by(
            Variant.chromosome
        ).all()

        return {row.chromosome: row.count for row in result}

    def get_variant_count_by_type(self, vcf_file_id: int) -> Dict[str, int]:
        from sqlalchemy import func

        result = self._db.query(
            Variant.variant_type,
            func.count(Variant.id).label("count")
        ).filter(
            Variant.vcf_file_id == vcf_file_id
        ).group_by(
            Variant.variant_type
        ).all()

        return {row.variant_type: row.count for row in result}

    def get_quality_distribution(
        self,
        vcf_file_id: int,
        bins: int = 10
    ) -> List[Dict[str, Any]]:
        import math

        variants = self._db.query(Variant.quality).filter(
            and_(
                Variant.vcf_file_id == vcf_file_id,
                Variant.quality.isnot(None)
            )
        ).all()

        qualities = [v.quality for v in variants if v.quality is not None]

        if not qualities:
            return []

        min_q = min(qualities)
        max_q = max(qualities)
        bin_width = (max_q - min_q) / bins if max_q > min_q else 1

        distribution = []
        for i in range(bins):
            bin_start = min_q + i * bin_width
            bin_end = min_q + (i + 1) * bin_width
            count = sum(1 for q in qualities if bin_start <= q < bin_end)
            if i == bins - 1:
                count = sum(1 for q in qualities if bin_start <= q <= bin_end)

            distribution.append({
                "bin_start": round(bin_start, 2),
                "bin_end": round(bin_end, 2),
                "count": count
            })

        return distribution

    def delete_by_vcf_file(self, vcf_file_id: int) -> int:
        count = self._db.query(Variant).filter(
            Variant.vcf_file_id == vcf_file_id
        ).count()

        self._db.query(Variant).filter(
            Variant.vcf_file_id == vcf_file_id
        ).delete()

        self._db.commit()

        self._cache.delete_pattern(f"{CACHE_PREFIX}*")

        logger.info(f"Deleted {count} variants for VCF file {vcf_file_id}")
        return count

    def get_cached_variant(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str
    ) -> Optional[Dict[str, Any]]:
        cache_key = self._generate_variant_key(chromosome, position, ref, alt)
        return self._cache.get(cache_key)

    def invalidate_cache(self, variant_id: Optional[int] = None) -> int:
        if variant_id is None:
            return self._cache.delete_pattern(f"{CACHE_PREFIX}*")

        variant = self.get_by_id(variant_id)
        cache_key = self._generate_variant_key(
            variant.chromosome, variant.position, variant.ref, variant.alt
        )
        return 1 if self._cache.delete(cache_key) else 0


def create_variant_service(db: Session, cache: Optional[VariantCache] = None) -> VariantService:
    return VariantService(db, cache)


def get_cached_variants_bulk(
    cache: VariantCache,
    variant_keys: List[Tuple[str, int, str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    results = {}
    for chromosome, position, ref, alt in variant_keys:
        key = VariantService._generate_variant_key(chromosome, position, ref, alt)
        results[key] = cache.get(key)
    return results
