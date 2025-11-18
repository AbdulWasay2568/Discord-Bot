"""Initial models

Revision ID: 4ad0048c06d9
Revises: bb21b6c0e03b
Create Date: 2025-11-18 17:15:24.706443

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ad0048c06d9'
down_revision: Union[str, Sequence[str], None] = 'bb21b6c0e03b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
