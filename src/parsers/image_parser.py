import io

from PIL import Image
from pytesseract import pytesseract

from src.common.objects import LoadedFileType, FileType
from src.parsers.base import Parser


class ImageParser(Parser):

    file_types = [FileType.IMAGE]
    supported = LoadedFileType.IN_MEMORY

    def parse(self, data: [bytes, str]) -> str:
        if isinstance(data, bytes):
            file = io.BytesIO(data)
        else:
            file = data
        text = pytesseract.image_to_string(
          Image.open(file),
          lang='eng',
        )
        return text
