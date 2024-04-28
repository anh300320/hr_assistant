import os.path

import pytesseract
from PIL import Image
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.common.logging import init_logging
from src.parsers.doc_parser import DocParser
from src.parsers.image_parser import ImageParser
from src.parsers.pdf_parser import PdfParser
from src.vault.google_drive import GoogleDrive

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def main():
    # init_logging()
    # gg_drive = GoogleDrive(
    #   {
    #     "google_drive_folder": "test_cv",
    #   }
    # )
    # files = gg_drive.load_all_metadata()
    # print(files)

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    parser = ImageParser()
    text = parser.parse("resources/test_data/Screenshot 2024-04-27 210934.png")
    print(text)


if __name__ == "__main__":
    main()
