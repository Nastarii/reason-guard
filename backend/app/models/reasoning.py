from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ReasoningTrace(Base):
    """Module 1: Reasoning Tracer (CoT) - Stores chain of thought traces."""
    __tablename__ = "reasoning_traces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    original_prompt = Column(Text, nullable=False)
    enhanced_prompt = Column(Text, nullable=False)
    raw_response = Column(Text, nullable=False)
    parsed_reasoning = Column(JSON, nullable=True)

    model_provider = Column(String, nullable=False)
    model_name = Column(String, nullable=False)

    integrity_hash = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reasoning_traces")
    steps = relationship("ReasoningStep", back_populates="trace", cascade="all, delete-orphan")


class ReasoningStep(Base):
    """Individual steps in a reasoning chain."""
    __tablename__ = "reasoning_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id = Column(UUID(as_uuid=True), ForeignKey("reasoning_traces.id"), nullable=False)

    step_number = Column(Integer, nullable=False)
    step_type = Column(String, nullable=False)  # premise, inference, conclusion
    content = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trace = relationship("ReasoningTrace", back_populates="steps")


class PathAnalysis(Base):
    """Module 2: Path Analyzer (ToT) - Tree of Thought analysis."""
    __tablename__ = "path_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    original_problem = Column(Text, nullable=False)
    decomposition = Column(JSON, nullable=False)  # Subproblems
    exploration_tree = Column(JSON, nullable=False)  # Full tree structure
    pruned_paths = Column(JSON, nullable=True)  # Paths that were pruned
    selected_path = Column(JSON, nullable=True)  # Best path selected

    total_nodes_explored = Column(Integer, default=0)
    total_paths_pruned = Column(Integer, default=0)

    model_provider = Column(String, nullable=False)
    model_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="path_analyses")
    nodes = relationship("PathNode", back_populates="analysis", cascade="all, delete-orphan")


class PathNode(Base):
    """Individual nodes in a Tree of Thought."""
    __tablename__ = "path_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("path_analyses.id"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("path_nodes.id"), nullable=True)

    depth = Column(Integer, nullable=False)
    hypothesis = Column(Text, nullable=False)
    evaluation_score = Column(Float, nullable=True)
    is_pruned = Column(Boolean, default=False)
    pruning_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analysis = relationship("PathAnalysis", back_populates="nodes")
    children = relationship("PathNode", backref="parent", remote_side=[id])


class LogicGraph(Base):
    """Module 3: Logic Validator (GoT) - Graph of Thought for logic validation."""
    __tablename__ = "logic_graphs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reasoning_trace_id = Column(UUID(as_uuid=True), ForeignKey("reasoning_traces.id"), nullable=True)

    graph_structure = Column(JSON, nullable=False)  # Full graph as JSON

    # Validation results
    has_contradictions = Column(Boolean, default=False)
    has_logic_gaps = Column(Boolean, default=False)
    has_hidden_premises = Column(Boolean, default=False)
    has_circularity = Column(Boolean, default=False)

    contradictions = Column(JSON, nullable=True)
    logic_gaps = Column(JSON, nullable=True)
    hidden_premises = Column(JSON, nullable=True)
    circular_references = Column(JSON, nullable=True)

    overall_validity_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="logic_graphs")
    nodes = relationship("LogicNode", back_populates="graph", cascade="all, delete-orphan")
    edges = relationship("LogicEdge", back_populates="graph", cascade="all, delete-orphan")


class LogicNode(Base):
    """Propositions in a logic graph."""
    __tablename__ = "logic_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_id = Column(UUID(as_uuid=True), ForeignKey("logic_graphs.id"), nullable=False)

    node_type = Column(String, nullable=False)  # premise, inference, conclusion, hidden_premise
    content = Column(Text, nullable=False)
    truth_value = Column(Boolean, nullable=True)
    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    graph = relationship("LogicGraph", back_populates="nodes")


class LogicEdge(Base):
    """Logical connections between propositions."""
    __tablename__ = "logic_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_id = Column(UUID(as_uuid=True), ForeignKey("logic_graphs.id"), nullable=False)

    source_node_id = Column(UUID(as_uuid=True), ForeignKey("logic_nodes.id"), nullable=False)
    target_node_id = Column(UUID(as_uuid=True), ForeignKey("logic_nodes.id"), nullable=False)

    edge_type = Column(String, nullable=False)  # supports, contradicts, implies, depends_on
    strength = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    graph = relationship("LogicGraph", back_populates="edges")


class ConsistencyCheck(Base):
    """Module 4: Consistency Checker - Multi-run consistency analysis."""
    __tablename__ = "consistency_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    original_query = Column(Text, nullable=False)
    query_variations = Column(JSON, nullable=False)  # List of query variations used

    responses = Column(JSON, nullable=False)  # All responses from multiple runs

    convergence_rate = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    divergent_points = Column(JSON, nullable=True)

    total_runs = Column(Integer, nullable=False)

    model_provider = Column(String, nullable=False)
    model_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="consistency_checks")


class AuditReport(Base):
    """Module 5: Audit Trail Generator - Consolidated reports."""
    __tablename__ = "audit_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    report_type = Column(String, nullable=False)  # compliance, legal, technical
    format = Column(String, nullable=False)  # pdf, json, excel

    # References to analyzed data
    reasoning_trace_ids = Column(JSON, nullable=True)
    path_analysis_ids = Column(JSON, nullable=True)
    logic_graph_ids = Column(JSON, nullable=True)
    consistency_check_ids = Column(JSON, nullable=True)

    report_data = Column(JSON, nullable=False)
    file_path = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_reports")
