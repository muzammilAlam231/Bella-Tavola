import datetime as dt
from zoneinfo import ZoneInfo
from app.config import settings
OPEN_TIME = dt.time(12, 0)
LAST_SEATING = dt.time(21, 0)
MAX_PARTY_SIZE = 12
SEATS_PER_SLOT = 40          # total guests we can seat at one time slot
MIN_NOTICE_HOURS = 1
MAX_DAYS_AHEAD = 60
def now_local() -> dt.datetime:
    """Current time at the restaurant (naive datetime, no tzinfo)."""
    return dt.datetime.now(ZoneInfo(settings.timezone)).replace(tzinfo=None)