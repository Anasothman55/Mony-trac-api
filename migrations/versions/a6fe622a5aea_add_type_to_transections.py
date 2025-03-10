"""add type to transections

Revision ID: a6fe622a5aea
Revises: f5e502112caf
Create Date: 2025-03-03 20:39:08.963706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a6fe622a5aea'
down_revision: Union[str, None] = 'f5e502112caf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('type', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.create_index(op.f('ix_transactions_type'), 'transactions', ['type'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transactions_type'), table_name='transactions')
    op.drop_column('transactions', 'type')
    # ### end Alembic commands ###
