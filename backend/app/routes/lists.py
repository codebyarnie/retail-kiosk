"""User list (shopping basket) API routes."""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.list import (
    ListItemCreate,
    ListItemResponse,
    ListItemUpdate,
    ListSyncResponse,
    UserListCreate,
    UserListDetailResponse,
    UserListResponse,
    UserListUpdate,
)
from app.schemas.product import ProductResponse
from app.services.list_service import ListService
from app.services.session_service import SessionService

router = APIRouter(prefix="/lists")


async def get_or_create_session(
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    db: AsyncSession = Depends(get_db),
) -> int:
    """Get or create user session, returning the database ID."""
    session_service = SessionService(db)
    session = await session_service.get_or_create_session(session_id)

    # Set cookie if new session
    if not session_id or session_id != session.session_id:
        response.set_cookie(
            key="session_id",
            value=session.session_id,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            samesite="lax",
        )

    return session.id


@router.get("", response_model=list[UserListResponse])
async def get_my_lists(
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    db: AsyncSession = Depends(get_db),
) -> list[UserListResponse]:
    """Get all lists for the current session."""
    db_session_id = await get_or_create_session(response, session_id, db)
    service = ListService(db)
    lists = await service.get_lists_for_session(db_session_id)

    return [
        UserListResponse(
            id=lst.id,
            list_id=lst.list_id,
            name=lst.name,
            description=lst.description,
            share_code=lst.share_code,
            total_items=lst.total_items,
            unique_items=lst.unique_items,
            created_at=lst.created_at,
            updated_at=lst.updated_at,
        )
        for lst in lists
    ]


@router.post("", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    list_data: UserListCreate,
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    db: AsyncSession = Depends(get_db),
) -> UserListResponse:
    """Create a new shopping list."""
    db_session_id = await get_or_create_session(response, session_id, db)
    service = ListService(db)
    user_list = await service.create_list(db_session_id, list_data)

    return UserListResponse(
        id=user_list.id,
        list_id=user_list.list_id,
        name=user_list.name,
        description=user_list.description,
        share_code=user_list.share_code,
        total_items=0,
        unique_items=0,
        created_at=user_list.created_at,
        updated_at=user_list.updated_at,
    )


@router.get("/{list_id}", response_model=UserListDetailResponse)
async def get_list(
    list_id: str,
    db: AsyncSession = Depends(get_db),
) -> UserListDetailResponse:
    """Get a list with all its items."""
    service = ListService(db)
    user_list = await service.get_list_by_id(list_id)

    if not user_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List '{list_id}' not found",
        )

    items = [
        ListItemResponse(
            id=item.id,
            quantity=item.quantity,
            notes=item.notes,
            price_at_add=item.price_at_add,
            product=ProductResponse.model_validate(item.product),
            created_at=item.created_at,
        )
        for item in user_list.items
    ]

    return UserListDetailResponse(
        id=user_list.id,
        list_id=user_list.list_id,
        name=user_list.name,
        description=user_list.description,
        share_code=user_list.share_code,
        total_items=user_list.total_items,
        unique_items=user_list.unique_items,
        created_at=user_list.created_at,
        updated_at=user_list.updated_at,
        items=items,
    )


@router.patch("/{list_id}", response_model=UserListResponse)
async def update_list(
    list_id: str,
    list_data: UserListUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserListResponse:
    """Update a list's name or description."""
    service = ListService(db)
    user_list = await service.update_list(list_id, list_data)

    if not user_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List '{list_id}' not found",
        )

    return UserListResponse(
        id=user_list.id,
        list_id=user_list.list_id,
        name=user_list.name,
        description=user_list.description,
        share_code=user_list.share_code,
        total_items=user_list.total_items,
        unique_items=user_list.unique_items,
        created_at=user_list.created_at,
        updated_at=user_list.updated_at,
    )


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a shopping list."""
    service = ListService(db)
    deleted = await service.delete_list(list_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List '{list_id}' not found",
        )


@router.post("/{list_id}/items", response_model=ListItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item_to_list(
    list_id: str,
    item_data: ListItemCreate,
    db: AsyncSession = Depends(get_db),
) -> ListItemResponse:
    """Add an item to a list."""
    service = ListService(db)
    item = await service.add_item(list_id, item_data)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List or product not found",
        )

    return ListItemResponse(
        id=item.id,
        quantity=item.quantity,
        notes=item.notes,
        price_at_add=item.price_at_add,
        product=ProductResponse.model_validate(item.product),
        created_at=item.created_at,
    )


@router.patch("/{list_id}/items/{sku}", response_model=ListItemResponse)
async def update_list_item(
    list_id: str,
    sku: str,
    item_data: ListItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> ListItemResponse:
    """Update an item's quantity or notes."""
    service = ListService(db)
    item = await service.update_item(list_id, sku, item_data)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List or item not found",
        )

    return ListItemResponse(
        id=item.id,
        quantity=item.quantity,
        notes=item.notes,
        price_at_add=item.price_at_add,
        product=ProductResponse.model_validate(item.product),
        created_at=item.created_at,
    )


@router.delete("/{list_id}/items/{sku}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_list(
    list_id: str,
    sku: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove an item from a list."""
    service = ListService(db)
    removed = await service.remove_item(list_id, sku)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List or item not found",
        )


@router.post("/{list_id}/share", response_model=ListSyncResponse)
async def generate_share_code(
    list_id: str,
    db: AsyncSession = Depends(get_db),
) -> ListSyncResponse:
    """Generate a share code for QR sync."""
    service = ListService(db)
    share_code = await service.generate_share_code(list_id)

    if not share_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"List '{list_id}' not found",
        )

    return ListSyncResponse(
        list_id=list_id,
        share_code=share_code,
        sync_url=f"/api/lists/sync/{share_code}",
    )


@router.post("/sync/{share_code}", response_model=UserListDetailResponse)
async def sync_list_from_code(
    share_code: str,
    response: Response,
    session_id: str | None = Cookie(default=None, alias="session_id"),
    db: AsyncSession = Depends(get_db),
) -> UserListDetailResponse:
    """Sync a list from a share code (QR scan)."""
    db_session_id = await get_or_create_session(response, session_id, db)
    service = ListService(db)

    # Clone the list to the new session
    user_list = await service.clone_list_to_session(share_code, db_session_id)

    if not user_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No list found with share code '{share_code}'",
        )

    # Get the full list with items
    user_list = await service.get_list_by_id(user_list.list_id)

    items = [
        ListItemResponse(
            id=item.id,
            quantity=item.quantity,
            notes=item.notes,
            price_at_add=item.price_at_add,
            product=ProductResponse.model_validate(item.product),
            created_at=item.created_at,
        )
        for item in user_list.items
    ]

    return UserListDetailResponse(
        id=user_list.id,
        list_id=user_list.list_id,
        name=user_list.name,
        description=user_list.description,
        share_code=user_list.share_code,
        total_items=user_list.total_items,
        unique_items=user_list.unique_items,
        created_at=user_list.created_at,
        updated_at=user_list.updated_at,
        items=items,
    )
