from typing import Union

import textract

from src.common.objects import FileType
from src.common.utils import decode
from src.parsers.base import Parser


class DocParser(Parser):

    file_types = [FileType.DOC]

    def parse(self, data: Union[bytes, str]) -> str:
        text: bytes = textract.process(data)
        return decode(text)
