from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db


router = APIRouter(prefix="/api/menu", tags=["menu"])

def get_item_or_404(db: Session, item_id: int) -> models.MenuItem:
    item = db.get(models.MenuItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item
@router.get("", response_model=list[schemas.MenuItemOut])

def list_menu(category: str | None = None, vegetarian: bool | None = None,
              include_unavailable: bool = False, db: Session = Depends(get_db)):
    stmt = select(models.MenuItem).order_by(models.MenuItem.id)
    if not include_unavailable:
        stmt = stmt.where(models.MenuItem.is_available.is_(True))
    if category:
        stmt = stmt.where(func.lower(models.MenuItem.category) == category.lower())
    if vegetarian is not None:
        stmt = stmt.where(models.MenuItem.is_vegetarian.is_(vegetarian))
    return db.scalars(stmt).all()

@router.get("/{item_id}", response_model=schemas.MenuItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    return get_item_or_404(db, item_id)

@router.post("", response_model=schemas.MenuItemOut, status_code=201)
def create_item(payload: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(models.MenuItem).where(models.MenuItem.name == payload.name))
    if exists:
        raise HTTPException(status_code=409, detail="A menu item with this name already exists")
    item = models.MenuItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)          # reload so item.id is filled in
    return item

@router.put("/{item_id}", response_model=schemas.MenuItemOut)
def update_item(item_id: int, payload: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_id)
    clash = db.scalar(select(models.MenuItem).where(
        models.MenuItem.name == payload.name, models.MenuItem.id != item_id))
    if clash:
        raise HTTPException(status_code=409, detail="Another menu item already uses this name")
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = get_item_or_404(db, item_id)
    db.delete(item)
    db.commit()
    return Response(status_code=204)