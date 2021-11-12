"""empty message

Revision ID: 06b66d485db9
Revises: 222ca5b8a33d
Create Date: 2021-11-11 13:31:52.459969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06b66d485db9'
down_revision = '222ca5b8a33d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rental', sa.Column('due_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rental', 'due_date')
    # ### end Alembic commands ###
