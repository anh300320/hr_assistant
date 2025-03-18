import logging
from datetime import datetime, date
from typing import Any, List

import pytz

from src.common.exceptions import InternalException


def decode(data: bytes) -> str:
    encode_types = ['utf8']
    for e in encode_types:
        try:
            result = data.decode(e)
            return result
        except Exception as e:
            continue
    raise InternalException(
        "Failed to decode data"
    )


def datetime_str(dt: datetime) -> str:
    return dt.strftime('%Y%m%d %H%M%S')


def date_str(dt: date) -> str:
    return dt.strftime('%Y%m%d')


def get_current_utc() -> datetime:
    now = datetime.utcnow()
    utc = pytz.UTC
    return utc.localize(now)


def batch_gen(elements: List[Any], batch_size: int):
    batch = []
    for e in elements:
        batch.append(e)
        if len(batch) >= batch_size:
            yield batch
            batch = []
