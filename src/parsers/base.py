from abc import ABC, abstractmethod
from typing import Union


class Parser(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def parse(self, data: Union[bytes, str]) -> str:
        raise NotImplementedError
