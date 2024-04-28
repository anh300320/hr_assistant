import io

from pypdf import PdfReader

from src.parsers.base import Parser


class PdfParser(Parser):
    def __init__(self):
        super().__init__()

    def parse(self, data: bytes) -> str:
        reader = PdfReader(io.BytesIO(data))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text
