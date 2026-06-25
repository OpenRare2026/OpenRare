"""change pathogenic_rank to integer

Revision ID: change_pathogenic_rank_int
Revises: 6b1564f017bb
Create Date: 2026-06-05

"""
from alembic import op
import sqlalchemy as sa


revision = 'change_pathogenic_rank_int'
down_revision = '6b1564f017bb'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('variants', 'pathogenic_rank')
    op.add_column('variants', sa.Column('pathogenic_rank', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('variants', 'pathogenic_rank')
    op.add_column('variants', sa.Column('pathogenic_rank', sa.String(50), nullable=True))
