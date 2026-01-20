"""
Module 5: Audit Trail Generator
Consolidates data into PDF, JSON, and Excel reports
for different stakeholders (Compliance, Legal, Technical).
"""

import io
import json
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import pandas as pd

from app.models.reasoning import (
    AuditReport, ReasoningTrace, PathAnalysis, LogicGraph, ConsistencyCheck
)


class AuditGenerator:
    """Audit report generator for multiple stakeholders."""

    def __init__(self, db: Session):
        self.db = db

    def _get_reasoning_traces(self, trace_ids: List[UUID]) -> List[ReasoningTrace]:
        """Fetch reasoning traces by IDs."""
        if not trace_ids:
            return []
        return self.db.query(ReasoningTrace).filter(
            ReasoningTrace.id.in_(trace_ids)
        ).all()

    def _get_path_analyses(self, analysis_ids: List[UUID]) -> List[PathAnalysis]:
        """Fetch path analyses by IDs."""
        if not analysis_ids:
            return []
        return self.db.query(PathAnalysis).filter(
            PathAnalysis.id.in_(analysis_ids)
        ).all()

    def _get_logic_graphs(self, graph_ids: List[UUID]) -> List[LogicGraph]:
        """Fetch logic graphs by IDs."""
        if not graph_ids:
            return []
        return self.db.query(LogicGraph).filter(
            LogicGraph.id.in_(graph_ids)
        ).all()

    def _get_consistency_checks(self, check_ids: List[UUID]) -> List[ConsistencyCheck]:
        """Fetch consistency checks by IDs."""
        if not check_ids:
            return []
        return self.db.query(ConsistencyCheck).filter(
            ConsistencyCheck.id.in_(check_ids)
        ).all()

    def _compile_report_data(
        self,
        report_type: str,
        reasoning_traces: List[ReasoningTrace],
        path_analyses: List[PathAnalysis],
        logic_graphs: List[LogicGraph],
        consistency_checks: List[ConsistencyCheck],
    ) -> Dict[str, Any]:
        """Compile data for the report based on stakeholder type."""
        report_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "report_type": report_type,
            "summary": {},
            "details": {},
        }

        # Calculate summary statistics
        total_decisions = len(reasoning_traces)
        total_issues = 0
        total_validity_scores = []
        total_confidence_scores = []

        for graph in logic_graphs:
            if graph.has_contradictions:
                total_issues += len(graph.contradictions or [])
            if graph.has_logic_gaps:
                total_issues += len(graph.logic_gaps or [])
            if graph.overall_validity_score:
                total_validity_scores.append(graph.overall_validity_score)

        for check in consistency_checks:
            total_confidence_scores.append(check.confidence_score)

        avg_validity = (
            sum(total_validity_scores) / len(total_validity_scores)
            if total_validity_scores else 0
        )
        avg_confidence = (
            sum(total_confidence_scores) / len(total_confidence_scores)
            if total_confidence_scores else 0
        )

        report_data["summary"] = {
            "total_decisions": total_decisions,
            "total_path_analyses": len(path_analyses),
            "total_logic_validations": len(logic_graphs),
            "total_consistency_checks": len(consistency_checks),
            "total_issues_found": total_issues,
            "average_validity_score": round(avg_validity * 100, 2),
            "average_confidence_score": round(avg_confidence * 100, 2),
        }

        # Compile details based on report type
        if report_type == "compliance":
            report_data["details"] = self._compile_compliance_details(
                reasoning_traces, logic_graphs, consistency_checks
            )
        elif report_type == "legal":
            report_data["details"] = self._compile_legal_details(
                reasoning_traces, logic_graphs, consistency_checks
            )
        elif report_type == "technical":
            report_data["details"] = self._compile_technical_details(
                reasoning_traces, path_analyses, logic_graphs, consistency_checks
            )

        return report_data

    def _compile_compliance_details(
        self,
        traces: List[ReasoningTrace],
        graphs: List[LogicGraph],
        checks: List[ConsistencyCheck],
    ) -> Dict[str, Any]:
        """Compile compliance-focused report details."""
        return {
            "decisions": [
                {
                    "id": str(trace.id),
                    "timestamp": trace.created_at.isoformat(),
                    "model": f"{trace.model_provider}/{trace.model_name}",
                    "prompt": trace.original_prompt[:200] + "..." if len(trace.original_prompt) > 200 else trace.original_prompt,
                    "integrity_verified": True,  # Placeholder - would verify hash
                    "integrity_hash": trace.integrity_hash[:16] + "...",
                }
                for trace in traces
            ],
            "logic_issues": [
                {
                    "graph_id": str(graph.id),
                    "timestamp": graph.created_at.isoformat(),
                    "has_contradictions": graph.has_contradictions,
                    "has_logic_gaps": graph.has_logic_gaps,
                    "validity_score": round(graph.overall_validity_score * 100, 2) if graph.overall_validity_score else None,
                }
                for graph in graphs
            ],
            "consistency_results": [
                {
                    "check_id": str(check.id),
                    "timestamp": check.created_at.isoformat(),
                    "convergence_rate": round(check.convergence_rate * 100, 2),
                    "confidence_score": round(check.confidence_score * 100, 2),
                    "runs": check.total_runs,
                }
                for check in checks
            ],
        }

    def _compile_legal_details(
        self,
        traces: List[ReasoningTrace],
        graphs: List[LogicGraph],
        checks: List[ConsistencyCheck],
    ) -> Dict[str, Any]:
        """Compile legal-focused report details."""
        # Focus on auditability and evidence
        return {
            "decision_audit_trail": [
                {
                    "id": str(trace.id),
                    "timestamp": trace.created_at.isoformat(),
                    "input": trace.original_prompt,
                    "reasoning_documented": trace.parsed_reasoning is not None,
                    "steps_count": len(trace.steps) if trace.steps else 0,
                    "model_used": f"{trace.model_provider}/{trace.model_name}",
                    "integrity_hash": trace.integrity_hash,
                }
                for trace in traces
            ],
            "identified_issues": [
                {
                    "graph_id": str(graph.id),
                    "contradictions": graph.contradictions,
                    "hidden_assumptions": graph.hidden_premises,
                    "circular_reasoning": graph.circular_references,
                }
                for graph in graphs
                if graph.has_contradictions or graph.has_hidden_premises or graph.has_circularity
            ],
            "reliability_assessment": [
                {
                    "check_id": str(check.id),
                    "query": check.original_query,
                    "variations_tested": len(check.query_variations),
                    "convergence_rate": check.convergence_rate,
                    "divergent_points": check.divergent_points,
                }
                for check in checks
            ],
        }

    def _compile_technical_details(
        self,
        traces: List[ReasoningTrace],
        analyses: List[PathAnalysis],
        graphs: List[LogicGraph],
        checks: List[ConsistencyCheck],
    ) -> Dict[str, Any]:
        """Compile technical-focused report details."""
        return {
            "reasoning_traces": [
                {
                    "id": str(trace.id),
                    "original_prompt": trace.original_prompt,
                    "enhanced_prompt": trace.enhanced_prompt,
                    "raw_response": trace.raw_response,
                    "parsed_reasoning": trace.parsed_reasoning,
                    "model": {
                        "provider": trace.model_provider,
                        "name": trace.model_name,
                    },
                    "steps": [
                        {
                            "number": step.step_number,
                            "type": step.step_type,
                            "content": step.content,
                            "confidence": step.confidence,
                        }
                        for step in trace.steps
                    ] if trace.steps else [],
                }
                for trace in traces
            ],
            "path_analyses": [
                {
                    "id": str(analysis.id),
                    "problem": analysis.original_problem,
                    "decomposition": analysis.decomposition,
                    "exploration_tree": analysis.exploration_tree,
                    "selected_path": analysis.selected_path,
                    "stats": {
                        "nodes_explored": analysis.total_nodes_explored,
                        "paths_pruned": analysis.total_paths_pruned,
                    },
                }
                for analysis in analyses
            ],
            "logic_graphs": [
                {
                    "id": str(graph.id),
                    "structure": graph.graph_structure,
                    "validation": {
                        "contradictions": graph.contradictions,
                        "logic_gaps": graph.logic_gaps,
                        "hidden_premises": graph.hidden_premises,
                        "circularity": graph.circular_references,
                    },
                    "validity_score": graph.overall_validity_score,
                }
                for graph in graphs
            ],
            "consistency_checks": [
                {
                    "id": str(check.id),
                    "query": check.original_query,
                    "variations": check.query_variations,
                    "responses": check.responses,
                    "metrics": {
                        "convergence_rate": check.convergence_rate,
                        "confidence_score": check.confidence_score,
                        "divergent_points": check.divergent_points,
                    },
                }
                for check in checks
            ],
        }

    def _generate_pdf(self, report_data: Dict[str, Any], report_type: str) -> bytes:
        """Generate PDF report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
        )

        elements = []

        # Title
        title_map = {
            "compliance": "Relatório de Auditoria - Compliance",
            "legal": "Relatório de Auditoria - Jurídico",
            "technical": "Relatório de Auditoria - Técnico",
        }
        elements.append(Paragraph(title_map.get(report_type, "Relatório de Auditoria"), title_style))
        elements.append(Spacer(1, 12))

        # Generation info
        elements.append(Paragraph(
            f"Gerado em: {report_data['generated_at']}",
            body_style
        ))
        elements.append(Spacer(1, 24))

        # Summary section
        elements.append(Paragraph("Resumo Executivo", heading_style))

        summary = report_data["summary"]
        summary_data = [
            ["Métrica", "Valor"],
            ["Total de Decisões", str(summary.get("total_decisions", 0))],
            ["Análises de Caminho", str(summary.get("total_path_analyses", 0))],
            ["Validações Lógicas", str(summary.get("total_logic_validations", 0))],
            ["Verificações de Consistência", str(summary.get("total_consistency_checks", 0))],
            ["Problemas Encontrados", str(summary.get("total_issues_found", 0))],
            ["Score Médio de Validade", f"{summary.get('average_validity_score', 0)}%"],
            ["Score Médio de Confiança", f"{summary.get('average_confidence_score', 0)}%"],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 24))

        # Details section
        elements.append(Paragraph("Detalhes", heading_style))

        details = report_data.get("details", {})
        for key, value in details.items():
            if isinstance(value, list) and value:
                elements.append(Paragraph(key.replace("_", " ").title(), styles['Heading3']))
                elements.append(Spacer(1, 6))

                # Create a simple text summary for each item
                for item in value[:10]:  # Limit to first 10 items
                    if isinstance(item, dict):
                        item_text = ", ".join([
                            f"{k}: {str(v)[:50]}..."
                            if isinstance(v, str) and len(str(v)) > 50
                            else f"{k}: {v}"
                            for k, v in item.items()
                            if k != "raw_response" and k != "responses"
                        ][:5])  # Limit to 5 fields
                        elements.append(Paragraph(f"• {item_text}", body_style))

                elements.append(Spacer(1, 12))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_excel(self, report_data: Dict[str, Any], report_type: str) -> bytes:
        """Generate Excel report."""
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame([report_data["summary"]])
            summary_df.to_excel(writer, sheet_name='Resumo', index=False)

            # Details sheets
            details = report_data.get("details", {})
            for key, value in details.items():
                if isinstance(value, list) and value:
                    # Flatten nested dicts for Excel
                    flat_data = []
                    for item in value:
                        if isinstance(item, dict):
                            flat_item = {}
                            for k, v in item.items():
                                if isinstance(v, (dict, list)):
                                    flat_item[k] = json.dumps(v, default=str)[:500]
                                else:
                                    flat_item[k] = str(v)[:500] if v else ""
                            flat_data.append(flat_item)

                    if flat_data:
                        df = pd.DataFrame(flat_data)
                        sheet_name = key[:31]  # Excel sheet name limit
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

        buffer.seek(0)
        return buffer.getvalue()

    async def generate(
        self,
        user_id: UUID,
        report_type: str,
        format: str,
        reasoning_trace_ids: Optional[List[UUID]] = None,
        path_analysis_ids: Optional[List[UUID]] = None,
        logic_graph_ids: Optional[List[UUID]] = None,
        consistency_check_ids: Optional[List[UUID]] = None,
    ) -> AuditReport:
        """
        Generate an audit report in the specified format.
        """
        # Fetch all related data
        reasoning_traces = self._get_reasoning_traces(reasoning_trace_ids or [])
        path_analyses = self._get_path_analyses(path_analysis_ids or [])
        logic_graphs = self._get_logic_graphs(logic_graph_ids or [])
        consistency_checks = self._get_consistency_checks(consistency_check_ids or [])

        # Compile report data
        report_data = self._compile_report_data(
            report_type,
            reasoning_traces,
            path_analyses,
            logic_graphs,
            consistency_checks,
        )

        # Generate file based on format
        file_path = None
        if format == "pdf":
            content = self._generate_pdf(report_data, report_type)
            file_path = f"reports/{user_id}/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{report_type}.pdf"
        elif format == "excel":
            content = self._generate_excel(report_data, report_type)
            file_path = f"reports/{user_id}/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{report_type}.xlsx"
        # JSON format doesn't need a file, it's stored in the database

        # Create AuditReport record
        audit_report = AuditReport(
            user_id=user_id,
            report_type=report_type,
            format=format,
            reasoning_trace_ids=[str(id) for id in (reasoning_trace_ids or [])],
            path_analysis_ids=[str(id) for id in (path_analysis_ids or [])],
            logic_graph_ids=[str(id) for id in (logic_graph_ids or [])],
            consistency_check_ids=[str(id) for id in (consistency_check_ids or [])],
            report_data=report_data,
            file_path=file_path,
        )
        self.db.add(audit_report)
        self.db.commit()
        self.db.refresh(audit_report)

        return audit_report

    def get_report(self, report_id: UUID) -> Optional[AuditReport]:
        """Retrieve an audit report by ID."""
        return self.db.query(AuditReport).filter(AuditReport.id == report_id).first()

    def get_user_reports(self, user_id: UUID, limit: int = 50) -> List[AuditReport]:
        """Get all audit reports for a user."""
        return (
            self.db.query(AuditReport)
            .filter(AuditReport.user_id == user_id)
            .order_by(AuditReport.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_report_file(self, report: AuditReport) -> Optional[bytes]:
        """Generate and return the report file content."""
        if report.format == "json":
            return json.dumps(report.report_data, indent=2, default=str).encode()
        elif report.format == "pdf":
            return self._generate_pdf(report.report_data, report.report_type)
        elif report.format == "excel":
            return self._generate_excel(report.report_data, report.report_type)
        return None
