from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Set, Dict

from src.common.utils import datetime_str
from src.index.index_persist import IndexPersistent, Pointer
from src.search.objects import SearchEntry


KEYS_DISTANCE = [0, 1, 2]


@dataclass
class Occurrence:
    start: int
    end: int
    match_keys: Set[int] = field(default_factory=set)


class DocumentCandidate:
    def __init__(self):
        self.occurrences: Dict[str, Occurrence] = {}

    def add(self, key_id: int, key: str, pointer: Pointer):
        oc = Occurrence(
            start=pointer.position,
            end=pointer.position + len(key),
            match_keys={key_id}
        )
        oc_id = f"{oc.start}|{oc.end}"
        existed_occurrences = self.occurrences.get(oc_id)
        if not existed_occurrences:
            self.occurrences[oc_id] = oc
        else:
            existed_occurrences.match_keys.add(key_id)


class Retriever:
    def __init__(
            self,
            index_persist: IndexPersistent,
    ):
        self._index_persist = index_persist

    def get(self, search_entry: SearchEntry) -> List[int]:
        """
        :param search_entry:
        :return: list of document_id
        """
        search_entry = self._normalize_search_entry(search_entry)
        doc_candidates = self._build_doc_candidates(search_entry)
        accepted_candidates = []
        for doc_id, candidate in doc_candidates.items():
            occurrences: List[Occurrence] = list(candidate.occurrences.values())
            occurrences.sort(key=lambda o: (o.start, o.end))
            word_tail_link = self.build_word_tail_link(occurrences)
            f = [[False] * len(search_entry.words) for _ in range(len(occurrences))]
            for i, oc in enumerate(occurrences):
                for key in oc.match_keys:
                    if key == 0:
                        f[i][key] = True
                        continue
                    for distance in KEYS_DISTANCE:
                        tail = oc.start - distance
                        if tail not in word_tail_link:
                            continue
                        links = word_tail_link[tail]
                        for link in links:
                            prev = occurrences[link]
                            if (key - 1) in prev.match_keys:
                                f[i][key] = f[link][key - 1] or f[i][key]

                if f[i][len(search_entry.words) - 1]:
                    accepted_candidates.append(doc_id)
                    continue
        return accepted_candidates

    def build_word_tail_link(self, occurrences: List[Occurrence]):
        links = defaultdict(list)
        for i, oc in enumerate(occurrences):
            links[oc.end].append(i)
        return links

    def _build_doc_candidates(
            self,
            search_entry: SearchEntry,
    ) -> Dict[int, DocumentCandidate]:
        doc_candidates = defaultdict(DocumentCandidate)
        for i, key in enumerate(search_entry.words):
            pointers = self._index_persist.retrieve(key)
            pointers = self._clean_up_pointers(pointers)
            for pointer in pointers:
                doc_candidates[pointer.doc_id].add(i, key, pointer)
        return doc_candidates

    def extract_full_match(
            self,
            search_entry: SearchEntry,
    ):
        for i in range(len(search_entry.words)):
            pass

    def _clean_up_pointers(
            self,
            pointers: List[Pointer],
    ) -> List[Pointer]:
        """
        :param pointers:
        :return: List[Pointer]

        remove outdated pointers for each document
        """
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

        doc_to_pointers = defaultdict(list)
        for pointer in pointers:
            doc_to_pointers[pointer.doc_id].append(pointer)
        cleaned_pointers = []
        for pointers in doc_to_pointers.values():
            cleaned_pointers.extend(filter_outdated_pointers(pointers))
        return cleaned_pointers

    def _normalize_search_entry(self, search_entry: SearchEntry):
        normalized = SearchEntry()
        for word in search_entry.words:
            normalized.words.append(word.lower())
        return normalized
