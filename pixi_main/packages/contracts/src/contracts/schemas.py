"""Cross-module I/O contracts.

This package is imported by BOTH the Python 3.8 module and the Python 3.12
module, so it must use 3.8-compatible typing (typing.List, not list[...]).
It depends only on pydantic, so installing it into every environment never
introduces a dependency conflict.
"""
from typing import Dict, List

from pydantic import BaseModel


# ----- module A: data cleaning -----
class AInput(BaseModel):
    raw: List[float]


class AOutput(BaseModel):
    cleaned: List[float]
    meta: Dict[str, float]


# ----- module B: forecasting -----
class BInput(BaseModel):
    series: List[float]
    window: int = 3


class BOutput(BaseModel):
    forecast: List[float]
