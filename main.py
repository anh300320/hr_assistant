import os.path

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
    # indexer.run()

    retriever = Retriever(index_persistent)
    search_entry = SearchEntry(words=["excel"])
    doc_ids = retriever.get(search_entry)
    docs = []
    for doc_id in doc_ids:
        doc = crud.get_doc_by_id(doc_id)
        docs.append(doc)
    uniq = set()
    for d in docs:
        uniq.add(d.path)
    for l in uniq:
        print(l)


if __name__ == "__main__":
    main()
