from fastapi import APIRouter, Depends
from app.security import require_admin
router = APIRouter(prefix="/api/admin", tags=["admin"])
@router.get("/me")
def me(user: str = Depends(require_admin)):
    """Used by the admin login form to check credentials."""
    return {"ok": True, "user": user}