"""Rename name column to username

Revision ID: 97ec88cc3845
Revises: 98dc59858e1e
Create Date: 2025-08-26 12:41:04.716297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97ec88cc3845'
down_revision: Union[str, Sequence[str], None] = '98dc59858e1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('users', 'name', new_column_name='username')

def downgrade():
    op.alter_column('users', 'username', new_column_name='name')
