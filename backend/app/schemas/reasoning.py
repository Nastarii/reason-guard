from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class ModelProvider(str, Enum):
    OPENAI = "openai"


class StepType(str, Enum):
    PREMISE = "premise"
    INFERENCE = "inference"
    CONCLUSION = "conclusion"


class NodeType(str, Enum):
    PREMISE = "premise"
    INFERENCE = "inference"
    CONCLUSION = "conclusion"
    HIDDEN_PREMISE = "hidden_premise"


class EdgeType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    IMPLIES = "implies"
    DEPENDS_ON = "depends_on"


class ReportType(str, Enum):
    COMPLIANCE = "compliance"
    LEGAL = "legal"
    TECHNICAL = "technical"


class ReportFormat(str, Enum):
    PDF = "pdf"
    JSON = "json"
    EXCEL = "excel"


# Proxy Request/Response
class ProxyRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    prompt: str
    model_provider: ModelProvider = ModelProvider.OPENAI
    model_name: Optional[str] = None
    enable_cot: bool = True
    enable_tot: bool = False
    enable_got: bool = False
    enable_consistency: bool = False
    consistency_runs: int = Field(default=3, ge=2, le=10)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = None


class ProxyResponse(BaseModel):
    response: str
    reasoning_trace_id: Optional[UUID] = None
    path_analysis_id: Optional[UUID] = None
    logic_graph_id: Optional[UUID] = None
    consistency_check_id: Optional[UUID] = None
    metadata: Dict[str, Any] = {}


# Reasoning Trace Schemas
class ReasoningStepResponse(BaseModel):
    id: UUID
    step_number: int
    step_type: str
    content: str
    confidence: Optional[float]

    class Config:
        from_attributes = True


class ReasoningTraceCreate(BaseModel):
    model_config = {"protected_namespaces": ()}

    original_prompt: str
    model_provider: ModelProvider
    model_name: Optional[str] = None


class ReasoningTraceResponse(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: UUID
    original_prompt: str
    enhanced_prompt: str
    raw_response: str
    parsed_reasoning: Optional[Dict[str, Any]]
    model_provider: str
    model_name: str
    integrity_hash: str
    created_at: datetime
    steps: List[ReasoningStepResponse] = []


# Path Analysis Schemas
class PathNodeResponse(BaseModel):
    id: UUID
    parent_id: Optional[UUID]
    depth: int
    hypothesis: str
    evaluation_score: Optional[float]
    is_pruned: bool
    pruning_reason: Optional[str]

    class Config:
        from_attributes = True


class PathAnalysisCreate(BaseModel):
    model_config = {"protected_namespaces": ()}

    problem: str
    model_provider: ModelProvider
    model_name: Optional[str] = None
    max_depth: int = Field(default=3, ge=1, le=5)
    breadth: int = Field(default=3, ge=2, le=5)


class PathAnalysisResponse(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: UUID
    original_problem: str
    decomposition: Dict[str, Any]
    exploration_tree: Dict[str, Any]
    pruned_paths: Optional[List[Dict[str, Any]]]
    selected_path: Optional[Dict[str, Any]]
    total_nodes_explored: int
    total_paths_pruned: int
    model_provider: str
    model_name: str
    created_at: datetime


# Logic Graph Schemas
class LogicNodeCreate(BaseModel):
    node_type: NodeType
    content: str
    truth_value: Optional[bool] = None
    confidence: Optional[float] = None


class LogicEdgeCreate(BaseModel):
    source_node_id: UUID
    target_node_id: UUID
    edge_type: EdgeType
    strength: Optional[float] = None


class LogicGraphCreate(BaseModel):
    reasoning_trace_id: Optional[UUID] = None
    raw_text: Optional[str] = None


class LogicNodeResponse(BaseModel):
    id: UUID
    node_type: str
    content: str
    truth_value: Optional[bool]
    confidence: Optional[float]

    class Config:
        from_attributes = True


class LogicEdgeResponse(BaseModel):
    id: UUID
    source_node_id: UUID
    target_node_id: UUID
    edge_type: str
    strength: Optional[float]

    class Config:
        from_attributes = True


class LogicGraphResponse(BaseModel):
    id: UUID
    reasoning_trace_id: Optional[UUID]
    graph_structure: Dict[str, Any]
    has_contradictions: bool
    has_logic_gaps: bool
    has_hidden_premises: bool
    has_circularity: bool
    contradictions: Optional[List[Dict[str, Any]]]
    logic_gaps: Optional[List[Dict[str, Any]]]
    hidden_premises: Optional[List[Dict[str, Any]]]
    circular_references: Optional[List[Dict[str, Any]]]
    overall_validity_score: Optional[float]
    created_at: datetime
    nodes: List[LogicNodeResponse] = []
    edges: List[LogicEdgeResponse] = []

    class Config:
        from_attributes = True


# Consistency Check Schemas
class ConsistencyCheckCreate(BaseModel):
    model_config = {"protected_namespaces": ()}

    query: str
    model_provider: ModelProvider
    model_name: Optional[str] = None
    num_runs: int = Field(default=5, ge=2, le=10)
    include_variations: bool = True


class ConsistencyCheckResponse(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: UUID
    original_query: str
    query_variations: List[str]
    responses: List[Dict[str, Any]]
    convergence_rate: float
    confidence_score: float
    divergent_points: Optional[List[Dict[str, Any]]]
    total_runs: int
    model_provider: str
    model_name: str
    created_at: datetime


# Audit Report Schemas
class AuditReportCreate(BaseModel):
    report_type: ReportType
    format: ReportFormat
    reasoning_trace_ids: Optional[List[UUID]] = None
    path_analysis_ids: Optional[List[UUID]] = None
    logic_graph_ids: Optional[List[UUID]] = None
    consistency_check_ids: Optional[List[UUID]] = None


class AuditReportResponse(BaseModel):
    id: UUID
    report_type: str
    format: str
    reasoning_trace_ids: Optional[List[UUID]]
    path_analysis_ids: Optional[List[UUID]]
    logic_graph_ids: Optional[List[UUID]]
    consistency_check_ids: Optional[List[UUID]]
    report_data: Dict[str, Any]
    file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_decisions: int
    consistency_rate: float
    critical_alerts: int
    decisions_today: int
    average_validity_score: float
    total_contradictions: int


class RecentActivity(BaseModel):
    id: UUID
    type: str
    description: str
    created_at: datetime
    status: str
