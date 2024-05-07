from abc import ABC, abstractmethod
from typing import Union


class Parser(ABC):
    file_types = []

    @abstractmethod
    def parse(self, data: Union[bytes, str]) -> str:
        raise NotImplementedError
