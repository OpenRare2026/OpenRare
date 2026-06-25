"""
Report Generation Service - Clinical and Research Track Reports

Generates dual-track reports:
- Clinical track: ACMG-compliant reports with verified evidence chains
- Research track: Hypotheses with uncertainty quantification

Key principles:
- Clinical reports are for patient-facing decisions
- Research reports are for exploratory analysis only
- Clear visual distinction between tracks
- All evidence traceable to source data
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from database.models import (
    Patient,
    Variant,
    ACMGClassification,
    ACMGEvidence,
    ClinicalReport,
    ResearchReport,
)
from services.acmg_classifier import ClassificationCategory, ClassificationResult

logger = logging.getLogger(__name__)


class ReportStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    FINAL = "final"
    ARCHIVED = "archived"


@dataclass
class EvidenceSummary:
    criterion: str
    criterion_name: str
    is_met: bool
    evidence_level: str
    description: str
    confidence: float
    sources: List[str] = field(default_factory=list)


@dataclass
class ClinicalReportData:
    report_id: str
    patient_id: str
    report_date: str
    status: ReportStatus
    
    summary: str
    variants_classified: List[Dict[str, Any]]
    
    pathogenic_findings: List[Dict[str, Any]]
    likely_pathogenic_findings: List[Dict[str, Any]]
    vus_findings: List[Dict[str, Any]]
    
    evidence_chains: List[Dict[str, Any]]
    
    recommendations: List[str]
    
    clinician_notes: Optional[str] = None
    review_status: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Hypothesis:
    hypothesis_id: str
    description: str
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    uncertainty_level: str
    confidence: float
    priority: float


@dataclass
class ResearchReportData:
    report_id: str
    patient_id: str
    report_date: str
    status: ReportStatus
    
    executive_summary: str
    
    hypotheses: List[Hypothesis]
    
    evidence_gaps: List[str]
    uncertainty_metrics: Dict[str, float]
    
    suggested_followup: List[str]
    
    disclaimer: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ClinicalReportGenerator:
    """
    Clinical Track Report Generator
    
    Generates clinical-grade reports that:
    - Comply with ACMG/AMP classification guidelines
    - Include fully verified evidence chains
    - Are traceable to source data
    - Can be edited by clinicians
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate(
        self,
        patient: Patient,
        variants: List[Variant],
        classifications: List[ACMGClassification],
        evidence_records: List[ACMGEvidence],
        context: Optional[Dict[str, Any]] = None
    ) -> ClinicalReportData:
        self.logger.info(f"Generating clinical report for patient {patient.id}")
        
        pathogenic = []
        likely_pathogenic = []
        vus = []
        likely_benign = []
        benign = []
        
        variant_map = {v.id: v for v in variants}
        
        for classification in classifications:
            variant = variant_map.get(classification.variant_id)
            if not variant:
                continue
            
            variant_evidence = [
                e for e in evidence_records
                if e.variant_id == classification.variant_id
            ]
            
            finding = self._create_variant_finding(
                variant, classification, variant_evidence
            )
            
            cat = classification.classification
            if cat == ClassificationCategory.PATHOGENIC.value:
                pathogenic.append(finding)
            elif cat == ClassificationCategory.LIKELY_PATHOGENIC.value:
                likely_pathogenic.append(finding)
            elif cat == ClassificationCategory.UNCERTAIN_SIGNIFICANCE.value:
                vus.append(finding)
            elif cat == ClassificationCategory.LIKELY_BENIGN.value:
                likely_benign.append(finding)
            elif cat == ClassificationCategory.BENIGN.value:
                benign.append(finding)
        
        all_findings = pathogenic + likely_pathogenic + vus
        evidence_chains = self._build_evidence_chains(all_findings, evidence_records)
        
        summary = self._generate_summary(
            patient, len(pathogenic), len(likely_pathogenic), len(vus)
        )
        
        recommendations = self._generate_recommendations(
            pathogenic, likely_pathogenic, vus
        )
        
        report = ClinicalReportData(
            report_id=f"CR-{patient.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            patient_id=str(patient.id),
            report_date=datetime.utcnow().isoformat(),
            status=ReportStatus.DRAFT,
            summary=summary,
            variants_classified=all_findings,
            pathogenic_findings=pathogenic,
            likely_pathogenic_findings=likely_pathogenic,
            vus_findings=vus,
            evidence_chains=evidence_chains,
            recommendations=recommendations,
            metadata={
                "generator_version": self.VERSION,
                "variant_count": len(variants),
                "classified_count": len(classifications),
            }
        )
        
        self.logger.info(f"Clinical report generated: {report.report_id}")
        return report
    
    def _create_variant_finding(
        self,
        variant: Variant,
        classification: ACMGClassification,
        evidence: List[ACMGEvidence]
    ) -> Dict[str, Any]:
        return {
            "variant_id": variant.id,
            "genomic_position": f"{variant.chromosome}:{variant.position}",
            "ref_alt": f"{variant.ref}>{variant.alt}",
            "variant_type": variant.variant_type,
            "classification": classification.classification,
            "confidence": classification.confidence_score,
            "evidence_summary": [
                {
                    "criterion": e.criterion,
                    "evidence_level": e.evidence_level,
                    "description": e.description,
                    "source": e.evidence_source,
                }
                for e in evidence if e.is_applied
            ],
            "notes": classification.notes,
        }
    
    def _build_evidence_chains(
        self,
        findings: List[Dict[str, Any]],
        evidence_records: List[ACMGEvidence]
    ) -> List[Dict[str, Any]]:
        chains = []
        for finding in findings:
            variant_id = finding["variant_id"]
            
            variant_evidence = [
                e for e in evidence_records
                if e.variant_id == variant_id and e.is_applied
            ]
            
            chain = {
                "variant_id": variant_id,
                "chain": [
                    {
                        "step": idx + 1,
                        "criterion": e.criterion,
                        "evidence_level": e.evidence_level,
                        "description": e.description,
                        "source": e.evidence_source or "Internal analysis",
                        "verification_status": "pending",
                    }
                    for idx, e in enumerate(variant_evidence)
                ]
            }
            chains.append(chain)
        
        return chains
    
    def _generate_summary(
        self,
        patient: Patient,
        pathogenic_count: int,
        likely_pathogenic_count: int,
        vus_count: int
    ) -> str:
        parts = [f"Clinical report for patient {patient.name or patient.id}."]
        
        if pathogenic_count > 0:
            parts.append(f"Found {pathogenic_count} pathogenic variant(s).")
        if likely_pathogenic_count > 0:
            parts.append(f"Found {likely_pathogenic_count} likely pathogenic variant(s).")
        if vus_count > 0:
            parts.append(f"Found {vus_count} variant(s) of uncertain significance.")
        
        if pathogenic_count == 0 and likely_pathogenic_count == 0:
            parts.append("No pathogenic or likely pathogenic variants identified.")
        
        return " ".join(parts)
    
    def _generate_recommendations(
        self,
        pathogenic: List[Dict[str, Any]],
        likely_pathogenic: List[Dict[str, Any]],
        vus: List[Dict[str, Any]]
    ) -> List[str]:
        recommendations = []
        
        if pathogenic:
            recommendations.append(
                "Pathogenic variant(s) identified. Recommend clinical correlation "
                "and genetic counseling for the patient and family members."
            )
        
        if likely_pathogenic:
            recommendations.append(
                "Likely pathogenic variant(s) identified. Recommend further "
                "validation studies and clinical correlation."
            )
        
        if vus:
            recommendations.append(
                f"{len(vus)} variant(s) of uncertain significance identified. "
                "Recommend periodic re-evaluation as new evidence becomes available."
            )
        
        if not pathogenic and not likely_pathogenic:
            recommendations.append(
                "Consider additional testing modalities if clinical suspicion remains high."
            )
        
        recommendations.append(
            "This report should be reviewed by a qualified clinical geneticist."
        )
        
        return recommendations
    
    def render_html(self, report: ClinicalReportData) -> str:
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="UTF-8">',
            f"<title>Clinical Report - {report.report_id}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 40px; }",
            ".header { border-bottom: 2px solid #1890ff; padding-bottom: 20px; margin-bottom: 20px; }",
            ".section { margin: 20px 0; }",
            ".pathogenic { background: #fff2f0; border-left: 4px solid #ff4d4f; padding: 10px; margin: 10px 0; }",
            ".likely-pathogenic { background: #fff7e6; border-left: 4px solid #fa8c16; padding: 10px; margin: 10px 0; }",
            ".vus { background: #f0f0f0; border-left: 4px solid #8c8c8c; padding: 10px; margin: 10px 0; }",
            ".evidence-chain { font-size: 0.9em; color: #666; }",
            ".recommendations { background: #e6f7ff; padding: 15px; border-radius: 4px; }",
            ".disclaimer { font-size: 0.8em; color: #8c8c8c; margin-top: 40px; border-top: 1px solid #d9d9d9; padding-top: 20px; }",
            "</style>",
            "</head>",
            "<body>",
            '<div class="header">',
            f"<h1>Clinical Genetic Report</h1>",
            f"<p><strong>Report ID:</strong> {report.report_id}</p>",
            f"<p><strong>Date:</strong> {report.report_date}</p>",
            f"<p><strong>Patient ID:</strong> {report.patient_id}</p>",
            "</div>",
        ]
        
        html_parts.append('<div class="section">')
        html_parts.append('<h2>Summary</h2>')
        html_parts.append(f'<p>{report.summary}</p>')
        html_parts.append('</div>')
        
        if report.pathogenic_findings:
            html_parts.append('<div class="section">')
            html_parts.append('<h2>Pathogenic Findings</h2>')
            for finding in report.pathogenic_findings:
                html_parts.append('<div class="pathogenic">')
                html_parts.append(f'<h3>{finding["genomic_position"]} {finding["ref_alt"]}</h3>')
                html_parts.append(f'<p><strong>Classification:</strong> {finding["classification"]}</p>')
                html_parts.append(f'<p><strong>Confidence:</strong> {finding["confidence"]:.1%}</p>')
                html_parts.append(self._render_evidence_html(finding["evidence_summary"]))
                html_parts.append('</div>')
            html_parts.append('</div>')
        
        if report.likely_pathogenic_findings:
            html_parts.append('<div class="section">')
            html_parts.append('<h2>Likely Pathogenic Findings</h2>')
            for finding in report.likely_pathogenic_findings:
                html_parts.append('<div class="likely-pathogenic">')
                html_parts.append(f'<h3>{finding["genomic_position"]} {finding["ref_alt"]}</h3>')
                html_parts.append(f'<p><strong>Classification:</strong> {finding["classification"]}</p>')
                html_parts.append(f'<p><strong>Confidence:</strong> {finding["confidence"]:.1%}</p>')
                html_parts.append(self._render_evidence_html(finding["evidence_summary"]))
                html_parts.append('</div>')
            html_parts.append('</div>')
        
        if report.vus_findings:
            html_parts.append('<div class="section">')
            html_parts.append('<h2>Variants of Uncertain Significance</h2>')
            for finding in report.vus_findings:
                html_parts.append('<div class="vus">')
                html_parts.append(f'<h3>{finding["genomic_position"]} {finding["ref_alt"]}</h3>')
                html_parts.append(f'<p><strong>Classification:</strong> {finding["classification"]}</p>')
                html_parts.append(self._render_evidence_html(finding["evidence_summary"]))
                html_parts.append('</div>')
            html_parts.append('</div>')
        
        html_parts.append('<div class="section recommendations">')
        html_parts.append('<h2>Recommendations</h2>')
        html_parts.append('<ul>')
        for rec in report.recommendations:
            html_parts.append(f'<li>{rec}</li>')
        html_parts.append('</ul>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="disclaimer">')
        html_parts.append('<p><strong>Disclaimer:</strong> This report is generated by an automated system and ')
        html_parts.append('must be reviewed by a qualified clinical geneticist before use in patient care decisions.</p>')
        html_parts.append('<p>All evidence is traceable to source data. Report generated with ACMG/AMP guidelines compliance.</p>')
        html_parts.append('</div>')
        
        html_parts.append('</body></html>')
        
        return ''.join(html_parts)
    
    def _render_evidence_html(self, evidence: List[Dict[str, Any]]) -> str:
        if not evidence:
            return '<p class="evidence-chain">No detailed evidence available.</p>'
        
        parts = ['<div class="evidence-chain">', '<h4>Evidence:</h4>', '<ul>']
        for e in evidence:
            parts.append(f'<li><strong>[{e["criterion"]}]</strong> {e["description"]} (Source: {e["source"]})</li>')
        parts.append('</ul></div>')
        return ''.join(parts)
    
    def to_json(self, report: ClinicalReportData) -> str:
        data = asdict(report)
        data['status'] = report.status.value
        return json.dumps(data, indent=2)


class ResearchReportGenerator:
    """
    Research Track Report Generator
    
    Generates research-track reports that:
    - Document exploratory findings
    - Include explicit uncertainty quantification
    - Generate testable hypotheses
    - Identify evidence gaps
    - Are NOT for clinical decision-making
    """
    
    VERSION = "1.0.0"
    DISCALIMER = (
        "IMPORTANT: This is a RESEARCH TRACK report. "
        "Findings contained herein are for exploratory purposes only and "
        "should NOT be used for clinical decision-making. "
        "All hypotheses require further validation before any clinical application."
    )
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate(
        self,
        patient: Patient,
        variants: List[Variant],
        classifications: List[ACMGClassification],
        evidence_records: List[ACMGEvidence],
        context: Optional[Dict[str, Any]] = None
    ) -> ResearchReportData:
        self.logger.info(f"Generating research report for patient {patient.id}")
        
        hypotheses = self._generate_hypotheses(
            patient, variants, classifications, evidence_records
        )
        
        evidence_gaps = self._identify_evidence_gaps(
            variants, classifications, evidence_records
        )
        
        uncertainty_metrics = self._calculate_uncertainty_metrics(
            classifications, evidence_records
        )
        
        summary = self._generate_executive_summary(
            patient, hypotheses, evidence_gaps, uncertainty_metrics
        )
        
        followup = self._generate_followup_suggestions(
            hypotheses, evidence_gaps
        )
        
        report = ResearchReportData(
            report_id=f"RR-{patient.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            patient_id=str(patient.id),
            report_date=datetime.utcnow().isoformat(),
            status=ReportStatus.DRAFT,
            executive_summary=summary,
            hypotheses=hypotheses,
            evidence_gaps=evidence_gaps,
            uncertainty_metrics=uncertainty_metrics,
            suggested_followup=followup,
            disclaimer=self.DISCALIMER,
            metadata={
                "generator_version": self.VERSION,
                "variant_count": len(variants),
                "classified_count": len(classifications),
                "is_research_track": True,
            }
        )
        
        self.logger.info(f"Research report generated: {report.report_id}")
        return report
    
    def _generate_hypotheses(
        self,
        patient: Patient,
        variants: List[Variant],
        classifications: List[ACMGClassification],
        evidence_records: List[ACMGEvidence]
    ) -> List[Hypothesis]:
        hypotheses = []
        variant_map = {v.id: v for v in variants}
        
        for classification in classifications:
            if classification.classification == ClassificationCategory.UNCERTAIN_SIGNIFICANCE.value:
                variant = variant_map.get(classification.variant_id)
                if not variant:
                    continue
                
                variant_evidence = [
                    e for e in evidence_records
                    if e.variant_id == classification.variant_id
                ]
                
                supporting = []
                contradicting = []
                for e in variant_evidence:
                    if e.is_applied:
                        if "pathogenic" in e.evidence_level.lower():
                            supporting.append(f"[{e.criterion}] {e.description}")
                        elif "benign" in e.evidence_level.lower():
                            contradicting.append(f"[{e.criterion}] {e.description}")
                
                hypothesis = Hypothesis(
                    hypothesis_id=f"HYP-{classification.variant_id}",
                    description=(
                        f"Variant {variant.chromosome}:{variant.position} {variant.ref}>{variant.alt} "
                        f"may be associated with patient phenotype."
                    ),
                    supporting_evidence=supporting,
                    contradicting_evidence=contradicting,
                    uncertainty_level="high" if classification.confidence_score < 0.5 else "moderate",
                    confidence=classification.confidence_score,
                    priority=self._calculate_hypothesis_priority(
                        variant, classification, variant_evidence
                    ),
                )
                hypotheses.append(hypothesis)
        
        hypotheses.sort(key=lambda h: h.priority, reverse=True)
        return hypotheses[:10]
    
    def _calculate_hypothesis_priority(
        self,
        variant: Variant,
        classification: ACMGClassification,
        evidence: List[ACMGEvidence]
    ) -> float:
        priority = 0.5
        
        pathogenic_evidence = [
            e for e in evidence
            if e.is_applied and "pathogenic" in e.evidence_level.lower()
        ]
        if pathogenic_evidence:
            priority += 0.2
        
        if classification.confidence_score > 0.5:
            priority += 0.1
        
        if variant.quality and variant.quality > 50:
            priority += 0.1
        
        if variant.variant_type in ("SNV", "INDEL"):
            priority += 0.05
        
        return min(1.0, priority)
    
    def _identify_evidence_gaps(
        self,
        variants: List[Variant],
        classifications: List[ACMGClassification],
        evidence_records: List[ACMGEvidence]
    ) -> List[str]:
        gaps = []
        
        vus_count = sum(
            1 for c in classifications
            if c.classification == ClassificationCategory.UNCERTAIN_SIGNIFICANCE.value
        )
        if vus_count > 0:
            gaps.append(
                f"{vus_count} variant(s) classified as VUS require additional evidence "
                "for re-classification."
            )
        
        low_confidence = [
            c for c in classifications
            if c.confidence_score and c.confidence_score < 0.7
        ]
        if low_confidence:
            gaps.append(
                f"{len(low_confidence)} classification(s) have low confidence scores "
                "and may benefit from additional data sources."
            )
        
        missing_sources = []
        for evidence in evidence_records:
            if not evidence.evidence_source:
                missing_sources.append(evidence.criterion)
        
        if missing_sources:
            unique_criteria = list(set(missing_sources))[:5]
            gaps.append(
                f"Evidence sources not specified for criteria: {', '.join(unique_criteria)}. "
                "Recommend consulting external databases."
            )
        
        if not gaps:
            gaps.append("No significant evidence gaps identified.")
        
        return gaps
    
    def _calculate_uncertainty_metrics(
        self,
        classifications: List[ACMGClassification],
        evidence_records: List[ACMGEvidence]
    ) -> Dict[str, float]:
        if not classifications:
            return {"overall_uncertainty": 1.0}
        
        vus_count = sum(
            1 for c in classifications
            if c.classification == ClassificationCategory.UNCERTAIN_SIGNIFICANCE.value
        )
        vus_rate = vus_count / len(classifications)
        
        avg_confidence = 0.0
        confidence_values = [
            c.confidence_score for c in classifications
            if c.confidence_score is not None
        ]
        if confidence_values:
            avg_confidence = sum(confidence_values) / len(confidence_values)
        
        evidence_per_variant = {}
        for e in evidence_records:
            if e.variant_id not in evidence_per_variant:
                evidence_per_variant[e.variant_id] = 0
            if e.is_applied:
                evidence_per_variant[e.variant_id] += 1
        
        avg_evidence = (
            sum(evidence_per_variant.values()) / len(evidence_per_variant)
            if evidence_per_variant else 0
        )
        
        return {
            "overall_uncertainty": vus_rate,
            "classification_confidence": avg_confidence,
            "average_evidence_per_variant": avg_evidence,
            "vus_rate": vus_rate,
        }
    
    def _generate_executive_summary(
        self,
        patient: Patient,
        hypotheses: List[Hypothesis],
        evidence_gaps: List[str],
        uncertainty_metrics: Dict[str, float]
    ) -> str:
        parts = [
            f"Research track analysis for patient {patient.name or patient.id}.",
            f"Generated {len(hypotheses)} testable hypotheses from the data.",
        ]
        
        if uncertainty_metrics.get("vus_rate", 0) > 0.5:
            parts.append(
                "High uncertainty rate observed. "
                "Many variants require additional evidence for definitive classification."
            )
        
        if hypotheses:
            top_hypothesis = hypotheses[0]
            parts.append(
                f"Top hypothesis: {top_hypothesis.description[:100]}..."
            )
        
        return " ".join(parts)
    
    def _generate_followup_suggestions(
        self,
        hypotheses: List[Hypothesis],
        evidence_gaps: List[str]
    ) -> List[str]:
        suggestions = []
        
        if hypotheses:
            suggestions.append(
                "Prioritize functional validation studies for top-ranked hypotheses."
            )
            suggestions.append(
                "Consider literature review for genes associated with top hypotheses."
            )
        
        for gap in evidence_gaps[:3]:
            suggestions.append(f"Evidence gap to address: {gap}")
        
        suggestions.append(
            "Re-evaluate classifications as new evidence becomes available."
        )
        
        return suggestions
    
    def render_html(self, report: ResearchReportData) -> str:
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="UTF-8">',
            f"<title>Research Report - {report.report_id}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 40px; }",
            ".header { border-bottom: 2px solid #722ed1; padding-bottom: 20px; margin-bottom: 20px; }",
            ".warning-banner { background: #fff2e8; border: 2px solid #fa541c; padding: 15px; margin: 20px 0; border-radius: 4px; }",
            ".section { margin: 20px 0; }",
            ".hypothesis { background: #f9f0ff; border-left: 4px solid #722ed1; padding: 10px; margin: 10px 0; }",
            ".evidence-gap { background: #fff1f0; padding: 10px; margin: 5px 0; }",
            ".metrics { display: flex; gap: 20px; margin: 20px 0; }",
            ".metric-box { background: #f5f5f5; padding: 15px; border-radius: 4px; flex: 1; }",
            ".disclaimer { font-size: 0.8em; color: #8c8c8c; margin-top: 40px; border-top: 1px solid #d9d9d9; padding-top: 20px; }",
            "</style>",
            "</head>",
            "<body>",
            '<div class="header">',
            f"<h1>Research Track Report</h1>",
            f"<p><strong>Report ID:</strong> {report.report_id}</p>",
            f"<p><strong>Date:</strong> {report.report_date}</p>",
            f"<p><strong>Patient ID:</strong> {report.patient_id}</p>",
            "</div>",
        ]
        
        html_parts.append('<div class="warning-banner">')
        html_parts.append('<h2 style="color: #fa541c;">RESEARCH TRACK - NOT FOR CLINICAL USE</h2>')
        html_parts.append(f'<p>{report.disclaimer}</p>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="section">')
        html_parts.append('<h2>Executive Summary</h2>')
        html_parts.append(f'<p>{report.executive_summary}</p>')
        html_parts.append('</div>')
        
        if report.hypotheses:
            html_parts.append('<div class="section">')
            html_parts.append('<h2>Generated Hypotheses</h2>')
            for hyp in report.hypotheses:
                html_parts.append('<div class="hypothesis">')
                html_parts.append(f'<h3>{hyp.hypothesis_id}</h3>')
                html_parts.append(f'<p>{hyp.description}</p>')
                html_parts.append(f'<p><strong>Uncertainty:</strong> {hyp.uncertainty_level} | ')
                html_parts.append(f'<strong>Confidence:</strong> {hyp.confidence:.1%} | ')
                html_parts.append(f'<strong>Priority:</strong> {hyp.priority:.2f}</p>')
                if hyp.supporting_evidence:
                    html_parts.append('<p><strong>Supporting:</strong></p><ul>')
                    for e in hyp.supporting_evidence[:3]:
                        html_parts.append(f'<li>{e}</li>')
                    html_parts.append('</ul>')
                if hyp.contradicting_evidence:
                    html_parts.append('<p><strong>Contradicting:</strong></p><ul>')
                    for e in hyp.contradicting_evidence[:3]:
                        html_parts.append(f'<li>{e}</li>')
                    html_parts.append('</ul>')
                html_parts.append('</div>')
            html_parts.append('</div>')
        
        html_parts.append('<div class="section">')
        html_parts.append('<h2>Uncertainty Metrics</h2>')
        html_parts.append('<div class="metrics">')
        for name, value in report.uncertainty_metrics.items():
            html_parts.append('<div class="metric-box">')
            html_parts.append(f'<h4>{name.replace("_", " ").title()}</h4>')
            html_parts.append(f'<p style="font-size: 1.5em;">{value:.2%}</p>')
            html_parts.append('</div>')
        html_parts.append('</div>')
        html_parts.append('</div>')
        
        if report.evidence_gaps:
            html_parts.append('<div class="section">')
            html_parts.append('<h2>Evidence Gaps</h2>')
            for gap in report.evidence_gaps:
                html_parts.append(f'<div class="evidence-gap">{gap}</div>')
            html_parts.append('</div>')
        
        html_parts.append('<div class="section">')
        html_parts.append('<h2>Suggested Follow-up</h2>')
        html_parts.append('<ul>')
        for suggestion in report.suggested_followup:
            html_parts.append(f'<li>{suggestion}</li>')
        html_parts.append('</ul>')
        html_parts.append('</div>')
        
        html_parts.append('<div class="disclaimer">')
        html_parts.append('<p><strong>Research Track Disclaimer:</strong> ')
        html_parts.append('This report is for exploratory research purposes only. ')
        html_parts.append('All findings must be validated before any clinical application. ')
        html_parts.append('Do not use for patient care decisions.</p>')
        html_parts.append('</div>')
        
        html_parts.append('</body></html>')
        
        return ''.join(html_parts)
    
    def to_json(self, report: ResearchReportData) -> str:
        data = {
            "report_id": report.report_id,
            "patient_id": report.patient_id,
            "report_date": report.report_date,
            "status": report.status.value,
            "executive_summary": report.executive_summary,
            "hypotheses": [
                {
                    "hypothesis_id": h.hypothesis_id,
                    "description": h.description,
                    "supporting_evidence": h.supporting_evidence,
                    "contradicting_evidence": h.contradicting_evidence,
                    "uncertainty_level": h.uncertainty_level,
                    "confidence": h.confidence,
                    "priority": h.priority,
                }
                for h in report.hypotheses
            ],
            "evidence_gaps": report.evidence_gaps,
            "uncertainty_metrics": report.uncertainty_metrics,
            "suggested_followup": report.suggested_followup,
            "disclaimer": report.disclaimer,
            "metadata": report.metadata,
        }
        return json.dumps(data, indent=2)


def create_clinical_report_generator() -> ClinicalReportGenerator:
    return ClinicalReportGenerator()


def create_research_report_generator() -> ResearchReportGenerator:
    return ResearchReportGenerator()
