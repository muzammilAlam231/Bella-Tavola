from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app import models, rules, schemas
from app.database import get_db
router = APIRouter(prefix="/api/reservations", tags=["reservations"])
@router.post("", response_model=schemas.ReservationOut, status_code=201)
def create_reservation(payload: schemas.ReservationCreate, db: Session = Depends(get_db)):
    R = models.Reservation
    active = R.status != "cancelled"
    duplicate = db.scalar(select(R).where(
        R.email == payload.email, R.reservation_date == payload.reservation_date,
        R.reservation_time == payload.reservation_time, active))
    if duplicate:
        raise HTTPException(409, "You already have a booking for that date and time.")
    seats_taken = db.scalar(select(func.coalesce(func.sum(R.party_size), 0)).where(
        R.reservation_date == payload.reservation_date,
        R.reservation_time == payload.reservation_time, active))
    if seats_taken + payload.party_size > rules.SEATS_PER_SLOT:
        raise HTTPException(409, "Sorry, that time is fully booked. Please choose another time.")
    reservation = R(**payload.model_dump())
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation
# --- management endpoints (we lock these behind admin login on Day 6) --
@router.get("", response_model=list[schemas.ReservationOut])
def list_reservations(status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(models.Reservation).order_by(
        models.Reservation.reservation_date, models.Reservation.reservation_time)
    if status:
        stmt = stmt.where(models.Reservation.status == status)
    return db.scalars(stmt).all()
@router.patch("/{reservation_id}/status", response_model=schemas.ReservationOut)
def update_status(reservation_id: int, payload: schemas.ReservationStatusUpdate,
                  db: Session = Depends(get_db)):
    reservation = db.get(models.Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(404, "Reservation not found")
    reservation.status = payload.status
    db.commit()
    db.refresh(reservation)
    return reservation
@router.delete("/{reservation_id}", status_code=204)
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.get(models.Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(404, "Reservation not found")
    db.delete(reservation)
    db.commit()