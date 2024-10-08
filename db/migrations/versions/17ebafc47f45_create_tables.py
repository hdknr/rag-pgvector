"""create tables

Revision ID: 17ebafc47f45
Revises: 
Create Date: 2024-10-08 16:09:27.361231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17ebafc47f45'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document',
    sa.Column('categories', sa.String(length=256), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False, comment='primary_key_field'),
    sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=False, comment='vector_field'),
    sa.Column('meta_data', sa.JSON(), nullable=False, comment='metadata_field'),
    sa.Column('text', sa.Text(), nullable=False, comment='text_field'),
    sa.PrimaryKeyConstraint('id'),
    schema='rag'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('document', schema='rag')
    # ### end Alembic commands ###
