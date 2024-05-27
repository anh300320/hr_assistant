import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

from src.common.objects import Metadata, LoadedFile, VaultType


class Vault(ABC):

    vault_type: VaultType

    def __init__(self, config):
        self._vault_root: Optional[str] = None

    @abstractmethod
    def load_all_metadata(self) -> list[Metadata]:
        raise NotImplementedError

    def load_content(
            self,
            metadata: Metadata
    ) -> LoadedFile:
        start_cp = time.perf_counter()
        result = self._load(metadata)
        finish_cp = time.perf_counter()
        logging.getLogger(__name__).debug(
            "Loaded content for metadata finished, elapsed time %s",
            finish_cp - start_cp
        )
        return result

    @abstractmethod
    def _load(
            self,
            metadata: Metadata
    ) -> LoadedFile:
        raise NotImplementedError
