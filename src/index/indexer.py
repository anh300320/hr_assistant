import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Generator, Tuple, List

from src.common.disk_sentinel import DiskSentinel
from src.common.objects import Metadata, LoadedFileType, Index
from src.database import crud
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
            saved = []
            gen = crud.load_all_metadatas(self._vault.vault_type.value)
            for m in gen:
                saved.extend(m)
            all_metadata = self._vault.load_all_metadata()  # TODO batching
            all_metadata = all_metadata[:10]
            added_documents_info = self._persist_metadata(all_metadata)
            index = self._build_index(all_metadata)     # TODO handle when index size is too big
            self._persist_index(index, added_documents_info)
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
        finised_cnt = 0
        for metadata, loaded_file in self._load_file_with_multithread(all_metadata):
            finised_cnt += 1
            logging.getLogger(__name__).info(
                "Loaded %s/%s files",
                finised_cnt,
                len(all_metadata)
            )
            with loaded_file as file:
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
                try:
                    content = parser.parse(file)
                    for tokenizer in self._tokenizers:
                        tokens = tokenizer.tokenize(content)
                        index.update(tokens, metadata)
                except Exception as e:
                    print('x')
        return index

    def _persist_metadata(
            self,
            all_metadata: List[Metadata],
    ) -> list[DocumentInfo]:
        return crud.add_document_metadata(all_metadata)

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
