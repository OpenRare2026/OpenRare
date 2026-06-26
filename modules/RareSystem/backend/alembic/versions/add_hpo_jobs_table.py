"""add hpo_jobs table

Revision ID: add_hpo_jobs_table
Revises: 06d2aca48886
Create Date: 2026-06-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'add_hpo_jobs_table'
down_revision: Union[str, Sequence[str], None] = '06d2aca48886'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('hpo_jobs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('job_id', sa.String(length=100), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('clinical_note', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('results', sa.JSON(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name=op.f('fk_hpo_jobs_patient_id_patients')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_hpo_jobs'))
    )
    op.create_index(op.f('ix_hpo_jobs_id'), 'hpo_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_hpo_jobs_job_id'), 'hpo_jobs', ['job_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_hpo_jobs_job_id'), table_name='hpo_jobs')
    op.drop_index(op.f('ix_hpo_jobs_id'), table_name='hpo_jobs')
    op.drop_table('hpo_jobs')
