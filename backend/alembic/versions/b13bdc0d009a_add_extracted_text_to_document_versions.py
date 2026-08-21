"""add extracted text to document versions

Revision ID: b13bdc0d009a
Revises: 8293c85f2162
Create Date: 2026-08-21 12:29:15.552701

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b13bdc0d009a"
down_revision: str | Sequence[str] | None = "8293c85f2162"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "document_versions",
        sa.Column("extracted_text", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "document_versions",
        "extracted_text",
    )
