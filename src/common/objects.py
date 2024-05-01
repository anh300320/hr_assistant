from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


@dataclass
class Token:
    text: str
    position: int


class FileType(Enum):
    PDF = 1
    DOC = 2
    IMAGE = 3


@dataclass
class Metadata:
    name: str
    vault_id: str
    file_type: Optional[FileType] = None    # TODO
    link: Optional[str] = None
    create_date: Optional[datetime] = None


@dataclass
class ParsedDocument:
    metadata: Metadata
    tokens: list[Token]


@dataclass
class Reference:
    metadata: Metadata
    position: int
