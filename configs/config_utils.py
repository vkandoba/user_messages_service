import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from enum import Enum
import yaml


class Period(str, Enum):
    CALENDAR_DAY = "calendar_day"
    DAY = "24h"


def get_period_from(period: Period, period_to: datetime) -> datetime:
    if period == Period.CALENDAR_DAY:
        return datetime.combine(period_to.date(), datetime.min.time(), tzinfo=timezone.utc)
    elif period == Period.DAY:
        return period_to - timedelta(hours=24)
    else:
        logging.error(f"The within option {period} not implemented")
        raise ValueError(f"Unsupported within period: {period}")


def load_yaml_config(file_path):
    config_file = Path(__file__).parent.parent / file_path
    config_content = config_file.read_text()
    return yaml.safe_load(config_content)