"""initial schema"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(60)),
        sa.Column("resume_url", sa.Text(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_candidates_full_name", "candidates", ["full_name"])
    op.create_index("ix_candidates_email", "candidates", ["email"])
    op.create_table("skills", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), unique=True))
    op.create_index("ix_skills_name", "skills", ["name"])
    op.create_table("job_descriptions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("content", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table(
        "candidate_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE")),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE")),
    )
    op.create_table(
        "analysis_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), unique=True),
        sa.Column("matching_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("semantic_similarity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("keyword_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_table("analysis_results")
    op.drop_table("candidate_skills")
    op.drop_table("job_descriptions")
    op.drop_index("ix_skills_name", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_candidates_email", table_name="candidates")
    op.drop_index("ix_candidates_full_name", table_name="candidates")
    op.drop_table("candidates")

