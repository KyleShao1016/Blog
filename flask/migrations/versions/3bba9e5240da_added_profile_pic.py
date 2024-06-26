"""Added Profile Pic

Revision ID: 3bba9e5240da
Revises: 3a11be4e6a25
Create Date: 2024-06-13 18:39:09.675475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bba9e5240da'
down_revision = '3a11be4e6a25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_pic', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('profile_pic')

    # ### end Alembic commands ###
