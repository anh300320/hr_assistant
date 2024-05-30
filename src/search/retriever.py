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
        key_idx_to_occurs = {}
        for i, key in enumerate(search_entry.words):
            occurrences = self._index_persist.retrieve(key)
            occurrences = self._clean_up_occurrences(occurrences)
            doc_id_to_ocs = defaultdict(set)
            for oc in occurrences:
                doc_id_to_ocs[oc.doc_id].add(oc.position)
            key_idx_to_occurs[i] = doc_id_to_ocs


    def extract_full_match(
            self,
            search_entry: SearchEntry,
    ):
        for i in range(len(search_entry.words)):
            pass


    def _clean_up_occurrences(
            self,
            occurrences: List[Pointer],
    ) -> List[Pointer]:
        def filter_outdated_pointers(
                pointers: List[Pointer],
        ):
            last_updated_time = None
            for pointer in pointers:
                if pointer.update_time is None:
                    continue  # TODO handle null datetime
                elif last_updated_time is None or datetime_str(last_updated_time) <= datetime_str(pointer.update_time):
                    last_updated_time = pointer.update_time
            keep = []
            for pointer in pointers:
                if pointer.update_time is None:
                    continue
                if datetime_str(pointer.update_time) == datetime_str(last_updated_time):
                    keep.append(pointer)
            return keep

        doc_to_occur = defaultdict(list)
        for oc in occurrences:
            doc_to_occur[oc.doc_id].append(oc)
        cleaned_occurrences = []
        for ocs in doc_to_occur.values():
            cleaned_occurrences.extend(filter_outdated_pointers(ocs))
        return cleaned_occurrences
