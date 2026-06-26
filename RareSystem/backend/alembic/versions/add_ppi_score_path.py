"""add ppi_score_path to vep_jobs

Revision ID: add_ppi_score_path
Revises:
Create Date: 2026-06-25
"""
from alembic import op
import sqlalchemy as sa


revision: str = 'add_ppi_score_path'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vep_jobs', sa.Column('ppi_score_path', sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('vep_jobs', 'ppi_score_path')
