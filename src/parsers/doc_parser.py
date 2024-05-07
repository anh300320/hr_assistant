from typing import Union

import textract

from src.common.utils import decode
from src.parsers.base import Parser


class DocParser(Parser):

    file_types = ['doc', 'docx']

    def parse(self, data: Union[bytes, str]) -> str:
        text: bytes = textract.process(data)
        return decode(text)
