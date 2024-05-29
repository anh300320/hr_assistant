import re
from typing import List

import nltk

from src.search.objects import RawSearch, SearchEntry


class EntryProcessor:
    def __init__(self):
        pass

    def produce_search_entries(
            self,
            search: RawSearch,
    ) -> List[SearchEntry]:
        search = search.lower()
        search = re.sub(r'[^a-zA-Z0-9]', ' ', search)
        words = nltk.wordpunct_tokenize(search)
        search_entries = [SearchEntry(words)]
        search_entries.extend(self.produce_candidates(words))
        return search_entries

    def produce_candidates(
            self,
            words: List[str],
    ) -> List[SearchEntry]:
        result = []
        if len(words) != 1:
            return result
        search = words[0]
        for i in range(len(search)):
            if i == len(search) - 1:
                continue
            words = [search[:i + 1], search[i + 1:]]
            result.append(SearchEntry(words))
        return result
