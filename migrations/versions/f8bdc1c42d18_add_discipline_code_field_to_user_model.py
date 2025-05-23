"""Add discipline_code field to User model

Revision ID: f8bdc1c42d18
Revises: cb895f09df66
Create Date: 2025-05-03 15:32:54.995999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8bdc1c42d18'
down_revision = 'cb895f09df66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('discipline_code', sa.String(length=10), nullable=True))
        batch_op.create_foreign_key('fk_user_discipline_code', 'discipline_code', ['discipline_code'], ['code'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_discipline_code', type_='foreignkey')
        batch_op.drop_column('discipline_code')

    # ### end Alembic commands ###
