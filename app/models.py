import datetime as dt
from sqlalchemy import Boolean, Date, DateTime, Float, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String(50), index=True)
    ingredients: Mapped[str] = mapped_column(Text, default="")
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vegan: Mapped[bool] = mapped_column(Boolean, default=False)
    is_gluten_free: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    
class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), index=True)
    phone: Mapped[str] = mapped_column(String(20))
    party_size: Mapped[int]
    reservation_date: Mapped[dt.date] = mapped_column(Date, index=True)
    reservation_time: Mapped[dt.time] = mapped_column(Time)
    special_requests: Mapped[str | None] = mapped_column(String(300), default=None)
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, server_default=func.now())