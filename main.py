import os.path

import pytesseract
from PIL import Image
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from lsm import LSM

from src.common.disk_sentinel import DiskSentinel
from src.common.logging import init_logging
from src.database.connection import init_database
from src.index.index_persist import IndexPersistent
from src.index.indexer import Indexer
from src.parsers.doc_parser import DocParser
from src.parsers.image_parser import ImageParser
from src.parsers.pdf_parser import PdfParser
from src.tokenizer.base import Tokenizer
from src.tokenizer.semantic import SemanticTokenize
from src.vault.google_drive import GoogleDrive

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main():
    init_logging()
    init_database(f'sqlite:///{os.path.join("temp", "hr_assistant.db")}')
    config = {
        "google_drive_folder": "TEST_CV",
      }
    tokenizers = [
        SemanticTokenize({}),
        Tokenizer()
    ]
    parsers = [
        PdfParser(),
        DocParser(),
    ]
    vault = GoogleDrive(config)
    index_persistent = IndexPersistent(
        {
            'index_fp': os.path.join("temp", "index.lsm")
        }
    )
    disk_sentinel = DiskSentinel(config)
    indexer = Indexer(
        "",
        vault,
        tokenizers,
        parsers,
        index_persistent,
        disk_sentinel
    )
    indexer.run()

    # with LSM(os.path.join("temp", "index.lsm"), binary=False) as db:
    #     x = db['pháp']
    #     print(x)



if __name__ == "__main__":
    main()
