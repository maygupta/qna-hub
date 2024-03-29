"""Add title to lecture

Revision ID: 523be21c1439
Revises: 31c08f71a4da
Create Date: 2021-10-11 23:23:32.039258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '523be21c1439'
down_revision = '31c08f71a4da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lecture', sa.Column('title', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('lecture', 'title')
    # ### end Alembic commands ###
