"""RAG system: context_items, chat_threads, chat_messages tables

Revision ID: a1b2c3d4e5f6
Revises: dd975554af04
Create Date: 2026-02-28 22:00:00.000000

IMPORTANT: Before running this migration, enable the pgvector extension:
    CREATE EXTENSION IF NOT EXISTS vector;
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'dd975554af04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create context_items, chat_threads, and chat_messages tables."""

    # ── context_items ──────────────────────────────────────────────────────
    op.create_table(
        'context_items',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(3072), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    # HNSW index using halfvec cast — required for >2000 dimensions (pgvector 0.7.0+).
    # The column stores full-precision vector(3072); the cast to halfvec is only for
    # the index, halving memory use with negligible recall loss.
    op.execute(
        "CREATE INDEX IF NOT EXISTS context_items_embedding_idx "
        "ON context_items USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )

    # ── chat_threads ───────────────────────────────────────────────────────
    op.create_table(
        'chat_threads',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── chat_messages ──────────────────────────────────────────────────────
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('thread_id', sa.BigInteger(), nullable=False),
        sa.Column('role', sa.String(length=16), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['thread_id'], ['chat_threads.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    # Composite index for fast chronological message lookups per thread
    op.create_index(
        'chat_messages_thread_id_created_idx',
        'chat_messages',
        ['thread_id', 'created_at'],
        unique=False,
    )


def downgrade() -> None:
    """Drop all RAG tables."""
    op.drop_index('chat_messages_thread_id_created_idx', table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_table('chat_threads')
    op.execute("DROP INDEX IF EXISTS context_items_embedding_idx")
    op.drop_table('context_items')
