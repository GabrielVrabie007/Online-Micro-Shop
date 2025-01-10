"""drop_profile_table

Revision ID: 46b162ea2e68
Revises: 6205b79f1828
Create Date: 2025-01-10 20:45:40.932873

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "46b162ea2e68"
down_revision: Union[str, None] = "6205b79f1828"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("profiles")
    pass


def downgrade() -> None:
    pass
