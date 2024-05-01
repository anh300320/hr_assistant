from abc import ABC, abstractmethod
from typing import Optional

from src.common.objects import Metadata


class Vault(ABC):

    def __init__(self, config):
        self._vault_root: Optional[str] = None

    @abstractmethod
    def load_all_metadata(self) -> list[Metadata]:
        raise NotImplementedError

    @abstractmethod
    def load_content(
            self,
            metadata: Metadata
    ):
        raise NotImplementedError
