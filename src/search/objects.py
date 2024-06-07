from dataclasses import dataclass, field
from typing import List


RawSearch = str


@dataclass
class SearchEntry:
    words: List[str] = field(default_factory=list)
