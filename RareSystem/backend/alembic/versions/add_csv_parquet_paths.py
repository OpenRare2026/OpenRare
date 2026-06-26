"""add csv_path parquet_path to vep_jobs

Revision ID: add_csv_parquet_paths
Revises: a9edbed7d7df
Create Date: 2026-06-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'add_csv_parquet_paths'
down_revision: Union[str, Sequence[str], None] = 'a9edbed7d7df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vep_jobs', sa.Column('csv_path', sa.String(length=500), nullable=True))
    op.add_column('vep_jobs', sa.Column('parquet_path', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('vep_jobs', 'parquet_path')
    op.drop_column('vep_jobs', 'csv_path')
