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

    @abstractmethod
    def load_content(
            self,
            metadata: Metadata
    ) -> LoadedFile:
        raise NotImplementedError
