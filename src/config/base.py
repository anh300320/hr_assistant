import json
import logging
import os.path
from dataclasses import dataclass
from typing import Any


_logger = logging.getLogger(__name__)


@dataclass
class Config:
    telegram_bot_token: str
    google_drive_folder: str

    def get(self, key: str, default_value: Any):
        try:
            value = self.__getattribute__(key)
            if value:
                return value
        except Exception:
            if not default_value:
                _logger.exception("Failed to get config attr %s", key)
                raise
        return default_value


class ConfigLoader:
    def __init__(self):
        self._main_config_fp = os.path.join("resources", "main.conf")

    def load(self):
        with open(self._main_config_fp, "r") as fd:
            config = json.load(fd)
        return Config(
            telegram_bot_token=config["telegram_bot_token"],
            google_drive_folder=config.get("google_drive_folder", ""),
        )
