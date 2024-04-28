from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Metadata:
    name: str
    internal_id: str
    link: Optional[str] = None
    create_date: Optional[datetime] = None


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
