"""add survey_responses table

Revision ID: 20251226_add_survey_responses
Revises: 
Create Date: 2025-12-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251226_add_survey_responses"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "postgresql":
        json_type = postgresql.JSON()
    else:
        json_type = sa.Text()

    op.create_table(
        "survey_responses",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("survey_id", sa.Integer(), sa.ForeignKey("surveys.id"), nullable=False),
        sa.Column("respondent_id", sa.Integer(), nullable=True),
        sa.Column("respondent_name", sa.String(length=200), nullable=True),
        sa.Column("answers", json_type, nullable=False),
        sa.Column("submitted_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_survey_responses_survey_id", "survey_responses", ["survey_id"])


def downgrade() -> None:
    op.drop_index("ix_survey_responses_survey_id", table_name="survey_responses")
    op.drop_table("survey_responses")
