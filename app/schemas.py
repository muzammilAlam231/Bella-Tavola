import datetime as dt
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from app import rules

class MenuItemBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    price: float = Field(gt=0, le=1000)
    category: str = Field(min_length=2, max_length=50)
    ingredients: str = Field(default="", max_length=500)
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_gluten_free: bool = False
    is_featured: bool = False
    is_available: bool = True
    @model_validator(mode="after")
    def vegan_implies_vegetarian(self):
        if self.is_vegan:
            self.is_vegetarian = True
        return self
class MenuItemCreate(MenuItemBase):
    pass
class MenuItemOut(MenuItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)   # allow building from SQLAlchemy objects


class ReservationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(pattern=r"^[0-9+\-\s()]{7,20}$")
    party_size: int = Field(ge=1, le=rules.MAX_PARTY_SIZE)
    reservation_date: dt.date
    reservation_time: dt.time
    special_requests: str | None = Field(default=None, max_length=300)
    @field_validator("name", mode="before")
    @classmethod
    def tidy_name(cls, v: str) -> str:
        return " ".join(v.split()) if isinstance(v, str) else v
    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()
    @model_validator(mode="after")
    def check_slot(self):
        t = self.reservation_time
        if t.minute not in (0, 30) or t.second != 0:
            raise ValueError("Please choose a time on the hour or half hour")
        if not (rules.OPEN_TIME <= t <= rules.LAST_SEATING):
            raise ValueError("We take bookings between 12:00 and 21:00")
        when = dt.datetime.combine(self.reservation_date, t)
        now = rules.now_local()
        if when < now + dt.timedelta(hours=rules.MIN_NOTICE_HOURS):
            raise ValueError("Bookings need at least 1 hour notice")
        if when > now + dt.timedelta(days=rules.MAX_DAYS_AHEAD):
            raise ValueError("We take bookings up to 60 days ahead")
        return self
class ReservationOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    party_size: int
    reservation_date: dt.date
    reservation_time: dt.time
    special_requests: str | None
    status: str
    created_at: dt.datetime
    model_config = ConfigDict(from_attributes=True)
class ReservationStatusUpdate(BaseModel):
    status: Literal["confirmed", "cancelled"]
