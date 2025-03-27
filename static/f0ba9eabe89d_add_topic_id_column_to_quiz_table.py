from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f0ba9eabe89d'
down_revision = '<previous_migration_id>'  # Replace with actual previous migration ID
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('quiz', schema=None) as batch_op:
        batch_op.add_column(sa.Column('topic_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_quiz_topic',  # Explicit constraint name
            'topic',  # Reference table
            ['topic_id'],  # Local column
            ['id']  # Remote column
        )

def downgrade():
    with op.batch_alter_table('quiz', schema=None) as batch_op:
        batch_op.drop_constraint('fk_quiz_topic', type_='foreignkey')
        batch_op.drop_column('topic_id')
