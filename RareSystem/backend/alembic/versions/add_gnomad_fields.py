"""add gnomad and pathogenic fields

Revision ID: add_gnomad_fields
Revises: add_hpo_jobs_table
Create Date: 2026-06-05

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_gnomad_fields'
down_revision = 'add_hpo_jobs_table'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('variants', sa.Column('gnomad_popmax_af', sa.Float(), nullable=True))
    op.add_column('variants', sa.Column('gnomad_eas_af', sa.Float(), nullable=True))
    op.add_column('variants', sa.Column('gnomad_nhomalt', sa.Integer(), nullable=True))
    op.add_column('variants', sa.Column('pathogenic_rank', sa.String(50), nullable=True))
    op.add_column('variants', sa.Column('evidence_summary', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('variants', 'evidence_summary')
    op.drop_column('variants', 'pathogenic_rank')
    op.drop_column('variants', 'gnomad_nhomalt')
    op.drop_column('variants', 'gnomad_eas_af')
    op.drop_column('variants', 'gnomad_popmax_af')
