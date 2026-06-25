"""
PubMed Service - NCBI E-utilities API wrapper for PubMed literature retrieval.

Provides search, summary fetching, and combined search-and-fetch operations
with rate limiting, retry logic, and structured result types.

Follows the same patterns as services/llm_client.py (requests library,
error classes, factory function).
"""
import logging
import os
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

import requests

logger = logging.getLogger(__name__)

# NCBI E-utilities base URL
EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# Rate limits: 3 req/sec without API key, 10 req/sec with
RATE_LIMIT_NO_KEY = 3
RATE_LIMIT_WITH_KEY = 10

# Timeouts
SEARCH_TIMEOUT = 15
FETCH_TIMEOUT = 30

# Retry settings
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # seconds


class PubMedServiceError(Exception):
    """Base error for PubMed service operations."""
    pass


class PubMedSearchError(PubMedServiceError):
    """Error during PubMed search (ESearch)."""
    pass


class PubMedFetchError(PubMedServiceError):
    """Error during PubMed fetch (ESummary/EFetch)."""
    pass


class PubMedRateLimitError(PubMedServiceError):
    """Rate limit exceeded (HTTP 429)."""
    pass


@dataclass
class PubMedArticle:
    """Structured representation of a PubMed article."""
    pmid: str
    title: str
    authors: List[str] = field(default_factory=list)
    journal: str = ""
    year: str = ""
    abstract: str = ""
    url: str = ""
    doi: str = ""

    def __post_init__(self):
        if not self.url and self.pmid:
            self.url = f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


@dataclass
class PubMedSearchResult:
    """Result of a PubMed search operation."""
    articles: List[PubMedArticle] = field(default_factory=list)
    total_count: int = 0
    query_used: str = ""


class PubMedService:
    """
    NCBI E-utilities API wrapper for PubMed literature retrieval.

    Supports ESearch (search), ESummary (metadata), and EFetch (abstracts)
    with automatic rate limiting and retry logic.

    Configuration via environment variables:
    - NCBI_EMAIL: Required by NCBI for identification
    - NCBI_API_KEY: Optional, enables higher rate limits (10 req/sec vs 3)
    """

    def __init__(
        self,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        tool_name: str = "rare-disease-diagnosis-system"
    ):
        self._email = email or os.getenv("NCBI_EMAIL", "")
        self._api_key = api_key or os.getenv("NCBI_API_KEY", "")
        self._tool = tool_name

        # Rate limiting
        self._max_per_second = RATE_LIMIT_WITH_KEY if self._api_key else RATE_LIMIT_NO_KEY
        self._min_interval = 1.0 / self._max_per_second
        self._last_request_time = 0.0

        logger.info(
            f"PubMedService initialized: email={'set' if self._email else 'not set'}, "
            f"api_key={'set' if self._api_key else 'not set'}, "
            f"rate_limit={self._max_per_second}/sec"
        )

    def _get_base_params(self) -> Dict[str, str]:
        """Get base parameters required for all NCBI requests."""
        params = {
            "tool": self._tool,
        }
        if self._email:
            params["email"] = self._email
        if self._api_key:
            params["api_key"] = self._api_key
        return params

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            sleep_time = self._min_interval - elapsed
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def _request_with_retry(
        self,
        url: str,
        params: Dict[str, Any],
        timeout: int = SEARCH_TIMEOUT
    ) -> requests.Response:
        """Make HTTP request with retry logic for transient errors."""
        last_error = None

        for attempt in range(MAX_RETRIES):
            self._rate_limit()

            try:
                response = requests.get(url, params=params, timeout=timeout)

                if response.status_code == 200:
                    return response

                if response.status_code == 429:
                    wait_time = RETRY_BACKOFF_BASE ** attempt * 5
                    logger.warning(
                        f"PubMed rate limit hit (429), waiting {wait_time}s "
                        f"(attempt {attempt + 1}/{MAX_RETRIES})"
                    )
                    time.sleep(wait_time)
                    continue

                if response.status_code >= 500:
                    wait_time = RETRY_BACKOFF_BASE ** attempt
                    logger.warning(
                        f"PubMed server error ({response.status_code}), retrying in {wait_time}s "
                        f"(attempt {attempt + 1}/{MAX_RETRIES})"
                    )
                    time.sleep(wait_time)
                    continue

                # Client error (4xx except 429) - don't retry
                raise PubMedServiceError(
                    f"PubMed API error: {response.status_code} - {response.text[:500]}"
                )

            except requests.exceptions.Timeout:
                last_error = f"Request timed out after {timeout}s"
                logger.warning(
                    f"PubMed request timeout, retrying "
                    f"(attempt {attempt + 1}/{MAX_RETRIES}): {last_error}"
                )
                continue

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {e}"
                logger.warning(
                    f"PubMed connection error, retrying "
                    f"(attempt {attempt + 1}/{MAX_RETRIES}): {last_error}"
                )
                time.sleep(RETRY_BACKOFF_BASE ** attempt)
                continue

        raise PubMedServiceError(
            f"Max retries ({MAX_RETRIES}) exceeded. Last error: {last_error}"
        )

    def search(
        self,
        query: str,
        max_results: int = 20,
        sort: str = "relevance"
    ) -> Dict[str, Any]:
        """
        Search PubMed using ESearch API.

        Args:
            query: PubMed search query (supports Boolean operators, MeSH terms, field tags)
            max_results: Maximum number of PMIDs to return (default 20, max 100000)
            sort: Sort order - "relevance" or "date"

        Returns:
            Dict with keys: IdList (list of PMIDs), Count (total results)

        Raises:
            PubMedSearchError: If search fails
        """
        url = f"{EUTILS_BASE_URL}esearch.fcgi"
        params = {
            **self._get_base_params(),
            "db": "pubmed",
            "term": query,
            "retmax": min(max_results, 100000),
            "retmode": "json",
            "sort": sort,
        }

        try:
            response = self._request_with_retry(url, params, timeout=SEARCH_TIMEOUT)
            data = response.json()

            result = data.get("esearchresult", {})
            id_list = result.get("idlist", [])
            count = int(result.get("count", 0))

            logger.info(
                f"PubMed search: query='{query[:100]}', "
                f"total={count}, returned={len(id_list)}"
            )

            return {
                "IdList": id_list,
                "Count": count,
            }

        except PubMedServiceError:
            raise
        except Exception as e:
            raise PubMedSearchError(f"PubMed search failed: {e}")

    def fetch_summaries(self, pmids: List[str]) -> List[PubMedArticle]:
        """
        Fetch article summaries using ESummary API.

        Args:
            pmids: List of PubMed IDs

        Returns:
            List of PubMedArticle objects with metadata (no abstracts)

        Raises:
            PubMedFetchError: If fetch fails
        """
        if not pmids:
            return []

        url = f"{EUTILS_BASE_URL}esummary.fcgi"
        params = {
            **self._get_base_params(),
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json",
        }

        try:
            response = self._request_with_retry(url, params, timeout=FETCH_TIMEOUT)
            data = response.json()

            articles = []
            result_data = data.get("result", {})

            for pmid in pmids:
                article_data = result_data.get(pmid, {})
                if not article_data or "error" in article_data:
                    continue

                # Parse authors
                authors = []
                for author in article_data.get("authors", []):
                    name = author.get("name", "")
                    if name:
                        authors.append(name)

                # Parse year from pubdate
                pub_date = article_data.get("pubdate", "")
                year = pub_date.split(" ")[0] if pub_date else ""

                # Parse DOI from article IDs
                doi = ""
                for aid in article_data.get("articleids", []):
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value", "")
                        break

                article = PubMedArticle(
                    pmid=pmid,
                    title=article_data.get("title", ""),
                    authors=authors,
                    journal=article_data.get("fulljournalname", "") or article_data.get("source", ""),
                    year=year,
                    abstract="",
                    doi=doi,
                )
                articles.append(article)

            logger.info(f"PubMed ESummary: fetched {len(articles)}/{len(pmids)} articles")
            return articles

        except PubMedServiceError:
            raise
        except Exception as e:
            raise PubMedFetchError(f"PubMed summary fetch failed: {e}")

    def fetch_abstracts(self, pmids: List[str]) -> Dict[str, str]:
        """
        Fetch article abstracts using EFetch API.

        Args:
            pmids: List of PubMed IDs

        Returns:
            Dict mapping PMID to abstract text

        Raises:
            PubMedFetchError: If fetch fails
        """
        if not pmids:
            return {}

        url = f"{EUTILS_BASE_URL}efetch.fcgi"
        params = {
            **self._get_base_params(),
            "db": "pubmed",
            "id": ",".join(pmids),
            "rettype": "medline",
            "retmode": "text",
        }

        try:
            response = self._request_with_retry(url, params, timeout=FETCH_TIMEOUT)
            text = response.text

            # Parse MEDLINE-style abstract text
            # Format: AB  - First line of abstract
            #               Continuation lines are indented with 6 spaces
            abstracts = {}
            current_pmid = None
            current_abstract_lines = []

            for line in text.split("\n"):
                stripped = line.strip()

                # Detect PMID lines (format: "PMID- 12345678")
                if stripped.startswith("PMID- "):
                    # Save previous article
                    if current_pmid and current_abstract_lines:
                        abstracts[current_pmid] = " ".join(current_abstract_lines).strip()
                    current_pmid = stripped.replace("PMID- ", "").strip()
                    current_abstract_lines = []
                    continue

                # Collect abstract text lines
                # MEDLINE format: "AB  - " (AB + 2 spaces + hyphen + space)
                if stripped.startswith("AB  - "):
                    # First line of abstract - extract text after "AB  - "
                    abstract_text = stripped[6:].strip()
                    current_abstract_lines.append(abstract_text)
                elif current_abstract_lines and line.startswith("      "):
                    # Continuation line: 6 spaces prefix in original line
                    abstract_text = stripped
                    if abstract_text:
                        current_abstract_lines.append(abstract_text)

            # Save last article
            if current_pmid and current_abstract_lines:
                abstracts[current_pmid] = " ".join(current_abstract_lines).strip()

            logger.info(f"PubMed EFetch: fetched {len(abstracts)} abstracts from {len(pmids)} PMIDs")
            return abstracts

        except PubMedServiceError:
            raise
        except Exception as e:
            raise PubMedFetchError(f"PubMed abstract fetch failed: {e}")

    def search_and_fetch(
        self,
        query: str,
        max_results: int = 10,
        sort: str = "relevance",
        include_abstracts: bool = True
    ) -> PubMedSearchResult:
        """
        High-level method: search PubMed and fetch article details.

        Combines ESearch + ESummary (+ optional EFetch for abstracts)
        into a single convenient call.

        Args:
            query: PubMed search query
            max_results: Maximum number of articles to return
            sort: Sort order - "relevance" or "date"
            include_abstracts: Whether to fetch full abstracts (slower)

        Returns:
            PubMedSearchResult with articles, total count, and query used
        """
        # Step 1: Search for PMIDs
        search_result = self.search(query, max_results=max_results, sort=sort)
        pmids = search_result["IdList"]
        total_count = search_result["Count"]

        if not pmids:
            logger.info(f"PubMed search returned no results for: {query}")
            return PubMedSearchResult(
                articles=[],
                total_count=0,
                query_used=query
            )

        # Step 2: Fetch summaries (title, authors, journal, year)
        articles = self.fetch_summaries(pmids)

        # Step 3: Optionally fetch abstracts
        if include_abstracts and articles:
            article_pmids = [a.pmid for a in articles]
            try:
                abstracts = self.fetch_abstracts(article_pmids)
                for article in articles:
                    if article.pmid in abstracts:
                        article.abstract = abstracts[article.pmid]
            except PubMedFetchError as e:
                logger.warning(f"Failed to fetch abstracts, continuing without them: {e}")

        return PubMedSearchResult(
            articles=articles,
            total_count=total_count,
            query_used=query
        )


def create_pubmed_service(
    email: Optional[str] = None,
    api_key: Optional[str] = None
) -> PubMedService:
    """Factory function: create a PubMedService instance."""
    return PubMedService(email=email, api_key=api_key)
