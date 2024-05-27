import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

import pytz
from sqlalchemy.orm import Session

from src.common.disk_sentinel import DiskSentinel
from src.common.objects import Metadata, Index
from src.database import crud
from src.database.connection import get_db
from src.database.models import DocumentInfo
from src.index.index_persist import IndexPersistent
from src.parsers.base import Parser
from src.tokenizer.base import Tokenizer
from src.vault.base import Vault


class Indexer:

    def __init__(
            self,
            last_updated_fp: str,
            vault: Vault,
            tokenizers: list[Tokenizer],
            parsers: list[Parser],
            index_persistent: IndexPersistent,
            disk_sentinel: DiskSentinel,
    ):
        self._last_updated_fp = last_updated_fp     # TODO
        self._vault = vault
        self._tokenizers = tokenizers
        self._threadpool_size = 2
        self._parsers: dict[str, Parser] = {}
        for parser in parsers:
            for t in parser.file_types:
                self._parsers[t] = parser
        self._index_persistent = index_persistent
        self._disk_sentinel = disk_sentinel

    def run(self):
        try:
            all_metadata = self._vault.load_all_metadata()  # TODO batching
            all_metadata = all_metadata[:20]
            new_docs: List[Metadata] = []
            updated_docs: List[Tuple[DocumentInfo, Metadata]] = []
            for metadata in all_metadata:
                saved = crud.get_document(
                    metadata.vault_id,
                    metadata.vault_type,
                )
                if not saved:
                    new_docs.append(metadata)
                elif pytz.UTC.localize(saved.update_date) < metadata.update_date:
                    updated_docs.append((saved, metadata))
            self._build_for_updated_documents(updated_docs)
            self._build_for_new_documents(new_docs)
        finally:
            self._disk_sentinel.clean_up()

    def _build_index(
            self,
            all_metadata: List[Metadata],
    ) -> Index:
        logging.getLogger(__name__).info(
            "Loaded %s metadatas",
            len(all_metadata)
        )
        index = Index()
        finished_cnt = 0
        for metadata, loaded_file in self._load_file_with_multithread(all_metadata):
            print('x')
            with loaded_file as file:
                start_cp = time.perf_counter()
                parser = self._parsers.get(metadata.file_type)
                if not parser:
                    logging.getLogger(__name__).info(
                        "Failed to find appropriate parser for file %s",
                        metadata
                    )
                    continue
                logging.getLogger(__name__).info(
                    "Processing file %s", metadata
                )
                content = parser.parse(file)
                for tokenizer in self._tokenizers:
                    tokens = tokenizer.tokenize(content)
                    index.update(tokens, metadata)
                finish_cp = time.perf_counter()
            finished_cnt += 1
            logging.getLogger(__name__).info(
                "Finished indexing file %s, elapse time %s",
                loaded_file, finish_cp - start_cp
            )
            logging.getLogger(__name__).info(
                "Loaded %s/%s files",
                finished_cnt,
                len(all_metadata)
            )
        return index

    def _build_for_updated_documents(
            self,
            updated_docs: List[Tuple[DocumentInfo, Metadata]],
    ):
        if not updated_docs:
            return
        with get_db() as session:
            crud.batch_update_docs_update_time(session, updated_docs)
            index = self._build_index([m for _, m in updated_docs])
            self._persist_index(index, [d for d, _ in updated_docs])

    def _build_for_new_documents(
            self,
            new_docs: List[Metadata],
    ):
        if not new_docs:
            return
        with get_db() as session:
            inserted_docs = crud.add_document_metadata(session, new_docs)
            index = self._build_index(new_docs)
            self._persist_index(index, inserted_docs)

    def _persist_index(
            self,
            index: Index,
            added_document_infos: list[DocumentInfo],
    ) -> None:
        vault_id_to_doc_info = {d.vault_id: d for d in added_document_infos}
        for key_word, refs in index.index.items():
            for ref in refs:
                doc_info = vault_id_to_doc_info.get(ref.metadata.vault_id)
                if doc_info:
                    ref.document_id = doc_info.id
        self._index_persistent.persist(index)

    def _load_file_with_multithread(
            self, all_metadata: list[Metadata]
    ):
        with ThreadPoolExecutor(self._threadpool_size) as executor:
            tasks = {}
            for metadata in all_metadata:
                task = executor.submit(
                    self._vault.load_content,
                    metadata,
                )
                tasks[task] = metadata
            for completed_task in as_completed(tasks.keys()):
                exception = completed_task.exception()
                metadata = tasks[completed_task]
                if exception:
                    logging.getLogger(__name__).exception(
                        "Failed to load file %s", metadata
                    )
                else:
                    yield metadata, completed_task.result()
