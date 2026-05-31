"""Add Gemini insights fields to analysis_results

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add Gemini-enhanced insights fields to analysis_results table
    op.add_column('analysis_results', sa.Column('candidate_summary', sa.Text(), nullable=False, server_default=''))
    op.add_column('analysis_results', sa.Column('hiring_recommendation', sa.String(length=50), nullable=False, server_default='Consider'))
    op.add_column('analysis_results', sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0'))
    op.add_column('analysis_results', sa.Column('strengths', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('analysis_results', sa.Column('weaknesses', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('analysis_results', sa.Column('recommendations', sa.JSON(), nullable=False, server_default='[]'))
    op.add_column('analysis_results', sa.Column('ai_provider', sa.String(length=50), nullable=True))
    op.add_column('analysis_results', sa.Column('ai_model', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('analysis_results', 'ai_model')
    op.drop_column('analysis_results', 'ai_provider')
    op.drop_column('analysis_results', 'recommendations')
    op.drop_column('analysis_results', 'weaknesses')
    op.drop_column('analysis_results', 'strengths')
    op.drop_column('analysis_results', 'confidence_score')
    op.drop_column('analysis_results', 'hiring_recommendation')
    op.drop_column('analysis_results', 'candidate_summary')