"""List service for shopping list management."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import ListItem, Product, UserList, UserSession
from app.schemas.list import ListItemCreate, ListItemUpdate, UserListCreate, UserListUpdate


class ListService:
    """Service for shopping list business logic."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the list service."""
        self.db = db

    async def get_list_by_id(self, list_id: str) -> Optional[UserList]:
        """Get list by list_id string."""
        result = await self.db.execute(
            select(UserList)
            .options(selectinload(UserList.items).selectinload(ListItem.product))
            .where(UserList.list_id == list_id)
        )
        return result.scalar_one_or_none()

    async def get_list_by_share_code(self, share_code: str) -> Optional[UserList]:
        """Get list by share code for QR sync."""
        result = await self.db.execute(
            select(UserList)
            .options(selectinload(UserList.items).selectinload(ListItem.product))
            .where(UserList.share_code == share_code)
        )
        return result.scalar_one_or_none()

    async def get_lists_for_session(self, session_id: int) -> list[UserList]:
        """Get all lists for a session."""
        result = await self.db.execute(
            select(UserList)
            .options(selectinload(UserList.items))
            .where(UserList.session_id == session_id)
            .order_by(UserList.updated_at.desc())
        )
        return list(result.scalars().all())

    async def create_list(
        self, session_id: int, list_data: UserListCreate
    ) -> UserList:
        """Create a new shopping list for a session."""
        user_list = UserList(
            list_id=str(uuid.uuid4()),
            session_id=session_id,
            **list_data.model_dump(),
        )
        self.db.add(user_list)
        await self.db.commit()
        await self.db.refresh(user_list)
        return user_list

    async def update_list(
        self, list_id: str, list_data: UserListUpdate
    ) -> Optional[UserList]:
        """Update a shopping list."""
        user_list = await self.get_list_by_id(list_id)
        if not user_list:
            return None

        update_data = list_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user_list, field, value)

        await self.db.commit()
        await self.db.refresh(user_list)
        return user_list

    async def delete_list(self, list_id: str) -> bool:
        """Delete a shopping list."""
        user_list = await self.get_list_by_id(list_id)
        if not user_list:
            return False

        await self.db.delete(user_list)
        await self.db.commit()
        return True

    async def add_item(
        self, list_id: str, item_data: ListItemCreate
    ) -> Optional[ListItem]:
        """Add an item to a list."""
        user_list = await self.get_list_by_id(list_id)
        if not user_list:
            return None

        # Get the product by SKU
        result = await self.db.execute(
            select(Product).where(Product.sku == item_data.product_sku)
        )
        product = result.scalar_one_or_none()
        if not product:
            return None

        # Check if item already exists in list
        existing_item = await self._get_list_item(user_list.id, product.id)
        if existing_item:
            # Update quantity instead
            existing_item.quantity += item_data.quantity
            if item_data.notes:
                existing_item.notes = item_data.notes
            await self.db.commit()
            await self.db.refresh(existing_item)
            return existing_item

        # Create new list item
        list_item = ListItem(
            list_id=user_list.id,
            product_id=product.id,
            quantity=item_data.quantity,
            notes=item_data.notes,
            price_at_add=product.price,
        )
        self.db.add(list_item)
        await self.db.commit()
        await self.db.refresh(list_item)

        # Load the product relationship
        result = await self.db.execute(
            select(ListItem)
            .options(selectinload(ListItem.product))
            .where(ListItem.id == list_item.id)
        )
        return result.scalar_one_or_none()

    async def update_item(
        self, list_id: str, product_sku: str, item_data: ListItemUpdate
    ) -> Optional[ListItem]:
        """Update an item in a list."""
        user_list = await self.get_list_by_id(list_id)
        if not user_list:
            return None

        # Get the product by SKU
        result = await self.db.execute(
            select(Product).where(Product.sku == product_sku)
        )
        product = result.scalar_one_or_none()
        if not product:
            return None

        # Get the list item
        list_item = await self._get_list_item(user_list.id, product.id)
        if not list_item:
            return None

        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(list_item, field, value)

        await self.db.commit()
        await self.db.refresh(list_item)
        return list_item

    async def remove_item(self, list_id: str, product_sku: str) -> bool:
        """Remove an item from a list."""
        user_list = await self.get_list_by_id(list_id)
        if not user_list:
            return False

        # Get the product by SKU
        result = await self.db.execute(
            select(Product).where(Product.sku == product_sku)
        )
        product = result.scalar_one_or_none()
        if not product:
            return False

        # Get the list item
        list_item = await self._get_list_item(user_list.id, product.id)
        if not list_item:
            return False

        await self.db.delete(list_item)
        await self.db.commit()
        return True

    async def _get_list_item(
        self, list_db_id: int, product_id: int
    ) -> Optional[ListItem]:
        """Get a list item by list database ID and product ID."""
        result = await self.db.execute(
            select(ListItem)
            .options(selectinload(ListItem.product))
            .where(ListItem.list_id == list_db_id, ListItem.product_id == product_id)
        )
        return result.scalar_one_or_none()

    async def generate_share_code(self, list_id: str) -> Optional[str]:
        """Generate a share code for QR sync."""
        user_list = await self.get_list_by_id(list_id)
        if not user_list:
            return None

        if not user_list.share_code:
            user_list.share_code = str(uuid.uuid4())[:8].upper()
            await self.db.commit()

        return user_list.share_code

    async def clone_list_to_session(
        self, share_code: str, new_session_id: int
    ) -> Optional[UserList]:
        """Clone a list to a new session (for QR sync)."""
        source_list = await self.get_list_by_share_code(share_code)
        if not source_list:
            return None

        # Create new list for the session
        new_list = UserList(
            list_id=str(uuid.uuid4()),
            session_id=new_session_id,
            name=source_list.name,
            description=source_list.description,
        )
        self.db.add(new_list)
        await self.db.flush()

        # Copy items
        for item in source_list.items:
            new_item = ListItem(
                list_id=new_list.id,
                product_id=item.product_id,
                quantity=item.quantity,
                notes=item.notes,
                price_at_add=item.price_at_add,
            )
            self.db.add(new_item)

        await self.db.commit()
        await self.db.refresh(new_list)
        return new_list
