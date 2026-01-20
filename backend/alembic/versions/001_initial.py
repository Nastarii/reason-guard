"""Initial migration

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clerk_user_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clerk_user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_clerk_user_id'), 'users', ['clerk_user_id'], unique=True)

    # Reasoning traces table
    op.create_table('reasoning_traces',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_prompt', sa.Text(), nullable=False),
        sa.Column('enhanced_prompt', sa.Text(), nullable=False),
        sa.Column('raw_response', sa.Text(), nullable=False),
        sa.Column('parsed_reasoning', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('model_provider', sa.String(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('integrity_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Reasoning steps table
    op.create_table('reasoning_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('step_type', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['trace_id'], ['reasoning_traces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Path analyses table
    op.create_table('path_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_problem', sa.Text(), nullable=False),
        sa.Column('decomposition', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('exploration_tree', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('pruned_paths', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('selected_path', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_nodes_explored', sa.Integer(), nullable=True),
        sa.Column('total_paths_pruned', sa.Integer(), nullable=True),
        sa.Column('model_provider', sa.String(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Path nodes table
    op.create_table('path_nodes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('depth', sa.Integer(), nullable=False),
        sa.Column('hypothesis', sa.Text(), nullable=False),
        sa.Column('evaluation_score', sa.Float(), nullable=True),
        sa.Column('is_pruned', sa.Boolean(), nullable=True),
        sa.Column('pruning_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['path_analyses.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['path_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Logic graphs table
    op.create_table('logic_graphs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reasoning_trace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('graph_structure', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('has_contradictions', sa.Boolean(), nullable=True),
        sa.Column('has_logic_gaps', sa.Boolean(), nullable=True),
        sa.Column('has_hidden_premises', sa.Boolean(), nullable=True),
        sa.Column('has_circularity', sa.Boolean(), nullable=True),
        sa.Column('contradictions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('logic_gaps', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('hidden_premises', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('circular_references', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('overall_validity_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['reasoning_trace_id'], ['reasoning_traces.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Logic nodes table
    op.create_table('logic_nodes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('graph_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('node_type', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('truth_value', sa.Boolean(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['graph_id'], ['logic_graphs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Logic edges table
    op.create_table('logic_edges',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('graph_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('edge_type', sa.String(), nullable=False),
        sa.Column('strength', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['graph_id'], ['logic_graphs.id'], ),
        sa.ForeignKeyConstraint(['source_node_id'], ['logic_nodes.id'], ),
        sa.ForeignKeyConstraint(['target_node_id'], ['logic_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Consistency checks table
    op.create_table('consistency_checks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_query', sa.Text(), nullable=False),
        sa.Column('query_variations', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('responses', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('convergence_rate', sa.Float(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('divergent_points', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_runs', sa.Integer(), nullable=False),
        sa.Column('model_provider', sa.String(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Audit reports table
    op.create_table('audit_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_type', sa.String(), nullable=False),
        sa.Column('format', sa.String(), nullable=False),
        sa.Column('reasoning_trace_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('path_analysis_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('logic_graph_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('consistency_check_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('report_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('audit_reports')
    op.drop_table('consistency_checks')
    op.drop_table('logic_edges')
    op.drop_table('logic_nodes')
    op.drop_table('logic_graphs')
    op.drop_table('path_nodes')
    op.drop_table('path_analyses')
    op.drop_table('reasoning_steps')
    op.drop_table('reasoning_traces')
    op.drop_index(op.f('ix_users_clerk_user_id'), table_name='users')
    op.drop_table('users')
