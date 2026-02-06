from datetime import datetime, timedelta
from enum import Enum


class Period(str, Enum):
    CALENDAR_DAY = "calendar_day"
    DAY = "24h"


def get_period_from(period: Period, period_to: datetime) -> datetime:
    if period == Period.CALENDAR_DAY:
        return datetime.combine(period_to.date(), datetime.min.time())
    elif period == Period.DAY:
        return period_to - timedelta(hours=24)
    else:
        raise ValueError("Unsupported period type")
