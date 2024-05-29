from collections import defaultdict
from typing import List

from src.common.utils import datetime_str
from src.index.index_persist import IndexPersistent, Pointer
from src.search.objects import SearchEntry


class Retriever:
    def __init__(
            self,
            index_persist: IndexPersistent,
    ):
        self._index_persist = index_persist

    def get(self, search_entry: SearchEntry):
        occurrences = []
        for key in search_entry.words:
            pointers = self._index_persist.retrieve(key)
            occurrences.append(pointers)

    def _filter_outdated_pointers(
            self,
            pointers: List[Pointer],
    ):
        last_updated_time = None
        pointers_with_na_update_time = []
        for pointer in pointers:
            if pointer.update_time is None:
                pointers_with_na_update_time.append(pointer)
            elif last_updated_time is None or datetime_str(last_updated_time) <= datetime_str(pointer.update_time):
                last_updated_time = pointer.update_time
        keep = []
        for pointer in pointers:
            if pointer.update_time is None:
                continue
            if datetime_str(pointer.update_time) == datetime_str(last_updated_time):
                keep.append(pointer)

    def _from_occurrences_to_actual_doc(
            self,
            occurrences: List[List[Pointer]],
    ):
        for i, pointers in enumerate(occurrences):
            doc_to_occur = defaultdict(list)
            for pointer in pointers:
                doc_to_occur[pointer.doc_id].append(pointer)
