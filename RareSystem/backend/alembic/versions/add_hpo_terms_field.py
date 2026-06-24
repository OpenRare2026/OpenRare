"""add hpo_terms to patient

Revision ID: add_hpo_terms
Revises: 6b1564f017bb
Create Date: 2026-06-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'add_hpo_terms'
down_revision: Union[str, Sequence[str], None] = '6b1564f017bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('patients', sa.Column('hpo_terms', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('patients', 'hpo_terms')
