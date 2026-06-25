"""Final report generation from wide-table CSV and test-case manifest."""

from report.models import GeneCard, ReportContext, SampleMeta, VariantRecord
from report.output import ReportOutputPaths, resolve_output_paths
from report.pipeline import generate_report

__all__ = [
    "GeneCard",
    "ReportContext",
    "ReportOutputPaths",
    "SampleMeta",
    "VariantRecord",
    "generate_report",
    "resolve_output_paths",
]
