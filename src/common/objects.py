import os.path
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Union


class VaultType(Enum):
    GOOGLE_DRIVE = 1
    LOCAL_DISK = 2


@dataclass
class Token:
    text: str
    position: int


class FileType(Enum):
    PDF = 1
    DOC = 2
    IMAGE = 3
    FOLDER = 4


@dataclass
class Metadata:
    name: str
    vault_id: str
    vault_type: VaultType
    file_type: Optional[FileType] = None    # TODO
    link: Optional[str] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None


@dataclass
class ParsedDocument:
    metadata: Metadata
    tokens: list[Token]


@dataclass
class Reference:
    metadata: Metadata
    position: int
    document_id: Optional[int] = None


class Index:
    def __init__(self):
        self.index: dict[str, list[Reference]] = defaultdict(list)

    def update(
            self,
            tokens: list[Token],
            metadata: Metadata,
    ):
        for token in tokens:
            self.index[token.text].append(
                Reference(
                    metadata,
                    position=token.position
                )
            )


class LoadedFileType(Enum):
    ON_DISK = 1
    IN_MEMORY = 2


class LoadedFile:
    def __init__(
            self,
            loaded_type: LoadedFileType,
            content: Union[str, bytes],
    ):
        self._loaded_type = loaded_type
        self._content = content

    def __enter__(self):
        return self._content

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._loaded_type == LoadedFileType.ON_DISK:
            if os.path.exists(self._content):
                os.remove(self._content)
        return False
