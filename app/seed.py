from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app import models
from app.data import SEED_MENU

def seed_menu(db: Session) -> None:
    """Insert the starter menu only when the table is empty."""
    count = db.scalar(select(func.count()).select_from(models.MenuItem))
    if count == 0:
        db.add_all([models.MenuItem(**row) for row in SEED_MENU])
        db.commit()