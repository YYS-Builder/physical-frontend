"""add analytics models

Revision ID: add_analytics_models
Revises: previous_revision
Create Date: 2024-03-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_analytics_models'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Create reading_sessions table
    op.create_table(
        'reading_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Float(), nullable=False),
        sa.Column('pages_read', sa.Integer(), nullable=False),
        sa.Column('reading_speed_pages_per_hour', sa.Float(), nullable=False),
        sa.Column('completion_percentage', sa.Float(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reading_sessions_id'), 'reading_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_reading_sessions_user_id'), 'reading_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_reading_sessions_document_id'), 'reading_sessions', ['document_id'], unique=False)

    # Create reading_goals table
    op.create_table(
        'reading_goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('daily_target', sa.Integer(), nullable=False),
        sa.Column('daily_current', sa.Integer(), nullable=False),
        sa.Column('weekly_target', sa.Integer(), nullable=False),
        sa.Column('weekly_current', sa.Integer(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_reading_goals_id'), 'reading_goals', ['id'], unique=False)
    op.create_index(op.f('ix_reading_goals_user_id'), 'reading_goals', ['user_id'], unique=True)

    # Create reading_stats table
    op.create_table(
        'reading_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('total_reading_time', sa.Float(), nullable=False),
        sa.Column('documents_read', sa.Integer(), nullable=False),
        sa.Column('average_speed', sa.Float(), nullable=False),
        sa.Column('streak_days', sa.Integer(), nullable=False),
        sa.Column('completion_rate', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reading_stats_id'), 'reading_stats', ['id'], unique=False)
    op.create_index(op.f('ix_reading_stats_user_id'), 'reading_stats', ['user_id'], unique=False)
    op.create_index(op.f('ix_reading_stats_date'), 'reading_stats', ['date'], unique=False)

    # Add analytics columns to documents table
    op.add_column('documents', sa.Column('last_read', sa.DateTime(), nullable=True))
    op.add_column('documents', sa.Column('average_reading_speed', sa.Float(), nullable=True))
    op.add_column('documents', sa.Column('completion_percentage', sa.Float(), nullable=False, server_default='0.0'))

def downgrade():
    # Remove analytics columns from documents table
    op.drop_column('documents', 'completion_percentage')
    op.drop_column('documents', 'average_reading_speed')
    op.drop_column('documents', 'last_read')

    # Drop reading_stats table
    op.drop_index(op.f('ix_reading_stats_date'), table_name='reading_stats')
    op.drop_index(op.f('ix_reading_stats_user_id'), table_name='reading_stats')
    op.drop_index(op.f('ix_reading_stats_id'), table_name='reading_stats')
    op.drop_table('reading_stats')

    # Drop reading_goals table
    op.drop_index(op.f('ix_reading_goals_user_id'), table_name='reading_goals')
    op.drop_index(op.f('ix_reading_goals_id'), table_name='reading_goals')
    op.drop_table('reading_goals')

    # Drop reading_sessions table
    op.drop_index(op.f('ix_reading_sessions_document_id'), table_name='reading_sessions')
    op.drop_index(op.f('ix_reading_sessions_user_id'), table_name='reading_sessions')
    op.drop_index(op.f('ix_reading_sessions_id'), table_name='reading_sessions')
    op.drop_table('reading_sessions') 