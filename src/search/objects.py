from dataclasses import dataclass
from typing import List


RawSearch = str


@dataclass
class SearchEntry:
    words: List[str]
