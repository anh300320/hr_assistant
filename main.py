import os.path

import jaro
import py4Soundex.code
import soundex
import webview
from py4Soundex.code import Soundex

from src.common.disk_sentinel import DiskSentinel
from src.common.logging import init_logging
from src.database import crud
from src.database.connection import init_database
from src.index.index_persist import IndexPersistent
from src.index.indexer import Indexer
from src.parsers.doc_parser import DocParser
from src.parsers.pdf_parser import PdfParser
from src.search.objects import SearchEntry
from src.search.retriever import Retriever
from src.tokenizer.base import Tokenizer
from src.tokenizer.normalizer import LemmingNormalizer
from src.ui.app import AppUI
from src.ui.context import Context
from src.ui.sidebar.sidebar import Sidebar
from src.vault.google_drive import GoogleDrive

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class Api():
  def log(self, value):
    print(value)



def main():
    init_logging()
    init_database(f'sqlite:///{os.path.join("temp", "hr_assistant.db")}')
    config = {
        "google_drive_folder": "TEST_CV",
      }
    tokenizers = [
        # SemanticTokenize({}),
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
    normalizers = [LemmingNormalizer()]
    disk_sentinel = DiskSentinel(config)
    indexer = Indexer(
        "",
        vault,
        tokenizers,
        normalizers,
        parsers,
        index_persistent,
        disk_sentinel
    )
    folders = vault.search_folder_by_name("test_cv")
    print(folders)

    # retriever = Retriever(index_persistent)
    # search_entry = SearchEntry(words=["Diplomatic", "Academy", "of", "Vietnam"])
    # doc_ids = retriever.get(search_entry)
    # docs = []
    # for doc_id in doc_ids:
    #     doc = crud.get_doc_by_id(doc_id)
    #     docs.append(doc)
    # uniq = set()
    # for d in docs:
    #     uniq.add(d.path)
    # for l in uniq:
    #     print(l)


def test_ui():
    init_logging()
    ui_context = Context()
    app = AppUI(ui_context)
    sidebar = Sidebar(app, context=ui_context)
    ui_context.add_subscriber(subscriber=app)
    app.mainloop()


if __name__ == "__main__":
    test_ui()
