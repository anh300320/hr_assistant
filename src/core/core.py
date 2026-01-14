import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from src.common.objects import VaultType
from src.config.base import Config
from src.database import crud
from src.database.connection import init_database, get_db
from src.database.crud import get_tracked_folders
from src.index.index_persist import IndexPersistent
from src.index.indexer import Indexer
from src.parsers.doc_parser import DocParser
from src.parsers.pdf_parser import PdfParser
from src.search.entry_processor import EntryProcessor
from src.search.retriever import Retriever
from src.search.searcher import BooleanSearcher
from src.tokenizer.base import Tokenizer
from src.tokenizer.normalizer import LemmingNormalizer
from src.tokenizer.semantic import SemanticTokenize
from src.vault.google_drive import GoogleDrive


_logger = logging.getLogger(__name__)


@dataclass
class MatchedEntry:
    query: str
    file_name: str
    path: str
    create_date: datetime
    update_date: datetime


class HrAssistantCore:
    def __init__(
            self,
            config: Config,
    ):
        init_database(f'sqlite:///{os.path.join("temp", "hr_assistant.db")}')
        tokenizers = [
            SemanticTokenize(config),
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
        # disk_sentinel = DiskSentinel(config)
        self._indexer = Indexer(
            vault,
            tokenizers,
            normalizers,
            parsers,
            index_persistent,
            # disk_sentinel
        )
        retriever = Retriever(index_persistent)
        entry_processor = EntryProcessor()
        self._searcher = BooleanSearcher(
            retriever,
            entry_processor,
        )

    def search(self, db_sess: Session, query: str) -> List[MatchedEntry]:
        doc_ids = self._searcher.search(query)
        _logger.info("Matched ids %s", doc_ids)
        matched_entries: List[MatchedEntry] = []
        for doc_id in doc_ids:
            doc = crud.get_doc_by_id(db_sess, doc_id)
            matched_entry = MatchedEntry(
                query=query,
                file_name=doc.name,
                path=doc.path,
                create_date=doc.create_date,
                update_date=doc.update_date,
            )
            matched_entries.append(matched_entry)
        return matched_entries

    def index(self):
        with get_db() as db_sess:
            tracked_folders = get_tracked_folders(db_sess, vault_type=VaultType.GOOGLE_DRIVE)
            self._indexer.run(db_sess, list(tracked_folders))
            _logger.info("Indexed finished.")
