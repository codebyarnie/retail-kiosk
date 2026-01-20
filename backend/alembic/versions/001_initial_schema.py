"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-01-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["categories.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)

    # Create products table
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("short_description", sa.String(length=500), nullable=True),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("specifications", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("embedding_updated_at", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_index("ix_products_is_active", "products", ["is_active"])
    op.create_index("ix_products_name_search", "products", ["name"])
    op.create_index("ix_products_active_featured", "products", ["is_active", "is_featured"])

    # Create product_categories junction table
    op.create_table(
        "product_categories",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("product_id", "category_id"),
    )
    op.create_index(
        "ix_product_categories_category", "product_categories", ["category_id"]
    )

    # Create user_sessions table
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("device_type", sa.String(length=50), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column(
            "last_active_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_sessions_session_id", "user_sessions", ["session_id"], unique=True)

    # Create user_lists table
    op.create_table(
        "user_lists",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("list_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False, server_default="My List"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("share_code", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["user_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_lists_list_id", "user_lists", ["list_id"], unique=True)
    op.create_index("ix_user_lists_share_code", "user_lists", ["share_code"], unique=True)
    op.create_index("ix_user_lists_session", "user_lists", ["session_id"])

    # Create list_items table
    op.create_table(
        "list_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("list_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("price_at_add", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["list_id"], ["user_lists.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_list_items_list", "list_items", ["list_id"])
    op.create_index("ix_list_items_product", "list_items", ["product_id"])
    op.create_index(
        "ix_list_items_list_product",
        "list_items",
        ["list_id", "product_id"],
        unique=True,
    )

    # Create analytics_events table
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column(
            "event_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("product_sku", sa.String(length=50), nullable=True),
        sa.Column("search_query", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"], ["user_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analytics_events_event_type", "analytics_events", ["event_type"])
    op.create_index("ix_analytics_events_event_timestamp", "analytics_events", ["event_timestamp"])
    op.create_index("ix_analytics_events_product_sku", "analytics_events", ["product_sku"])
    op.create_index(
        "ix_analytics_session_type",
        "analytics_events",
        ["session_id", "event_type"],
    )
    op.create_index(
        "ix_analytics_timestamp_type",
        "analytics_events",
        ["event_timestamp", "event_type"],
    )


def downgrade() -> None:
    op.drop_table("analytics_events")
    op.drop_table("list_items")
    op.drop_table("user_lists")
    op.drop_table("user_sessions")
    op.drop_table("product_categories")
    op.drop_table("products")
    op.drop_table("categories")
