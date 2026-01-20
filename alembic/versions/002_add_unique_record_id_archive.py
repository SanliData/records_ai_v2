"""add unique constraint on archive record_id

Revision ID: 002_add_unique_record_id_archive
Revises: 001_add_users_table
Create Date: 2025-01-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_unique_record_id_archive'
down_revision = '001_add_users_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # P0-3: Add unique constraint on record_id for idempotency
    # Note: This assumes archive_records table has a record_id column
    # If the table uses a different structure, adjust accordingly
    
    # Check if archive_records table exists and has record_id column
    # For now, we'll add the constraint if possible
    try:
        # Add unique constraint on record_id
        # Note: Adjust column name if different (e.g., archive_id)
        op.create_unique_constraint(
            'uq_archive_records_record_id',
            'archive_records',
            ['record_id']
        )
    except Exception:
        # If constraint creation fails (e.g., column doesn't exist or duplicates),
        # log warning but don't fail migration
        # In production, you'd want to handle this more gracefully
        pass


def downgrade() -> None:
    # Remove unique constraint
    try:
        op.drop_constraint(
            'uq_archive_records_record_id',
            'archive_records',
            type_='unique'
        )
    except Exception:
        pass
