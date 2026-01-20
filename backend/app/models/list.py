"""User list and list item models for shopping basket functionality."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .product import Product
    from .session import UserSession


class UserList(Base, TimestampMixin):
    """
    User shopping list model.

    Users can have multiple lists (e.g., "Current Project", "Wishlist").
    Lists are associated with sessions for anonymous access and can be
    synced across devices via QR codes.
    """

    __tablename__ = "user_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    list_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_sessions.id", ondelete="CASCADE"), nullable=False
    )

    # List metadata
    name: Mapped[str] = mapped_column(String(100), default="My List")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # QR code sharing
    share_code: Mapped[Optional[str]] = mapped_column(
        String(36), unique=True, nullable=True, index=True
    )

    # Relationships
    session: Mapped["UserSession"] = relationship("UserSession", back_populates="lists")
    items: Mapped[list["ListItem"]] = relationship(
        "ListItem", back_populates="user_list", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_user_lists_session", "session_id"),)

    def __repr__(self) -> str:
        return f"<UserList(id={self.id}, name='{self.name}', items={len(self.items)})>"

    @property
    def total_items(self) -> int:
        """Get total number of items (sum of quantities)."""
        return sum(item.quantity for item in self.items)

    @property
    def unique_items(self) -> int:
        """Get number of unique products in the list."""
        return len(self.items)


class ListItem(Base, TimestampMixin):
    """
    Individual item in a user's shopping list.

    Tracks which products are in a list with their quantities.
    """

    __tablename__ = "list_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    list_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_lists.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )

    # Item details
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Snapshot of price at time of adding (for analytics)
    price_at_add: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    user_list: Mapped["UserList"] = relationship("UserList", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="list_items")

    __table_args__ = (
        Index("ix_list_items_list", "list_id"),
        Index("ix_list_items_product", "product_id"),
        Index("ix_list_items_list_product", "list_id", "product_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<ListItem(list_id={self.list_id}, product_id={self.product_id}, qty={self.quantity})>"
