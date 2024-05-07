import os.path

import pytesseract
from PIL import Image
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.common.logging import init_logging
from src.tokenizer.base import SemanticTokenize
from src.parsers.doc_parser import DocParser
from src.parsers.image_parser import ImageParser
from src.parsers.pdf_parser import PdfParser
from src.vault.google_drive import GoogleDrive

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    init_logging()
    gg_drive = GoogleDrive(
      {
        "google_drive_folder": "TEST_CV",
      }
    )
    contents = []
    tokenizer = SemanticTokenize({})
    # files = gg_drive.load_all_metadata()
    # for file in files:
    #     if len(contents) > 50:
    #         break
    #
    #     if file.name.endswith('pdf'):
    #         temp_fp = gg_drive.load_content(file)
    #         content = PdfParser().parse(temp_fp)
    #         # tokens = tokenizer.tokenize(content)
    #         # contents.append(tokens)
    #         contents.append(content)
    # return contents
    content = PdfParser().parse("google_drive_temp/Phạm Phương Chi CS Eng.pdf")
    tokens = tokenizer.tokenize(content)
    return tokens

if __name__ == "__main__":
    main()
