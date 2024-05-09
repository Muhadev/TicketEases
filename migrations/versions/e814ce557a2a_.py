"""empty message

Revision ID: e814ce557a2a
Revises: 
Create Date: 2024-05-08 13:31:34.092245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e814ce557a2a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('time', sa.Time(), nullable=False))
    op.add_column('event', sa.Column('venue', sa.String(length=200), nullable=False))
    op.add_column('ticket', sa.Column('ticket_type_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'ticket', 'ticket_type', ['ticket_type_id'], ['id'], ondelete='CASCADE')
    op.drop_column('ticket', 'price')
    op.drop_column('ticket', 'ticket_type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ticket', sa.Column('ticket_type', mysql.VARCHAR(length=50), nullable=False))
    op.add_column('ticket', sa.Column('price', mysql.FLOAT(), nullable=False))
    op.drop_constraint(None, 'ticket', type_='foreignkey')
    op.drop_column('ticket', 'ticket_type_id')
    op.drop_column('event', 'venue')
    op.drop_column('event', 'time')
    # ### end Alembic commands ###
