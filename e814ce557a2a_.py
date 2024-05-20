from alembic import op
import sqlalchemy as sa

def upgrade():
    # Check if the 'time' column already exists in the 'events' table
    connection = op.get_bind()
    result = connection.execute("SHOW COLUMNS FROM events LIKE 'time'")
    column_exists = result.fetchone() is not None

    if not column_exists:
        # Add the 'time' column only if it doesn't exist
        op.add_column('events', sa.Column('time', sa.Time(), nullable=False))

def downgrade():
    op.drop_column('events', 'time')
