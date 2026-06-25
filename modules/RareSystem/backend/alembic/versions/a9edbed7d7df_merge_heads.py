"""merge heads

Revision ID: a9edbed7d7df
Revises: add_gnomad_fields, add_hpo_terms
Create Date: 2026-06-05 13:26:49.867751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9edbed7d7df'
down_revision: Union[str, Sequence[str], None] = ('add_gnomad_fields', 'add_hpo_terms')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
