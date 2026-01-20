"""Factory functions for creating test model instances.

This module provides factory functions that create model instances with
sensible defaults. Each factory function accepts **kwargs to override
any default values.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.analytics import AnalyticsEvent, EventType
from app.models.list import ListItem, UserList
from app.models.product import Category, Product, ProductCategory
from app.models.session import UserSession


def create_product(**kwargs: Any) -> Product:
    """Create a Product model instance with sensible defaults.

    Args:
        **kwargs: Override any default product attributes

    Returns:
        Product: A Product model instance (not persisted to database)

    Example:
        >>> product = create_product(name="Custom Name", price=29.99)
        >>> product.name
        'Custom Name'
        >>> product.price
        29.99
    """
    defaults: dict[str, Any] = {
        "sku": f"SKU-{uuid.uuid4().hex[:8].upper()}",
        "name": "Test Product",
        "description": "A test product for unit testing purposes",
        "short_description": "Test product",
        "price": 19.99,
        "image_url": "https://example.com/images/product.jpg",
        "thumbnail_url": "https://example.com/images/product-thumb.jpg",
        "attributes": {"material": "steel", "color": "silver"},
        "specifications": {"weight": "100g", "dimensions": "10x5x3cm"},
        "is_active": True,
        "is_featured": False,
        "embedding_updated_at": None,
    }
    defaults.update(kwargs)
    return Product(**defaults)


def create_category(**kwargs: Any) -> Category:
    """Create a Category model instance with sensible defaults.

    Args:
        **kwargs: Override any default category attributes

    Returns:
        Category: A Category model instance (not persisted to database)

    Example:
        >>> category = create_category(name="Power Tools", slug="power-tools")
        >>> category.slug
        'power-tools'
    """
    unique_slug = f"test-category-{uuid.uuid4().hex[:8]}"
    defaults: dict[str, Any] = {
        "name": "Test Category",
        "slug": unique_slug,
        "description": "A test category for unit testing",
        "image_url": "https://example.com/images/category.jpg",
        "display_order": 0,
        "is_active": True,
        "parent_id": None,
    }
    defaults.update(kwargs)
    return Category(**defaults)


def create_session(**kwargs: Any) -> UserSession:
    """Create a UserSession model instance with sensible defaults.

    Args:
        **kwargs: Override any default session attributes

    Returns:
        UserSession: A UserSession model instance (not persisted to database)

    Example:
        >>> session = create_session(device_type="mobile")
        >>> session.device_type
        'mobile'
    """
    defaults: dict[str, Any] = {
        "session_id": str(uuid.uuid4()),
        "device_type": "kiosk",
        "user_agent": "TestBrowser/1.0",
        "ip_address": "192.168.1.100",
        "last_active_at": datetime.now(timezone.utc),
        "expires_at": None,
    }
    defaults.update(kwargs)
    return UserSession(**defaults)


def create_user_list(session_id: int, **kwargs: Any) -> UserList:
    """Create a UserList model instance with sensible defaults.

    The session_id is required because lists must belong to a session.

    Args:
        session_id: The ID of the session this list belongs to
        **kwargs: Override any default list attributes

    Returns:
        UserList: A UserList model instance (not persisted to database)

    Example:
        >>> user_list = create_user_list(session_id=1, name="My Project List")
        >>> user_list.name
        'My Project List'
    """
    defaults: dict[str, Any] = {
        "session_id": session_id,
        "list_id": str(uuid.uuid4()),
        "name": "My Shopping List",
        "description": "A test shopping list",
        "share_code": None,
    }
    defaults.update(kwargs)
    return UserList(**defaults)


def create_list_item(list_id: int, product_id: int, **kwargs: Any) -> ListItem:
    """Create a ListItem model instance with sensible defaults.

    The list_id and product_id are required because items must belong
    to a list and reference a product.

    Args:
        list_id: The ID of the list this item belongs to
        product_id: The ID of the product this item references
        **kwargs: Override any default item attributes

    Returns:
        ListItem: A ListItem model instance (not persisted to database)

    Example:
        >>> item = create_list_item(list_id=1, product_id=1, quantity=3)
        >>> item.quantity
        3
    """
    defaults: dict[str, Any] = {
        "list_id": list_id,
        "product_id": product_id,
        "quantity": 1,
        "notes": None,
        "price_at_add": None,
    }
    defaults.update(kwargs)
    return ListItem(**defaults)


def create_analytics_event(session_id: int, **kwargs: Any) -> AnalyticsEvent:
    """Create an AnalyticsEvent model instance with sensible defaults.

    The session_id is required because events must belong to a session.

    Args:
        session_id: The ID of the session this event belongs to
        **kwargs: Override any default event attributes

    Returns:
        AnalyticsEvent: An AnalyticsEvent model instance (not persisted to database)

    Example:
        >>> event = create_analytics_event(
        ...     session_id=1,
        ...     event_type=EventType.VIEW_PRODUCT,
        ...     product_sku="ABC-123"
        ... )
        >>> event.event_type
        'view_product'
    """
    defaults: dict[str, Any] = {
        "session_id": session_id,
        "event_type": EventType.VIEW_PRODUCT.value,
        "event_data": {"source": "test"},
        "product_sku": None,
        "search_query": None,
    }
    defaults.update(kwargs)
    return AnalyticsEvent(**defaults)


def create_product_category(product_id: int, category_id: int) -> ProductCategory:
    """Create a ProductCategory association model instance.

    This creates a many-to-many relationship between a product and category.

    Args:
        product_id: The ID of the product
        category_id: The ID of the category

    Returns:
        ProductCategory: A ProductCategory model instance (not persisted to database)

    Example:
        >>> assoc = create_product_category(product_id=1, category_id=2)
        >>> assoc.product_id
        1
    """
    return ProductCategory(product_id=product_id, category_id=category_id)


# ============================================================================
# Async Helper Functions for Database Persistence
# ============================================================================


async def create_product_in_db(session, **kwargs: Any) -> Product:
    """Create and persist a Product to the database.

    Args:
        session: The async database session
        **kwargs: Override any default product attributes

    Returns:
        Product: The persisted Product instance with ID
    """
    product = create_product(**kwargs)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def create_category_in_db(session, **kwargs: Any) -> Category:
    """Create and persist a Category to the database.

    Args:
        session: The async database session
        **kwargs: Override any default category attributes

    Returns:
        Category: The persisted Category instance with ID
    """
    category = create_category(**kwargs)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def create_session_in_db(session, **kwargs: Any) -> UserSession:
    """Create and persist a UserSession to the database.

    Args:
        session: The async database session
        **kwargs: Override any default session attributes

    Returns:
        UserSession: The persisted UserSession instance with ID
    """
    user_session = create_session(**kwargs)
    session.add(user_session)
    await session.commit()
    await session.refresh(user_session)
    return user_session


async def create_user_list_in_db(session, session_id: int, **kwargs: Any) -> UserList:
    """Create and persist a UserList to the database.

    Args:
        session: The async database session
        session_id: The ID of the session this list belongs to
        **kwargs: Override any default list attributes

    Returns:
        UserList: The persisted UserList instance with ID
    """
    user_list = create_user_list(session_id=session_id, **kwargs)
    session.add(user_list)
    await session.commit()
    await session.refresh(user_list)
    return user_list


async def create_list_item_in_db(
    session, list_id: int, product_id: int, **kwargs: Any
) -> ListItem:
    """Create and persist a ListItem to the database.

    Args:
        session: The async database session
        list_id: The ID of the list this item belongs to
        product_id: The ID of the product this item references
        **kwargs: Override any default item attributes

    Returns:
        ListItem: The persisted ListItem instance with ID
    """
    item = create_list_item(list_id=list_id, product_id=product_id, **kwargs)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def create_analytics_event_in_db(session, session_id: int, **kwargs: Any) -> AnalyticsEvent:
    """Create and persist an AnalyticsEvent to the database.

    Args:
        session: The async database session
        session_id: The ID of the session this event belongs to
        **kwargs: Override any default event attributes

    Returns:
        AnalyticsEvent: The persisted AnalyticsEvent instance with ID
    """
    event = create_analytics_event(session_id=session_id, **kwargs)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event
