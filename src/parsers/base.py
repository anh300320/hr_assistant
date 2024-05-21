from abc import ABC, abstractmethod
from typing import Union

from src.common.objects import LoadedFileType


class Parser(ABC):
    file_types: list[str] = []
    supported: LoadedFileType = LoadedFileType.ON_DISK

    @abstractmethod
    def parse(self, data: Union[bytes, str]) -> str:
        raise NotImplementedError
