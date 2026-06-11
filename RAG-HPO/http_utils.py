"""Shared HTTP helpers for the dev scripts."""

from __future__ import annotations

import random
import time
from typing import Any, Callable, Iterable, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}
RETRYABLE_EXCEPTIONS = (
    requests.exceptions.SSLError,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ProxyError,
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.RequestException,
)


def build_retry_session(
    *,
    total: int = 5,
    connect: int = 5,
    read: int = 5,
    status: int = 5,
    backoff_factor: float = 1.0,
    pool_connections: int = 10,
    pool_maxsize: int = 10,
    methods: Iterable[str] = ("GET", "POST"),
) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=total,
        connect=connect,
        read=read,
        status=status,
        backoff_factor=backoff_factor,
        status_forcelist=tuple(RETRYABLE_STATUS_CODES),
        allowed_methods=frozenset(methods),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    *,
    max_retries: int = 5,
    timeout: Any = (10, 120),
    logger: Optional[Callable[[str], None]] = None,
    retryable_statuses: Iterable[int] = RETRYABLE_STATUS_CODES,
    retry_wait_cap: float = 30.0,
    **kwargs: Any,
) -> requests.Response:
    last_error: Optional[BaseException] = None
    retryable_statuses = set(retryable_statuses)

    for attempt in range(max_retries):
        try:
            response = session.request(method, url, timeout=timeout, **kwargs)
            if response.status_code in retryable_statuses:
                last_error = RuntimeError(
                    f"HTTP {response.status_code}: {response.text[:300]}"
                )
                wait = min((2 ** attempt) + random.uniform(0, 1), retry_wait_cap)
                if logger:
                    logger(
                        f"[RETRY] HTTP {response.status_code} on attempt {attempt + 1}/{max_retries}, waiting {wait:.1f}s"
                    )
                if attempt < max_retries - 1:
                    time.sleep(wait)
                    continue
            return response
        except RETRYABLE_EXCEPTIONS as e:
            last_error = e
            wait = min((2 ** attempt) + random.uniform(0, 1), retry_wait_cap)
            if logger:
                logger(
                    f"[RETRY] {type(e).__name__} on attempt {attempt + 1}/{max_retries}, waiting {wait:.1f}s: {repr(e)}"
                )
            if attempt < max_retries - 1:
                time.sleep(wait)

    raise RuntimeError(f"{method} {url} failed after {max_retries} attempts: {repr(last_error)}")
