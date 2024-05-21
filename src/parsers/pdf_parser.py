import io
import logging
from typing import Union

from pypdf import PdfReader

from src.common.objects import LoadedFileType, FileType
from src.parsers.base import Parser


class PdfParser(Parser):
    file_types = [FileType.PDF]
    supported = LoadedFileType.IN_MEMORY

    def parse(self, data: Union[bytes, str]) -> str:
        file = data
        if isinstance(data, bytes):
            file = io.BytesIO(data)
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text
