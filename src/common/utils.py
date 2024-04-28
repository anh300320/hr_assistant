import logging

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